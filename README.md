# Web-Application "KPI Sheet"

Dez 2020, Version 0.2

## Introduction

An interactive web app to display relevant KPI data for business stakeholders in Marketing, Product Management, and Senior Management in general.
The app can be accessed by the UWI Chrome webbrowser through the exposed network address.

The app offers high flexibility on how to display the data:

- convenient filtering: by selected KPI, KPI groups, and / or selected entitites, entity groups
- different aggregations: data can be viewed per month, or, for all KPI permitting aggregation, per 3-month, 6-month, 12-month or year-to-date aggregations
- 2 display modes: tabular data can be displayed as to group all selected KPI per entity or as to compare all selected entities per KPI
- absolute values and average values per acitve accounts: averages are provided for monthly data and most KPI

An interactive plot is automatically displayed:

- When a single KPI and no more than 8 separate entities are chosen
- When a single entity and no more than 2 separate KPI are chosen

Plots (in PNG format) and the selected data (in XLSX format) can be saved into to the user's default `downloads/` folder at any time.

## Build & Infrastructure

The app is built with Python 3.8 and [streamlit](https://www.streamlit.io/). Use the included `env_kpi_app.yml` file to set up the necessary dependencies (with conda).

Development:

- Working folder: "/O/Sales and Marketing/60_Customer Analytics/30_Projekte/86_KPI_Initiative/KPI-Sheet M&S/20-06_kpi_app/"
- Git Repo: "/O/Sales and Marketing/60_Customer Analytics/30_Projekte/86_KPI_Initiative/KPI-Sheet M&S/repo.git"

Production:

- Server: wp8bv-srv0040
- Folder: "/C/Projects/kpi_app/"

## Run

When started the app will expose a local address and a network address. The latter is used for sharing it.

### Run On Server (Prod)

There is a job installed in the Windows Task Manager on the server that checks every morning at 06:55 am if a python process with the "streamlit.exe" command is running. If not, it will try to relaunch the app. For this purpose there are two batch files in the main project folder:

- `app_check.bat`
- `app_launch.bat`

While you can start the app by dubble clicking on either one of them, it is advised to use `app_check.bat` as it will first check if the app is not running and will execute `app_launch.py` only in that case. (Alternatively you could also start the app with a cli command, see next section. But why should you?)

### Run Locally (Dev)

Activate the conda environment. The app can then be run from the main folder (containing this README file) by typing the following command in the CLI.

```python
streamlit run src/app.py
```

## Monthly Data Preparation

The app reads the data from a CSV file that is stored in the `data/` folder. This data is fetched and preprocessed once a month from the KF_CORE DB. The preprocessed data is then saved in two CSV files: one is the actual 'working' datafile mentioned before (overwriting the existing data), the other is a permanent copy in the `data/history/`folder.

### Automated On The Server (Default)

In the production environment on the server the update process is scheduled as job in the Windows Task Manager to take place every 5th of the month at 07:00 AM. That's what the batch file `auto_preprocess.bat` is for. (It works only on the server.) After the update you should pull the new CSV to the local env if you want to have the actual data there too.

**Attention:** After the update the cache of the app has to be refreshed manually. This is something that is not yet automated ...

### Manually (On Server or Locally)

If you want to run the preprocessing manually from the CLI, enter the following command from the main folder:

```python
python src/preprocess.py
```

---

## Documentation for Development

For a step-by-step "documentation" of the data processing in the app look at the `dev_helpers_new.ipynb` in the `dev/` folder. This helps to understand the logic and functionality of the app.

**Main files in /src:**

- `app.py`: All things 'streamlit' / frontend. One simple function that controls the data processing flow and display in the app. It is completetly re-run after every user input.
- `helpers.py`: Containing all the data processing functions (filtering, aggregation, slicing) and some for dataframe styling. This functios are called in app.py.
- `downloads.py`: Kind of an extension to helpers.py. Contains functions that handle the data download in excel format if the user requests that.
- `plots.py`: Kind of an extension to helpers.py. Contains functions that handle the data plots if certain conditions are met.
- `data_dicts.py`: Some configuration logics. Separated from helpers.py so they can be updated / changed seperately from the functional logic.
- `SessionState.py`: The SessionState class is a bit of a hack and imported to app.py for the purpose of user authentication with a password only.
-`preporcess.py`: Handles fetching the data from the DB, preprocessing it and saving it in the required format. This is run monthly, independent of the rest of the application.

**3 Logging files:**

- `app.log`: Logs all function calls for functions in helpers.py. This documents the usage of the app.
- `check.log`: This logs the results of the daily job checking if the app is running activly on PROD and relaunching it if not.
- `preprocessing.log`: Logs the results for the data load / preprocessing including some checks for validation.

Logging is configured in the `logging.conf` file.

**Some general info:**

- We load and preprocess data once a month and read from a csv file. There is no live connection to the database
- We only load the agg level IDs 5 (so, no F&C, no organizational stuff, no status) We also load period_id 2 only ...
- ... whith one exception: "Anzahl gültige Konten Total" is the only kpi with period_id = 1 ("Aktive Konten" is a monthly KPI)

**Most important for maintenance:**

- At the moment there is two KPI that will NOT be summed up for period aggregations (because this would lead to false results): "Gültige Konten" and "Aktive Konten". They are tracked manually in the NO_SUM_KPI dict in the `data.dicts.py` module. If ever a new KPI is added to the app that should also not be summed up for period aggregations, you have to add it to that dictionary!

## TODOs and Stuff

### Up Next

APP_Automation

- [ ] I should automate a cache refresh after each data upate ...

PERFORMANCE

- [x] When I change the Stichtag I loose the selection for entity and mandant_groups, only if the mandant_filter_ list changes (e.g. from Jul 2020 back) --> ACCEPTABLE
- [ ] When I look at one KPI for one product and change the aggregation, the chart is always reloaded despite of it not changing. Caching the plot functions did not help ...

AGGREGATIONS

- [ ] Attention - it's dangerous to look at aggregated tables and display monthly values, because the Abw. VJ of the table is not the same as for the graph data
- [ ] If we aggregate I should maybe print a disclaimer that non_agg_kpi are not aggregated

CARDPROFILE VIEW

- [ ] Not implemented yet. Could probably do "quite easily" by installing a new agg_level during preprocessing

VARIA

- [ ] The newest NCA kpi "Antraege completed" is (temporarily ?) disabled in `preprocessing`. It is applicable on Mandant Level only (agg_level_value is identical), maybe I should exclude it in the sql select

### Backlog (ideas for next phases)

- [ ] Highlight biggest changes, anomalies (set thresholds for absolute values)
- [ ] Give an option to download plots as html objects, see [here](https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426)
- [ ] Add more [Caching](https://docs.streamlit.io/en/stable/caching.html#example-4-when-an-inner-function-changes)
- [ ] "Clear all" function to deselect all selected options, see [here](https://discuss.streamlit.io/t/reset-multiselect-to-default-values-using-a-checkbox/1941)
- [ ] Just in case: Display URLs in df as clickable hyperlink, see [here](https://discuss.streamlit.io/t/display-urls-in-dataframe-column-as-a-clickable-hyperlink/743)

### Deployment

- Tuorial for [Deployment with Docker on Heroku](https://discuss.streamlit.io/t/deploying-streamlit-apps-with-docker-on-heroku/5136)
- 'Official' [Streamlit Deployment Guide](https://discuss.streamlit.io/t/streamlit-deployment-guide-wiki/5099)

## KPI-Liste Ausbau

- Prio 1: Abbildung CM1
- Prio 2: Abbildung Revenues (Zinseinnahmen --> Revolving, FX-Einnahmen, Kartengebühren, ...)
- Prio 3: Abbildung Sozio-demographische Merkmale, Dauer Kundenbeziehung BCAG, Credit-Risk-Score, ... (müssen noch genauer definiert werden)
- Prio 4: Möglicherweise Abbildung Durchschnitts-Werte für Umsätze, CM1, Revenues und Trx pro gültige Konten
- Prio 5: Möglicherweise Abbildung Durchschnitte pro aktive Konten (braucht zusätzliche Views)

### Fragestellungen PM ("Kick-off" 1 vom 2.7.20)

- [ ] "Ich möchte eine Übersicht über den Durschnittsumsatz und die aktiven Accounts aller Produkte."
- [ ] "Warum sehen wir eine Reduktion im Interchange-Revenue?" --> könnte man aufnehmen, Revenues sind in KF_CORE verfügbar (noch keine KPI)
- [ ] "In welchen Produkten haben wir die profitabelsten Kunden?" --> CM1, Durchschnitt gültige Konten (aktive macht nicht Sinn hier)
- [ ] "Wir planen ein neues Produkt auf Platinum-Level. Welches ist das Zielpublikum?" -->
- [ ] "Haben sich auf Grund von Loyalty-Kampagnen die 'Fokus-KPI' wie gewünscht verändert?"
- [ ] "Einen schnellen Quervergleich von Performance- und Demographie-KPI über mehrere Produkte."
- [ ] "%-Anteil revolving Customers an Gesamtkunden für die verschiedenen Produkte."
- [ ] "Womit verdienen wir am meisten?"

### Queries for validation of results

```SQL
SELECT        SUM(betrag) AS umsatz
FROM          jemas_base.dbo.Sales_Fact AS SF
WHERE         SF.erfassung_datum BETWEEN '20200101' AND '20201231 23:59'
AND                  SF.ist_umsatz = 1
;
```

Attention the following fetches unaggregated results only, I am responsible for the aggregations!

```SQL
SELECT        k.jamo, k.lea_id, lh.LEA_revised_name, k.produkt_id, p.produkt_FC, k.anzahl
FROM          jemas_report.fc.kennzahlen_stat_schnittstelle AS k
LEFT JOIN     jemas_report.fc.kennzahlen_stat_schnittstelle_LEA_help AS lh
       ON            k.LEA_id = lh.LEA_id
LEFT JOIN     (SELECT DISTINCT produkt_id_FC, produkt_FC FROM jemas_base.dbo.v_produkt) AS p
       ON            k.produkt_id = p.produkt_id_FC
WHERE         jamo = 202011
  AND         p.produkt_FC = 'Simply VISA Card Credit'
ORDER BY      anzahl DESC, jamo, LEA_id, produkt_id
;
```
