RESULT_DIM_DICT = {
    "Monat": None,
    "Year To Date": None,
    "3 Monate rollierend": 3,
    "6 Monate rollierend": 6,
    "12 Monate rollierend": 12,
}

COLORS_BCAG = {
    "rot_matt": "#D2535F",  # non-bcag
    "orange_hell": "#FFC000",
    "braun_mittel": "#997332",  # non-bcag
    "grau_hell": "#BCBCBB",
    "orange_dunkel": "#D26817",
    "braun_dunkel": "#7E3E00",
    "grau_dunkel": "#565655",
    "braun_hell": "#D6BDA3",
}

# These KPI values are not aggregated for display in multi-month periods
NO_SUM_KPI = [
    "Anzahl aktive Konten Total",
    "Anzahl gültige Konten Total",
]

# Denoting the value for filtering with str.startswith()
KPI_GROUPS = {
    "[alle] ohne NCA": "NCA",
    "[alle]": None,
    "Umsatz": "Umsatz",
    "Anzahl Trx": "Nr. TRX",
    "Anzahl Konten": "Anzahl",
    "NCA": "NCA",
}


# Some values that are expected outcomes for the preprocessed data file
# They are used for validation of the data and to control the log messages
# These values can change over time and should be updated accordingly
PREPROCESS_VALIDATION = {
    "mandant": [
        "BCAG",
        "B2B2C",
        "B2C",
        "Bonus Card",
        "Edelweiss",
        "FACES",
        "Glückskette",
        "HSG Alumni",
        "Jelmoli",
        "Liberty",
        "Ochsner",
        "Pink Ribbon",
        "SBB",
        "Simply",
        "TUI",
        "UZH Alumni",
    ],
    "cols": [
        "calculation_date",
        "kpi_name",
        "period_id",
        "product_name",
        "cardprofile",
        "mandant",
        "sector",
        "level",
        "value",
        "value_avg"
    ],
    "cardprofile": ["all", "CC", "PP", "CCL"],
    "level": [0, 1, 2, 3],
    "period_id": [1, 2],
    "n_period": 37,
}

# This dictionary is used during preprocessing to determine mandant / sector / profile
# It has to be updated here in case new products are loaded
# Defunct products have to stay in the dict for as long as they are loaded
PRODUCT_LOOK_UP = {
    "ALUMNI VBC": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Advanced Card BCAG": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Bonuscard": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Bonuscard Classic": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Bonuscard Exclusive": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Bonuscard Gold": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Bonuscard Prepaid": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Bonuscard Classic Charge": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Bonuscard Exclusive Charge": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA Bonuscard Gold Charge": {"mandant": "Bonus Card", "sector": "B2C"},
    "VISA LibertyCard Credit": {"mandant": "Liberty", "sector": "B2C"},
    "VISA LibertyCard Plus Credit": {"mandant": "Liberty", "sector": "B2C"},
    "VISA LibertyCard Prepaid": {"mandant": "Liberty", "sector": "B2C"},
    "VISA LibertyCard Plus Charge": {"mandant": "Liberty", "sector": "B2C"},
    "VISA LibertyCard Charge": {"mandant": "Liberty", "sector": "B2C"},
    "Simply VISA Card Credit": {"mandant": "Simply", "sector": "B2C"},
    "Simply VISA Card Prepaid": {"mandant": "Simply", "sector": "B2C"},
    "Simply VISA Card Charge": {"mandant": "Simply", "sector": "B2C"},
    "Edelweiss Business Card": {"mandant": "Edelweiss", "sector": "B2B2C"},
    "Edelweiss Credit Card": {"mandant": "Edelweiss", "sector": "B2B2C"},
    "Edelweiss Prepaid Card": {"mandant": "Edelweiss", "sector": "B2B2C"},
    "SWISS Crew Credit Card": {"mandant": "Edelweiss", "sector": "B2B2C"},
    "SWISS Crew Prepaid Card": {"mandant": "Edelweiss", "sector": "B2B2C"},
    "FACES Visa Bonus Card": {"mandant": "FACES", "sector": "B2B2C"},
    "FACES Visa Bonus Card Prepaid": {"mandant": "FACES", "sector": "B2B2C"},
    "Glückskette Visa Card": {"mandant": "Glückskette", "sector": "B2B2C"},
    "Glückskette Visa Card Prepaid": {"mandant": "Glückskette", "sector": "B2B2C"},
    "HSG Alumni VBC Classic": {"mandant": "HSG Alumni", "sector": "B2B2C"},
    "HSG Alumni VBC Exclusive": {"mandant": "HSG Alumni", "sector": "B2B2C"},
    "JVBC Premium Classic": {"mandant": "Jelmoli", "sector": "B2B2C"},
    "JVBC Premium Gold": {"mandant": "Jelmoli", "sector": "B2B2C"},
    "JVBC Royal Classic": {"mandant": "Jelmoli", "sector": "B2B2C"},
    "JVBC Royal Gold": {"mandant": "Jelmoli", "sector": "B2B2C"},
    "Ochsner Sport Club VBC Classic": {"mandant": "Ochsner", "sector": "B2B2C"},
    "Ochsner Sport Club VBC Gold": {"mandant": "Ochsner", "sector": "B2B2C"},
    "PINK RIBBON VBC KK": {"mandant": "Pink Ribbon", "sector": "B2B2C"},
    "PINK RIBBON VBC PP": {"mandant": "Pink Ribbon", "sector": "B2B2C"},
    "SBB Businesscard Classic": {"mandant": "SBB", "sector": "B2B2C"},
    "SBB Businesscard Gold": {"mandant": "SBB", "sector": "B2B2C"},
    "SBB Kredit mit Abo": {"mandant": "SBB", "sector": "B2B2C"},
    "SBB Kredit ohne Abo": {"mandant": "SBB", "sector": "B2B2C"},
    "SBB Prepaid mit Abo": {"mandant": "SBB", "sector": "B2B2C"},
    "SBB Prepaid ohne Abo": {"mandant": "SBB", "sector": "B2B2C"},
    "TUI VISA Card Classic": {"mandant": "TUI", "sector": "B2B2C"},
    "TUI VISA Card Exclusive": {"mandant": "TUI", "sector": "B2B2C"},
    "TUI VISA Card Gold": {"mandant": "TUI", "sector": "B2B2C"},
    "TUI VISA Card Prepaid": {"mandant": "TUI", "sector": "B2B2C"},
    "UZH Alumni VBC Classic": {"mandant": "UZH Alumni", "sector": "B2B2C"},
    "UZH Alumni VBC Exclusive": {"mandant": "UZH Alumni", "sector": "B2B2C"},
    "UZH Alumni VBC Classic Charge": {"mandant": "UZH Alumni", "sector": "B2B2C"},
}
