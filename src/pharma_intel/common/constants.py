"""Domain constants for cardiometabolic therapeutic area filtering.

All INN (International Nonproprietary Names) are stored UPPERCASE to match
FDA Orange Book convention.
"""

# ============ Diabetes Mellitus ============
DIABETES_DRUGS = {
    # Biguanides
    "METFORMIN HYDROCHLORIDE",
    "METFORMIN",
    # Sulfonylureas
    "GLIPIZIDE",
    "GLYBURIDE",
    "GLIMEPIRIDE",
    "GLICLAZIDE",
    # DPP-4 inhibitors
    "SITAGLIPTIN PHOSPHATE",
    "SITAGLIPTIN",
    "LINAGLIPTIN",
    "SAXAGLIPTIN HYDROCHLORIDE",
    "SAXAGLIPTIN",
    "VILDAGLIPTIN",
    "ALOGLIPTIN BENZOATE",
    # SGLT2 inhibitors
    "EMPAGLIFLOZIN",
    "DAPAGLIFLOZIN PROPANEDIOL",
    "DAPAGLIFLOZIN",
    "CANAGLIFLOZIN",
    "ERTUGLIFLOZIN",
    # GLP-1 receptor agonists
    "LIRAGLUTIDE",
    "SEMAGLUTIDE",
    "DULAGLUTIDE",
    "EXENATIDE",
    "TIRZEPATIDE",
    # TZDs
    "PIOGLITAZONE HYDROCHLORIDE",
    "PIOGLITAZONE",
    "ROSIGLITAZONE MALEATE",
    # Meglitinides
    "REPAGLINIDE",
    "NATEGLINIDE",
    # Alpha-glucosidase inhibitors
    "ACARBOSE",
    "MIGLITOL",
}

# ============ Hypertension ============
HYPERTENSION_DRUGS = {
    # ACE inhibitors
    "ENALAPRIL MALEATE",
    "ENALAPRIL",
    "LISINOPRIL",
    "RAMIPRIL",
    "PERINDOPRIL ERBUMINE",
    "PERINDOPRIL",
    "CAPTOPRIL",
    "BENAZEPRIL HYDROCHLORIDE",
    "QUINAPRIL HYDROCHLORIDE",
    # ARBs
    "LOSARTAN POTASSIUM",
    "LOSARTAN",
    "VALSARTAN",
    "OLMESARTAN MEDOXOMIL",
    "TELMISARTAN",
    "IRBESARTAN",
    "CANDESARTAN CILEXETIL",
    "AZILSARTAN MEDOXOMIL",
    # Calcium channel blockers
    "AMLODIPINE BESYLATE",
    "AMLODIPINE",
    "FELODIPINE",
    "NIFEDIPINE",
    "DILTIAZEM HYDROCHLORIDE",
    "VERAPAMIL HYDROCHLORIDE",
    # Beta blockers
    "ATENOLOL",
    "METOPROLOL SUCCINATE",
    "METOPROLOL TARTRATE",
    "BISOPROLOL FUMARATE",
    "CARVEDILOL",
    "PROPRANOLOL HYDROCHLORIDE",
    "NEBIVOLOL HYDROCHLORIDE",
    # Diuretics
    "HYDROCHLOROTHIAZIDE",
    "CHLORTHALIDONE",
    "INDAPAMIDE",
    "FUROSEMIDE",
    "SPIRONOLACTONE",
    "EPLERENONE",
    "TORSEMIDE",
}

# ============ Dyslipidemia ============
DYSLIPIDEMIA_DRUGS = {
    # Statins
    "SIMVASTATIN",
    "ATORVASTATIN CALCIUM",
    "ATORVASTATIN",
    "ROSUVASTATIN CALCIUM",
    "ROSUVASTATIN",
    "PRAVASTATIN SODIUM",
    "PITAVASTATIN CALCIUM",
    "LOVASTATIN",
    "FLUVASTATIN SODIUM",
    # Cholesterol absorption inhibitors
    "EZETIMIBE",
    # Fibrates
    "FENOFIBRATE",
    "GEMFIBROZIL",
    # Niacin
    "NIACIN",
    # PCSK9 inhibitors (biologics — typically not generic targets but included for completeness)
    "EVOLOCUMAB",
    "ALIROCUMAB",
    # Bile acid sequestrants
    "CHOLESTYRAMINE",
    "COLESEVELAM HYDROCHLORIDE",
}

# ============ Combined set ============
CARDIOMETABOLIC_DRUGS = DIABETES_DRUGS | HYPERTENSION_DRUGS | DYSLIPIDEMIA_DRUGS


def classify_therapeutic_area(ingredient: str) -> str | None:
    """Return therapeutic area for a given ingredient, or None if not cardiometabolic.

    Handles multi-ingredient products by checking if ANY component matches.
    """
    ingredient_upper = ingredient.upper().strip()

    # Handle combo products (semicolon-separated in Orange Book)
    components = [c.strip() for c in ingredient_upper.split(";")]

    areas = set()
    for comp in components:
        if comp in DIABETES_DRUGS:
            areas.add("diabetes")
        if comp in HYPERTENSION_DRUGS:
            areas.add("hypertension")
        if comp in DYSLIPIDEMIA_DRUGS:
            areas.add("dyslipidemia")

    if not areas:
        return None
    if len(areas) == 1:
        return areas.pop()
    return "combination"  # multi-area combo product
