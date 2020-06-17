import pandas as pd
import streamlit as st
import helpers


st.title("KPI Sheet")


data_full = helpers.load_data("../data/test/mock_preprocessed.csv")
data = helpers.create_df_with_actual_period_only(data_full)

# FILTER SECTION
filter_dict = helpers.get_filter_dict(data)
filter_values_1 = helpers.get_filter_values_1(filter_dict)

filter_dim = st.radio("Choose dimension:", options=["Product", "Profile"])
filter_mandant = st.selectbox("Choose Mandant:", options=filter_values_1)
st.write("")


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

# DISPLAY SECTION ENTITY

# if filter_mandant == "Overall":
#     if filter_dim == "Product":
#         agg_level = [1]
#     else:
#         agg_level = [2]
# else:
#     if filter_dim == "Product":
#         agg_level = [4, 5]
#     else:
#         agg_level = [3]

# data = helpers.filter_for_display(data, mandant=filter_mandant, agg_level=agg_level)
# display_dict = helpers.create_dict_of_df_per_entity(data)

# for k, v in display_dict.items():
#     st.write(f"**{k}**")
#     v = helpers.arrange_for_display_per_entity(v)
#     st.table(v.style.format({"Wert": "{:,.0f}", "Abw 12Mte": "{:0.1%}"}))

# DISPLAY SECTION KPI

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

data = helpers.filter_for_display(data, mandant=filter_mandant, agg_level=agg_level)
display_dict = helpers.create_dict_of_df_per_kpi(data)


def df_style(val):
    return "font-weight: bold"


# TODO: if dim="profile" and mandant != "overall", then sort agg_level DESC

for k, v in display_dict.items():
    st.write(f"**{k}**")
    v = helpers.arrange_for_display_per_kpi(v)
    st.table(
        v.style.format({"Wert": "{:,.0f}", "Abw 12Mte": "{:0.1%}"}).applymap(
            helpers.set_bold_font, subset=pd.IndexSlice[v.index[v.index == 0], :]
        )
    )
