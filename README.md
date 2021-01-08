# Web-Application "KPI Sheet"

Dez 2020, Version 0.2

## Introduction

An interactive web app to display relevant KPI data for business stakeholders in Marketing, Product Management, and Senior Management in general.
Witin the company network the app can be accessed by the UWI Chrome webbrowser through the exposed network address.

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

- Server: XXX
- Folder: "/C/Projects/kpi_app/"

## Run

When started the app will expose a local address and a network address. The latter is used for sharing it.

### Run On Server (Prod)

There is a job installed on the server that checks every morning at 06:55 am if a python process with the "streamlit.exe" command is running. If not it will try to relaunch the app. For this purpose there are two batch files in the main project folder:

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

In the production environment on the server the update process is scheduled with the Windows Task Manager to take place every 5th of the month at 07:00 AM. That's what the batch file `auto_preprocess.bat` is for. (It works only on the server.) After the update you should pull the new CSV to the local env if you want to have the actual data there too.

**Attention:** After the update the cache of the app has to be refreshed manually. This is something that is not yet automated ...

### Manually (On Server or Locally)

If you want to run the preprocessing manually from the CLI, enter the following command from the main folder:

```python
python src/preprocess.py
```

---

## Documentation for Development

For a step-by-step "documentation" of the data processing in the app look at the `dev_helpers_new.ipynb` in the `dev/` folder. This helps to understand the logic and functionality of the app.

**Some general info:**

- We load and preprocess data once a month and read from a csv file. There is no live connection to the database
- We only load the agg level IDs 5 (so, no F&C, no organizational stuff, no status) We also load period_id 2 only ...
- ... whith one exception: "Anzahl gültige Konten Total" is the only kpi with period_id = 1 ("Aktive Konten" is a monthly KPI)

**Important for maintenance:**

- At the moment there is two KPI that will NOT be summed up for period aggregations (because this would lead to false results): "Gültige Konten" and "Aktive Konten". They are tracked manually in the NO_SUM_KPI dict in the `data.dicts.py` module. If ever a new KPI is added to the app that should also not be summed up for period aggregations, you have to add it to that dictionary!
