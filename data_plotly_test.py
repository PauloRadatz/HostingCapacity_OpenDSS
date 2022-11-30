# -*- coding: utf-8 -*-
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : data_plotly_test.py
# @Software: PyCharm


import pandas as pd
import pathlib
import os
import plotly.express as px

script_path = os.path.dirname(os.path.abspath(__file__))
output_tshc_file = pathlib.Path(script_path).joinpath("outputs", "results_tshc.csv")

tshc_df = pd.read_csv(output_tshc_file)
tshc_df["gen kW"] = tshc_df[["OV Gen HC (kW)", "OL Gen HC (kW)"]].min(axis=1)
tshc_df["load kW"] = -1 * tshc_df[["UV Load HC (kW)", "OL Load HC (kW)"]].min(axis=1)

fig = px.line(tshc_df, x=list(range(24)), y=tshc_df["gen kW"])

# Add Scatter plot
fig.add_scatter(x=list(range(24)), y=tshc_df["load kW"])

# Display the plot
fig.show()