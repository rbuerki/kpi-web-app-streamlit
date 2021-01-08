﻿--============================================================================================================
-- SELECT DATA FOR KPI-SHEET
--============================================================================================================

-- DEFINE DATERANGE
-------------------

/*Set min date: 
1) find last calculation date in kpi_results 
2) from there take the last day of the previous month
3) from there subtract the number of years passed as variable
*/

-- DECLARE @n_years_back INT = 3
DECLARE @last_date DATE = (SELECT MAX(calculation_date) FROM KF_CORE.CALC.kpi_result)
DECLARE @max_date DATE = (SELECT DATEADD(MONTH, DATEDIFF(MONTH, -1, @last_date)-1, -1))
DECLARE @min_date DATE = (SELECT DATEADD(YEAR, (@n_years_back *-1), @max_date))


-- SELECT DATA
--------------

SELECT
	r.period_value,
	r.kpi_id,
	kpi.kpi_name_de AS kpi_name,
	--r.calculation_date,
	r.period_id,
	r.agg_level_id,
	r.agg_level_value,
	r.value,
	vp.mandant,
	vp.kartenprofil AS cardprofile
FROM calc.kpi_result AS r
	LEFT JOIN (
		SELECT distinct
		produkt,
		mandant,
		kartenprofil
	FROM jemas_base.dbo.v_produkt
	) AS vp
		ON vp.produkt = r.agg_level_value
	JOIN kf_core.mstr.kpi AS kpi
		ON kpi.kpi_id = r.kpi_id
WHERE r.calculation_date >= @min_date
	AND r.agg_level_id in (1, 2, 4, 5)
	AND r.period_id in (1, 2)
ORDER BY r.kpi_id, agg_level_id, period_id, period_value

/*
Notes:
- agg_level_id 3 was removed on 22.10.20 because it is no longer provided, see Mail Mirko from same day
*/
