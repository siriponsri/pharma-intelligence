"""Molecule-class taxonomy for cardiometabolic drugs.

Forecasting unit is molecule-class, not individual SKU. Each class groups
drugs that are clinically substitutable (e.g., all SGLT2i compete for the
same prescribing decision).

Also carries key metadata needed for mock data generation:
    - first_launch_th: year the class entered Thai market (affects base demand curve)
    - key_patent_expiries: patent cliff events that trigger demand shifts
    - growth_driver: which disease prevalence drives this class
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MoleculeClass:
    """A class of therapeutically similar drugs."""

    class_id: str  # stable identifier, e.g. "sglt2i"
    display_name: str  # e.g. "SGLT2 Inhibitors"
    therapeutic_area: str  # diabetes | hypertension | dyslipidemia
    members: tuple[str, ...]  # INN names (uppercase to match Orange Book)
    first_launch_th_year: int  # approximate year entered Thai market
    key_patent_expiries: dict[str, int] = field(default_factory=dict)  # molecule -> year
    growth_driver: str = "general"  # which prevalence signal drives demand


# ======================================================================
# Diabetes classes
# ======================================================================

METFORMIN = MoleculeClass(
    class_id="metformin",
    display_name="Metformin (Biguanides)",
    therapeutic_area="diabetes",
    members=("METFORMIN HYDROCHLORIDE", "METFORMIN"),
    first_launch_th_year=1995,  # long off-patent
    growth_driver="diabetes_prevalence",
)

SULFONYLUREAS = MoleculeClass(
    class_id="sulfonylureas",
    display_name="Sulfonylureas",
    therapeutic_area="diabetes",
    members=("GLIPIZIDE", "GLYBURIDE", "GLIMEPIRIDE", "GLICLAZIDE"),
    first_launch_th_year=1990,
    growth_driver="diabetes_prevalence",
)

DPP4_INHIBITORS = MoleculeClass(
    class_id="dpp4i",
    display_name="DPP-4 Inhibitors",
    therapeutic_area="diabetes",
    members=(
        "SITAGLIPTIN PHOSPHATE",
        "SITAGLIPTIN",
        "LINAGLIPTIN",
        "SAXAGLIPTIN HYDROCHLORIDE",
        "SAXAGLIPTIN",
        "VILDAGLIPTIN",
        "ALOGLIPTIN BENZOATE",
    ),
    first_launch_th_year=2008,
    key_patent_expiries={
        "SITAGLIPTIN": 2026,  # approximate
        "LINAGLIPTIN": 2028,
    },
    growth_driver="diabetes_prevalence",
)

SGLT2_INHIBITORS = MoleculeClass(
    class_id="sglt2i",
    display_name="SGLT2 Inhibitors",
    therapeutic_area="diabetes",
    members=(
        "EMPAGLIFLOZIN",
        "DAPAGLIFLOZIN PROPANEDIOL",
        "DAPAGLIFLOZIN",
        "CANAGLIFLOZIN",
        "ERTUGLIFLOZIN",
    ),
    first_launch_th_year=2014,
    key_patent_expiries={
        "EMPAGLIFLOZIN": 2025,
        "DAPAGLIFLOZIN": 2025,
    },
    growth_driver="diabetes_prevalence",
)

GLP1_AGONISTS = MoleculeClass(
    class_id="glp1",
    display_name="GLP-1 Receptor Agonists",
    therapeutic_area="diabetes",
    members=("LIRAGLUTIDE", "SEMAGLUTIDE", "DULAGLUTIDE", "EXENATIDE", "TIRZEPATIDE"),
    first_launch_th_year=2011,
    key_patent_expiries={
        "LIRAGLUTIDE": 2024,
    },
    growth_driver="diabetes_obesity_prevalence",  # GLP-1 boom from obesity
)

# ======================================================================
# Hypertension classes
# ======================================================================

ACE_INHIBITORS = MoleculeClass(
    class_id="acei",
    display_name="ACE Inhibitors",
    therapeutic_area="hypertension",
    members=(
        "ENALAPRIL MALEATE",
        "ENALAPRIL",
        "LISINOPRIL",
        "RAMIPRIL",
        "PERINDOPRIL ERBUMINE",
        "PERINDOPRIL",
        "CAPTOPRIL",
    ),
    first_launch_th_year=1988,
    growth_driver="hypertension_prevalence",
)

ARBS = MoleculeClass(
    class_id="arbs",
    display_name="Angiotensin Receptor Blockers (ARBs)",
    therapeutic_area="hypertension",
    members=(
        "LOSARTAN POTASSIUM",
        "LOSARTAN",
        "VALSARTAN",
        "OLMESARTAN MEDOXOMIL",
        "TELMISARTAN",
        "IRBESARTAN",
        "CANDESARTAN CILEXETIL",
    ),
    first_launch_th_year=1998,
    growth_driver="hypertension_prevalence",
)

CCB = MoleculeClass(
    class_id="ccb",
    display_name="Calcium Channel Blockers",
    therapeutic_area="hypertension",
    members=(
        "AMLODIPINE BESYLATE",
        "AMLODIPINE",
        "FELODIPINE",
        "NIFEDIPINE",
        "DILTIAZEM HYDROCHLORIDE",
        "VERAPAMIL HYDROCHLORIDE",
    ),
    first_launch_th_year=1992,
    growth_driver="hypertension_prevalence",
)

BETA_BLOCKERS = MoleculeClass(
    class_id="beta_blockers",
    display_name="Beta Blockers",
    therapeutic_area="hypertension",
    members=(
        "ATENOLOL",
        "METOPROLOL SUCCINATE",
        "METOPROLOL TARTRATE",
        "BISOPROLOL FUMARATE",
        "CARVEDILOL",
        "PROPRANOLOL HYDROCHLORIDE",
        "NEBIVOLOL HYDROCHLORIDE",
    ),
    first_launch_th_year=1985,
    growth_driver="hypertension_prevalence",
)

DIURETICS = MoleculeClass(
    class_id="diuretics",
    display_name="Diuretics",
    therapeutic_area="hypertension",
    members=(
        "HYDROCHLOROTHIAZIDE",
        "CHLORTHALIDONE",
        "INDAPAMIDE",
        "FUROSEMIDE",
        "SPIRONOLACTONE",
    ),
    first_launch_th_year=1980,
    growth_driver="hypertension_prevalence",
)

# ======================================================================
# Dyslipidemia classes
# ======================================================================

STATINS = MoleculeClass(
    class_id="statins",
    display_name="Statins (HMG-CoA Reductase Inhibitors)",
    therapeutic_area="dyslipidemia",
    members=(
        "SIMVASTATIN",
        "ATORVASTATIN CALCIUM",
        "ATORVASTATIN",
        "ROSUVASTATIN CALCIUM",
        "ROSUVASTATIN",
        "PRAVASTATIN SODIUM",
        "PITAVASTATIN CALCIUM",
        "LOVASTATIN",
    ),
    first_launch_th_year=1995,
    growth_driver="dyslipidemia_prevalence",
)

EZETIMIBE = MoleculeClass(
    class_id="ezetimibe",
    display_name="Cholesterol Absorption Inhibitors",
    therapeutic_area="dyslipidemia",
    members=("EZETIMIBE",),
    first_launch_th_year=2004,
    growth_driver="dyslipidemia_prevalence",
)

FIBRATES = MoleculeClass(
    class_id="fibrates",
    display_name="Fibrates",
    therapeutic_area="dyslipidemia",
    members=("FENOFIBRATE", "GEMFIBROZIL"),
    first_launch_th_year=1990,
    growth_driver="dyslipidemia_prevalence",
)

# ======================================================================
# Registry
# ======================================================================

ALL_CLASSES: tuple[MoleculeClass, ...] = (
    METFORMIN,
    SULFONYLUREAS,
    DPP4_INHIBITORS,
    SGLT2_INHIBITORS,
    GLP1_AGONISTS,
    ACE_INHIBITORS,
    ARBS,
    CCB,
    BETA_BLOCKERS,
    DIURETICS,
    STATINS,
    EZETIMIBE,
    FIBRATES,
)

CLASSES_BY_ID: dict[str, MoleculeClass] = {c.class_id: c for c in ALL_CLASSES}


def get_class(class_id: str) -> MoleculeClass:
    """Return a molecule class by ID, raising KeyError if not found."""
    if class_id not in CLASSES_BY_ID:
        raise KeyError(
            f"Unknown molecule class '{class_id}'. Available: {list(CLASSES_BY_ID)}"
        )
    return CLASSES_BY_ID[class_id]


def classes_for_area(therapeutic_area: str) -> list[MoleculeClass]:
    """Return all molecule classes for a given therapeutic area."""
    return [c for c in ALL_CLASSES if c.therapeutic_area == therapeutic_area]
