"""FDA Orange Book parser.

The Orange Book contains three pipe-delimited files (tilde-delimited, actually):
    - products.txt: Approved drug products with therapeutic equivalence
    - patent.txt: Patents covering each product
    - exclusivity.txt: Market exclusivity periods

Public source (check for updates):
    https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files

Download URL pattern (stable for years):
    https://www.fda.gov/media/76860/download  # monthly refresh

This module:
    1. Downloads the Orange Book ZIP
    2. Parses all three files into Polars DataFrames
    3. Filters to cardiometabolic drugs
    4. Joins products + patent + exclusivity → unified drug records
    5. Generates "drug monograph" text suitable for RAG embedding
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

import httpx
import polars as pl

from pharma_intel.common import logger, settings
from pharma_intel.common.constants import (
    CARDIOMETABOLIC_DRUGS,
    classify_therapeutic_area,
)

# Orange Book ZIP download — stable FDA URL
ORANGE_BOOK_URL = "https://www.fda.gov/media/76860/download"

# Expected columns per spec (Orange Book Data Files documentation)
PRODUCTS_COLS = [
    "Ingredient",
    "DF_Route",
    "Trade_Name",
    "Applicant",
    "Strength",
    "Appl_Type",
    "Appl_No",
    "Product_No",
    "TE_Code",
    "Approval_Date",
    "RLD",
    "RS",
    "Type",
    "Applicant_Full_Name",
]

PATENT_COLS = [
    "Appl_Type",
    "Appl_No",
    "Product_No",
    "Patent_No",
    "Patent_Expire_Date_Text",
    "Drug_Substance_Flag",
    "Drug_Product_Flag",
    "Patent_Use_Code",
    "Delist_Flag",
    "Submission_Date",
]

EXCLUSIVITY_COLS = [
    "Appl_Type",
    "Appl_No",
    "Product_No",
    "Exclusivity_Code",
    "Exclusivity_Date",
]


@dataclass
class DrugMonograph:
    """Unified record combining product + patents + exclusivities for RAG.

    One monograph per (Appl_No, Product_No) — i.e., per distinct approved product.
    The `text` field is the natural-language blob that gets embedded.
    """

    appl_no: str
    product_no: str
    ingredient: str
    trade_name: str
    applicant: str
    strength: str
    dosage_form_route: str
    approval_date: str | None
    therapeutic_area: str
    patents: list[dict]
    exclusivities: list[dict]
    text: str  # generated natural-language monograph

    @property
    def doc_id(self) -> str:
        return f"OB-{self.appl_no}-{self.product_no}"


# =========================================================================
# Download
# =========================================================================


def download_orange_book(
    url: str = ORANGE_BOOK_URL,
    dest_dir: Path | None = None,
    force: bool = False,
) -> Path:
    """Download Orange Book ZIP and extract to `dest_dir`.

    Args:
        url: Download URL. Defaults to FDA stable link.
        dest_dir: Extraction directory. Defaults to `settings.raw_dir / "orange_book"`.
        force: Re-download even if files exist.

    Returns:
        Path to the extracted directory containing products.txt, patent.txt, exclusivity.txt.
    """
    if dest_dir is None:
        dest_dir = settings.raw_dir / "orange_book"
    dest_dir.mkdir(parents=True, exist_ok=True)

    marker = dest_dir / "products.txt"
    if marker.exists() and not force:
        logger.info(f"Orange Book already downloaded at {dest_dir}")
        return dest_dir

    logger.info(f"Downloading Orange Book from {url}...")
    with httpx.Client(follow_redirects=True, timeout=120.0) as client:
        response = client.get(url)
        response.raise_for_status()
        logger.info(f"Downloaded {len(response.content) / 1024 / 1024:.1f} MB")

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall(dest_dir)
        logger.info(f"Extracted files: {[n for n in zf.namelist()]}")

    return dest_dir


# =========================================================================
# Parse
# =========================================================================


def _read_pipe_file(path: Path, columns: list[str]) -> pl.DataFrame:
    """Read an Orange Book '~'-delimited file with known columns.

    Files use '~' as delimiter, have a header row. Some rows may have trailing
    '~' so we use strict=False.
    """
    df = pl.read_csv(
        path,
        separator="~",
        has_header=True,
        truncate_ragged_lines=True,
        infer_schema_length=0,  # read everything as string first for safety
        encoding="utf8-lossy",
    )

    # Normalize column names (FDA uses inconsistent casing/spacing)
    df = df.rename({c: c.strip() for c in df.columns})

    # FDA changed this header from DF_Route to DF;Route in current products.txt.
    if "DF;Route" in df.columns and "DF_Route" not in df.columns:
        df = df.rename({"DF;Route": "DF_Route"})

    missing = [c for c in columns if c not in df.columns]
    if missing:
        logger.warning(f"Expected columns missing from {path.name}: {missing}")
        logger.warning(f"Actual columns: {df.columns}")

    return df


def load_products(data_dir: Path) -> pl.DataFrame:
    path = data_dir / "products.txt"
    df = _read_pipe_file(path, PRODUCTS_COLS)
    logger.info(f"Loaded {len(df)} product records from products.txt")
    return df


def load_patents(data_dir: Path) -> pl.DataFrame:
    path = data_dir / "patent.txt"
    df = _read_pipe_file(path, PATENT_COLS)
    logger.info(f"Loaded {len(df)} patent records from patent.txt")
    return df


def load_exclusivity(data_dir: Path) -> pl.DataFrame:
    path = data_dir / "exclusivity.txt"
    df = _read_pipe_file(path, EXCLUSIVITY_COLS)
    logger.info(f"Loaded {len(df)} exclusivity records from exclusivity.txt")
    return df


# =========================================================================
# Filter & build monographs
# =========================================================================


def filter_cardiometabolic(products: pl.DataFrame) -> pl.DataFrame:
    """Keep only products whose Ingredient matches the cardiometabolic drug list."""
    # Normalize ingredient for matching
    products_norm = products.with_columns(
        pl.col("Ingredient").str.to_uppercase().str.strip_chars().alias("_ingredient_norm")
    )

    # Build set match — handle combos by any-component match
    def matches_cardio(ing: str) -> bool:
        if not ing:
            return False
        components = [c.strip() for c in ing.split(";")]
        return any(c in CARDIOMETABOLIC_DRUGS for c in components)

    filtered = products_norm.filter(
        pl.col("_ingredient_norm").map_elements(matches_cardio, return_dtype=pl.Boolean)
    ).drop("_ingredient_norm")

    logger.info(
        f"Filtered to {len(filtered)} cardiometabolic products "
        f"({len(filtered) / len(products) * 100:.1f}% of total)"
    )
    return filtered


def build_monographs(
    products: pl.DataFrame,
    patents: pl.DataFrame,
    exclusivity: pl.DataFrame,
) -> list[DrugMonograph]:
    """Join products + patents + exclusivity and produce a list of DrugMonograph.

    Each monograph corresponds to one unique (Appl_No, Product_No) combo and
    aggregates all its patents + exclusivities.
    """
    monographs: list[DrugMonograph] = []

    def clean(value: str | None) -> str:
        return (value or "").strip()

    for row in products.iter_rows(named=True):
        appl_no = clean(row.get("Appl_No"))
        product_no = clean(row.get("Product_No"))
        ingredient = clean(row.get("Ingredient"))

        if not appl_no or not product_no:
            continue

        # Gather patents for this product
        product_patents = patents.filter(
            (pl.col("Appl_No") == appl_no) & (pl.col("Product_No") == product_no)
        )
        patents_list = [
            {
                "patent_no": r.get("Patent_No", ""),
                "expire_date": r.get("Patent_Expire_Date_Text", ""),
                "drug_substance": r.get("Drug_Substance_Flag", "") == "Y",
                "drug_product": r.get("Drug_Product_Flag", "") == "Y",
                "use_code": r.get("Patent_Use_Code", ""),
            }
            for r in product_patents.iter_rows(named=True)
        ]

        # Gather exclusivities
        product_excl = exclusivity.filter(
            (pl.col("Appl_No") == appl_no) & (pl.col("Product_No") == product_no)
        )
        excl_list = [
            {
                "code": r.get("Exclusivity_Code", ""),
                "expire_date": r.get("Exclusivity_Date", ""),
            }
            for r in product_excl.iter_rows(named=True)
        ]

        therapeutic_area = classify_therapeutic_area(ingredient) or "other"

        monograph = DrugMonograph(
            appl_no=appl_no,
            product_no=product_no,
            ingredient=ingredient,
            trade_name=clean(row.get("Trade_Name")),
            applicant=clean(row.get("Applicant")),
            strength=clean(row.get("Strength")),
            dosage_form_route=clean(row.get("DF_Route")),
            approval_date=clean(row.get("Approval_Date")) or None,
            therapeutic_area=therapeutic_area,
            patents=patents_list,
            exclusivities=excl_list,
            text=_generate_monograph_text(row, patents_list, excl_list, therapeutic_area),
        )
        monographs.append(monograph)

    logger.info(f"Built {len(monographs)} drug monographs")
    return monographs


def _generate_monograph_text(
    product_row: dict,
    patents: list[dict],
    exclusivities: list[dict],
    therapeutic_area: str,
) -> str:
    """Generate a natural-language drug monograph for RAG embedding.

    The text is structured to be searchable by different query styles:
        - "patents for empagliflozin" → patent section hit
        - "when did FDA approve dapagliflozin" → approval date hit
        - "generic metformin manufacturers" → applicant section hit
    """
    lines: list[str] = []

    def clean(value: str | None) -> str:
        return (value or "").strip()

    ingredient = clean(product_row.get("Ingredient"))
    trade_name = clean(product_row.get("Trade_Name"))
    strength = clean(product_row.get("Strength"))
    df_route = clean(product_row.get("DF_Route"))
    applicant = clean(product_row.get("Applicant_Full_Name")) or clean(product_row.get("Applicant"))
    approval_date = clean(product_row.get("Approval_Date"))
    te_code = clean(product_row.get("TE_Code"))
    rld = clean(product_row.get("RLD"))
    appl_type = clean(product_row.get("Appl_Type"))

    # Header
    lines.append(f"Drug Product: {trade_name or ingredient} ({ingredient})")
    lines.append(f"Therapeutic Area: {therapeutic_area}")
    lines.append("")

    # Basic facts
    lines.append("## Product Information")
    lines.append(f"- Active Ingredient: {ingredient}")
    if trade_name:
        lines.append(f"- Brand Name: {trade_name}")
    if strength:
        lines.append(f"- Strength: {strength}")
    if df_route:
        lines.append(f"- Dosage Form / Route: {df_route}")
    if applicant:
        lines.append(f"- Applicant / Manufacturer: {applicant}")
    if approval_date:
        lines.append(f"- FDA Approval Date: {approval_date}")
    if appl_type:
        lines.append(
            f"- Application Type: {appl_type} "
            f"({'New Drug Application' if appl_type == 'N' else 'Abbreviated (Generic)'})"
        )
    if rld == "Yes":
        lines.append("- Reference Listed Drug: Yes (originator/reference product)")
    if te_code:
        lines.append(f"- Therapeutic Equivalence Code: {te_code}")
    lines.append("")

    # Patents
    if patents:
        lines.append("## Patents")
        for p in patents:
            patent_line = f"- Patent {p['patent_no']}"
            if p["expire_date"]:
                patent_line += f", expires {p['expire_date']}"
            flags = []
            if p["drug_substance"]:
                flags.append("drug substance")
            if p["drug_product"]:
                flags.append("drug product")
            if flags:
                patent_line += f" (covers: {', '.join(flags)})"
            if p["use_code"]:
                patent_line += f" [use code {p['use_code']}]"
            lines.append(patent_line)
        lines.append("")

    # Exclusivity
    if exclusivities:
        lines.append("## Market Exclusivity")
        for e in exclusivities:
            excl_line = f"- Exclusivity code {e['code']}"
            if e["expire_date"]:
                excl_line += f", expires {e['expire_date']}"
            lines.append(excl_line)
        lines.append("")

    return "\n".join(lines)


# =========================================================================
# High-level pipeline
# =========================================================================


def run_pipeline(force_download: bool = False) -> list[DrugMonograph]:
    """End-to-end: download → parse → filter → build monographs.

    Returns list of DrugMonograph ready for embedding.
    """
    settings.ensure_dirs()

    # 1. Download
    data_dir = download_orange_book(force=force_download)

    # 2. Parse
    products = load_products(data_dir)
    patents = load_patents(data_dir)
    exclusivity = load_exclusivity(data_dir)

    # 3. Filter to cardiometabolic
    cardio_products = filter_cardiometabolic(products)

    # 4. Build monographs
    monographs = build_monographs(cardio_products, patents, exclusivity)

    # 5. Save processed output as Parquet
    save_monographs_parquet(monographs)

    return monographs


def save_monographs_parquet(monographs: list[DrugMonograph]) -> Path:
    """Persist monographs to Parquet for downstream use."""
    rows = [
        {
            "doc_id": m.doc_id,
            "appl_no": m.appl_no,
            "product_no": m.product_no,
            "ingredient": m.ingredient,
            "trade_name": m.trade_name,
            "applicant": m.applicant,
            "strength": m.strength,
            "dosage_form_route": m.dosage_form_route,
            "approval_date": m.approval_date,
            "therapeutic_area": m.therapeutic_area,
            "num_patents": len(m.patents),
            "num_exclusivities": len(m.exclusivities),
            "text": m.text,
        }
        for m in monographs
    ]
    df = pl.DataFrame(rows)
    out_path = settings.processed_dir / "orange_book_cardiometabolic.parquet"
    df.write_parquet(out_path)
    logger.info(f"Saved {len(df)} monographs to {out_path}")
    return out_path
