# App "KPI Sheet"

## TODO

- [ ] Index ausblenden
- [ ] export excel sort by entität (oder passend), spaltenbezeichnungen
>>>>>>> dev

## Considerations for Deployment

- [ ] [Blogpost](https://medium.com/rate-engineering/using-docker-containers-as-development-machines-4de8199fc662)
- [ ] [Blogpost](https://towardsdatascience.com/sharing-streamlit-apps-securely-with-your-clients-a34bf0f9e00c)
- [ ] Docker (see videos cleancodeforDS)

## Assumptions

- We load and preprocess data once a month (an on-the-fly approach with live data would be possible but probably makes no sense ...)
- I only use the agg level IDs 1-5 (no F&C, no organizational stuff, no status)
- When new KPI are added that cannot be summed up for period aggregations, I have to add them to the NO_SUM_KPI dict

## Backlog (Next Phases)

- [ ] Korrelationen zwischen verschiedenen KPI darstellen (Wählen für x und y Achse)
- [ ] Extreme Veränderungen hervorheben, Anomalies (v.a. auch zu Vormonat)
- [ ] Implement NCAs ...
- [ ] Implement KPI-Groups
- [ ] Add more [Caching](https://docs.streamlit.io/en/stable/caching.html#example-4-when-an-inner-function-changes)
- [ ] "Clear all" function to deselect all selected options, see [here](https://discuss.streamlit.io/t/reset-multiselect-to-default-values-using-a-checkbox/1941)
- [ ] Drop option "all" in UI as soon as something else is selected

- [ ] Budget-Werte reinnehmen
- [ ] Nur zur Info: Für 'frühe' Perioden > 1 Jahr zurück (jetzt versteckt) funktioniert die diff_calc und die ytd-summation nicht

## Fragestellungen PM ("Kick-off" 1 vom 2.7.20)

- [ ] "Ich möchte eine Übersicht über den Durschnittsumsatz und die aktiven Accounts aller Produkte."
- [ ] "Warum sehen wir eine Reduktion im Interchange-Revenue?"
- [ ] "In welchen Produkten haben wir die profitabelsten Kunden?"
- [ ] "Wir planen ein neues Produkt auf Platinum-Level. Welches ist das Zielpublikum?"
- [ ] "Haben sich auf grund von Loyalty-Kampagnen die 'Fokus-KPI' wie gewünscht verändert?"
- [ ] "Einen schnellen Quervergleich von Performance- und Demographie-KPI über mehrere Produkte."
- [ ] "%-Anteil revolving Customers an Gesamtkunden für die verschiedenen Produkte."
- [ ] "Womit verdienen wir am meisten?"

## Bare git And DSS Server

- Path to bare git repo: '/O/Sales and Marketing/60_Customer Analytics/30_Projekte/86_KPI_Initiative/KPI-Sheet M&S'
- Env on DS Server is `kpi_app_2`, this is an env without jupyter extensions (which do not work on the DSS)
