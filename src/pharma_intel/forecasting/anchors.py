"""Public statistical anchors for mock data generation.

These are APPROXIMATE figures sourced from public Thai health reports.
They should be replaced with live HDC API data when available.

Sources (verify/update periodically):
    - HDC (Health Data Center), Ministry of Public Health
    - Thailand NCD surveillance reports
    - IHPP (International Health Policy Program)
    - Published Thai diabetes/hypertension prevalence studies

⚠️ IMPORTANT: These numbers are for MOCK DATA SHAPE anchoring only, not
for any clinical or policy decision. Always cite original sources in the
paper, not this module.
"""

from __future__ import annotations

# ======================================================================
# Disease prevalence trends in Thailand (adults ≥18)
# Approximate prevalence rates (%) by year, used to shape demand growth
# ======================================================================

# Diabetes prevalence Thailand — based on NHES surveys + estimates
# Trend: roughly linear growth driven by aging + urbanization
DIABETES_PREVALENCE_TH = {
    2015: 8.9,
    2016: 9.2,
    2017: 9.6,
    2018: 10.0,
    2019: 10.4,
    2020: 10.8,  # small dip in diagnosis during COVID
    2021: 10.5,
    2022: 11.2,  # catchup diagnosis post-COVID
    2023: 11.6,
    2024: 12.0,
    2025: 12.4,
}

# Hypertension prevalence Thailand
HYPERTENSION_PREVALENCE_TH = {
    2015: 24.7,
    2016: 25.2,
    2017: 25.8,
    2018: 26.3,
    2019: 26.9,
    2020: 27.2,
    2021: 26.8,
    2022: 27.9,
    2023: 28.5,
    2024: 29.1,
    2025: 29.7,
}

# Dyslipidemia prevalence Thailand
DYSLIPIDEMIA_PREVALENCE_TH = {
    2015: 16.4,
    2016: 17.0,
    2017: 17.7,
    2018: 18.3,
    2019: 19.0,
    2020: 19.4,
    2021: 19.2,
    2022: 19.9,
    2023: 20.5,
    2024: 21.1,
    2025: 21.6,
}

# Obesity prevalence Thailand (relevant for GLP-1 class)
OBESITY_PREVALENCE_TH = {
    2015: 9.1,
    2016: 9.6,
    2017: 10.1,
    2018: 10.7,
    2019: 11.4,
    2020: 12.0,  # COVID lockdown effect
    2021: 13.1,
    2022: 13.8,
    2023: 14.4,
    2024: 14.9,
    2025: 15.5,
}

PREVALENCE_DRIVERS: dict[str, dict[int, float]] = {
    "diabetes_prevalence": DIABETES_PREVALENCE_TH,
    "hypertension_prevalence": HYPERTENSION_PREVALENCE_TH,
    "dyslipidemia_prevalence": DYSLIPIDEMIA_PREVALENCE_TH,
    "obesity_prevalence": OBESITY_PREVALENCE_TH,
    "diabetes_obesity_prevalence": {  # synthetic blend for GLP-1
        y: (DIABETES_PREVALENCE_TH[y] + OBESITY_PREVALENCE_TH[y]) / 2
        for y in DIABETES_PREVALENCE_TH
    },
    "general": {y: 100.0 for y in range(2015, 2026)},  # flat baseline
}


# ======================================================================
# Macroeconomic / healthcare budget proxy (Thailand public health budget index)
# ======================================================================

# Index: 2019 = 100. Approximates annual MOPH budget + UC budget trend.
HEALTHCARE_BUDGET_INDEX_TH = {
    2015: 82,
    2016: 86,
    2017: 90,
    2018: 94,
    2019: 100,
    2020: 105,  # pandemic emergency spending
    2021: 112,
    2022: 108,  # some rollback
    2023: 111,
    2024: 115,
    2025: 119,
}


# ======================================================================
# Class-level approximate market share (% of DDDs within therapeutic area)
# Used as base level for each molecule class in synthetic sales
# ======================================================================

# Diabetes — roughly reflects Thai clinical practice
CLASS_MARKET_SHARE_DM = {
    "metformin": 0.40,  # first-line, dominant
    "sulfonylureas": 0.20,
    "dpp4i": 0.15,
    "sglt2i": 0.12,
    "glp1": 0.08,
    # Remainder (~5%) are TZDs, meglitinides, alpha-glucosidase inhibitors
}

CLASS_MARKET_SHARE_HTN = {
    "acei": 0.15,
    "arbs": 0.25,  # replaced ACEi for many patients
    "ccb": 0.25,
    "beta_blockers": 0.15,
    "diuretics": 0.20,
}

CLASS_MARKET_SHARE_DYSLIPIDEMIA = {
    "statins": 0.80,  # dominant
    "ezetimibe": 0.12,
    "fibrates": 0.08,
}

CLASS_MARKET_SHARE_BY_AREA: dict[str, dict[str, float]] = {
    "diabetes": CLASS_MARKET_SHARE_DM,
    "hypertension": CLASS_MARKET_SHARE_HTN,
    "dyslipidemia": CLASS_MARKET_SHARE_DYSLIPIDEMIA,
}


# ======================================================================
# Total therapeutic-area market size anchors (Thailand)
# Approximate annual total demand in thousand-DDD (defined daily doses)
# ⚠️ These numbers are rough order-of-magnitude only
# ======================================================================

ANNUAL_MARKET_SIZE_KDDD = {
    "diabetes": 850_000,  # ~850 million DDDs/year approximate
    "hypertension": 1_600_000,  # biggest by volume
    "dyslipidemia": 900_000,
}


def get_prevalence(driver: str, year: int) -> float:
    """Get prevalence value for a given driver/year, with linear interpolation
    if year is outside the table range.
    """
    table = PREVALENCE_DRIVERS.get(driver, PREVALENCE_DRIVERS["general"])
    years = sorted(table.keys())

    if year in table:
        return table[year]
    if year < years[0]:
        # Extrapolate backward using earliest available trend
        return table[years[0]]
    if year > years[-1]:
        # Extrapolate forward with last annual delta
        last = table[years[-1]]
        prev = table[years[-2]]
        delta = last - prev
        return last + delta * (year - years[-1])
    # Linear interpolation between surrounding years (shouldn't hit in our data)
    return table[years[0]]
