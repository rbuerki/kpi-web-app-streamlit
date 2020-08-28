# Web-Application "KPI Sheet"

July 2020, Version 0.1

## Introduction

An interactive web app to display relevant KPI data for business stakeholders in Marketing, Product Management, and Senior Management in general.
Witin the company network the app can be accessed by the Chrome webbrowser through the exposed network address.

The app has offers high flexibility on how to display the data:

- convenient filtering: by selected KPI, KPI groups, and / or selected entitites, entity groups
- different aggregations: data can be viewed per month, or, for all KPI permitting aggregation, per 3-month, 6-month, 12-month or year-to-date aggregations
- 2 display modes: tabulare data can be displayed as to group all selected KPI per entity or as to compare all selected entities per KPI

When a single KPI and no more than 8 separate entities are chosen, an interactive plot is automatically displayed.

Plots (as png) and data (as xlsx) can be saved into to the user's default `downloads` folder at any time.

## Build

The application is built with Python 3.8 and [streamlit](https://www.streamlit.io/). Use the included `kpi_app.yml` file to set up the necessary dependencies (with conda).

## Run

The app can be run from the main folder (containing this README file) by typing the following command in the CLI. It will then expose a local address and a network address. The latter is used for sharing access to the app.

```python
streamlit run src/app.py
```

## Data preparation

To facilitate distribution the data is read from an enclosed CSV file (in the `data` folder.) This file is prepared once a month (on the 5th) by running the the preprocessing file from the CLI:

```python
python src/preprocess.py
```

This procedure starts by fetching the result data from the database and then performs the necessary cleaning and transformation steps. Finally it saves the preprocessed data in CSV format.

---

## TODOs and stuff

### Quickwins & FIXES

- [ ] Implement KPI-Group filtering (probably in the DICT file)
- [ ] Implement NCAs, depending on framework logic (decision pending)
- [ ] Make sure that png's are saved in the right place, time-stamp the filenames
- [ ] # TODO replace "CH" with "CCL" in `preprocess.py` as soon as kpi_names in DB are updated
- [ ] # TODO remove temporary fix in sql_statement as soon as kpi_id 27 is fixed

### PROBABLE BUGS IN THE DATA

- [ ] agg_level_id = 3 seems to be missing for kpi_id = 78. Is there a reason for that?
- [ ] ...

### Backlog (ideas for next phases)

- [ ] Highlight biggest changes, anomalies (set thresholds for absolute values)
- [ ] Build a "plot assembler", users can choose highlighting of correlations, comparison of entities etc.
- [x] Why not plot aggregations? -> because it makes no sense, you just blur the trends
- [ ] Give an option to download plots as html objects, see [here](https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426)
- [ ] Implement user authentication, see [here](https://discuss.streamlit.io/t/hide-text-input-box-after-the-input/4381)
- [ ] Add more [Caching](https://docs.streamlit.io/en/stable/caching.html#example-4-when-an-inner-function-changes)
- [ ] "Clear all" function to deselect all selected options, see [here](https://discuss.streamlit.io/t/reset-multiselect-to-default-values-using-a-checkbox/1941)
- [ ] Just in case: Display URLs in df as clickable hyperlink, see [here](https://discuss.streamlit.io/t/display-urls-in-dataframe-column-as-a-clickable-hyperlink/743)

### Necessary discussions for db enhancement

- [ ] DB should include Budgets
- [ ] Will ratios be calculated in the app or on the db --> probably db according to Marco

### Assumptions

- We load and preprocess data once a month (an on-the-fly approach with live data would be possible but probably makes no sense ...)
- I only use the agg level IDs 1-5 (no F&C, no organizational stuff, no status)
- When new KPI are added that cannot be summed up for period aggregations, I have to add them to the NO_SUM_KPI dict
- For info only: For the 'early' periods that are more than 1 year back (and thus hidden from display) diff_calc and ytd-summation don't work properly (compare app results to `test_cases.xlsx` in the dev folder)

### Fragestellungen PM ("Kick-off" 1 vom 2.7.20)

- [ ] "Ich möchte eine Übersicht über den Durschnittsumsatz und die aktiven Accounts aller Produkte."
- [ ] "Warum sehen wir eine Reduktion im Interchange-Revenue?"
- [ ] "In welchen Produkten haben wir die profitabelsten Kunden?"
- [ ] "Wir planen ein neues Produkt auf Platinum-Level. Welches ist das Zielpublikum?"
- [ ] "Haben sich auf Grund von Loyalty-Kampagnen die 'Fokus-KPI' wie gewünscht verändert?"
- [ ] "Einen schnellen Quervergleich von Performance- und Demographie-KPI über mehrere Produkte."
- [ ] "%-Anteil revolving Customers an Gesamtkunden für die verschiedenen Produkte."
- [ ] "Womit verdienen wir am meisten?"

### Bare git And DSS Server

- Path to bare git repo: '/O/Sales and Marketing/60_Customer Analytics/30_Projekte/86_KPI_Initiative/KPI-Sheet M&S/repo.git'
- Env on DS Server is `kpi_app_2`, this is an env without jupyter extensions (which do not work on the DSS)
