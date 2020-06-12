# App "KPI Sheet"

## Assumptions for Prototype

[ ] only period_id = 2 is considered (probably we will need period_id = 1 too, but what is the logic when choosing?
[ ] we get a column with a "last day of the month" date for every row in the original data (else the actual preprocessing will break)

## Questions for the Business

[ ] Maybe include Percentage of total?
[ ] Filtering for Mandant / Entity in one big dropdown, or in two steps (mandant-high-level, Sub-Produkts)
[ ] ....

## Discussion with ACI

Questions:
- What is the definition of Abw. YTD?
- What is the definition of Abw. 12months?
- Wich period level for which KPI?

For the moment I have to manually curate following logics for each KPI:

- Which period_level to take for display (1, 2, (5))
- Which display format to take for display (int, float, percentage, ...)

For the moment I have to manually curate following logics for each Entity:

- Hierarchical affiliation
- ...
