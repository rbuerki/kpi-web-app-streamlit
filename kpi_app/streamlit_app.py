import streamlit as st
import helpers


st.title("KPI Sheet")


data_full = helpers.load_data("../data/test/mock_preprocessed.csv")
data = helpers.create_df_display(data_full)

# FILTER SECTION
filter_dict = helpers.get_filter_dict(data)
filter_values_1 = helpers.get_filter_values_1(filter_dict)

filter_dim = st.radio("Choose dimension:", options=["Product", "Profile"])
filter_mandant = st.selectbox("Choose Mandant:", options=filter_values_1)
st.write("")

if filter_mandant == "Overall":
    if filter_dim == "Product":
        agg_level = [1, 4]
    else:
        agg_level = [1, 2]
else:
    if filter_dim == "Product":
        agg_level = [4, 5]
    else:
        agg_level = [4, 3]

# # if filter_dim == "Product":
# #     if filter_mandant == "Overall":
# #         agg_level = [1, 4]
# #     else:
# #         agg_level = [4, 5]
# # elif filter_dim == "Profile":
# #     if filter_mandant == "Overall":
# #         agg_level = [1, 2]
# #     else:
# #         agg_level = [4, 3]

# # DISPLAY SECTION
# st.write(data)
# st.write(data["agg_level_id"])
data = helpers.filter_for_display(data, mandant=filter_mandant, agg_level=agg_level)
# st.dataframe(data)
display_dict = helpers.iter_through_kpi_ids(data)

for k, v in display_dict.items():
    st.write(f"**{k}**")
    v = helpers.style_for_display(v)
    st.table(v.style.format({"Wert": "{:,.0f}", "Abw 12Mte (%)": "{:0.1%}"}))
