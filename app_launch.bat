@echo on
call conda activate kpi_app
call streamlit run "src/app.py"
@pause