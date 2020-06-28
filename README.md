# App "KPI Sheet"

## TODO

- [x] V1: Implement KPI multiselection
- [x] FLEX: Implement monthly vs ytd display as in V1
- [x] FLEX: Prototype Visualization
- [ ] GENERAL: Output an "aktueller Datenstand" in Sidebar
- [ ] GENERAL: Separate Preprocessing from Rest (cause preprocessing needs not to be run with rest of app), refactor Plotting to helpers (in own branch, test-driven!)
- [ ] GENERAL: "Clear all" function to deselect all selected options, see [here](https://discuss.streamlit.io/t/reset-multiselect-to-default-values-using-a-checkbox/1941)
- [ ] GENERAL: Drop option "all" in UI as soon as something else is selected
- [ ] GENERAL: [Caching](https://docs.streamlit.io/en/stable/caching.html#example-4-when-an-inner-function-changes)
- [ ] GENERAL: Implement Tests!
- [ ] GENERAL: Docker (see videos cleancodeforDS)
- [ ] Input for refactoring: ```a = st.sidebar.selectbox('Choose a restaurant', options, format_func=lambda x: dic[x]) st.write(a)```

## Considerations for Deployment

- [ ] [Blogpost](https://towardsdatascience.com/sharing-streamlit-apps-securely-with-your-clients-a34bf0f9e00c)
- [ ] ...

## Questions for the Business

- [ ] What are the main "User Stories" (examples of questions to be answered)
- [ ] In V1A - Maybe include Percentage of total?
- [ ] In V1A - Filtering for Mandant / Entity in one big dropdown, or in two steps (mandant-high-level, Sub-Produkts)
- [ ] ...

## Assumptions

- We load and preprocess data once a month (an on-the-fly approach with live data would be possible but probably makes no sense ...)
- We have a column with a "last day of the month" date for every row in the original data set
- No entity-kpi-combination has period_ids for 1 AND 2 (but one OR the oter). The same holds true for period_ids 5 and 6 (? - not yet implemented).
- The data in `data_dicts.py` has to be checked and updated if necessary
- ...
