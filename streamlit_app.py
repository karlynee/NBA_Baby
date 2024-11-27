import streamlit as st
import pandas as pd

st.write(1234)
st.write(
    pd.DataFrame(
        {
            "first column": [1, 2, 3, 4],
            "second column": [10, 20, 30, 40],
        }
    )
)
sql = "SELECT * FROM nba-baby-442813.Teams.total_stats_23_24;"
#df_stats2324 = pd.read_gbq(sql,project_id="nba-baby-442813",dialect="standard")
#df_stats2324.head()

