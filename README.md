# App "KPI Sheet"

## TODO

- [x] V1: Implement KPI multiselection
- [x] FLEX: Implement monthly vs ytd display as in V1
- [ ] FLEX: Prototype Visualization
- [ ] GENERAL: "Clear all" function to deselect all selected options
- [ ] GENERAL: Drop option "all" in UI as soon as something else is selected
- [ ] GENERAL: [Caching](https://docs.streamlit.io/en/stable/caching.html#example-4-when-an-inner-function-changes)
- [ ] GENERAL: Testing
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

## Some Assumptions

- We have a column with a "last day of the month" date for every row in the original data set
- No entity-kpi-combination has period_ids for 1 AND 2 (but one OR the oter). The same holds true for period_ids 5 and 6 (? - not yet implemented).
- ...
