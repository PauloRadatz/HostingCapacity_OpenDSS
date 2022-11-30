# -*- coding: utf-8 -*-
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : data_analysis.py
# @Software: PyCharm

import pandas as pd
import pathlib
import os
import matplotlib.pyplot as plt
import matplotlib.axes._axes as axes
import matplotlib.figure as figure

script_path = os.path.dirname(os.path.abspath(__file__))
output_hc_file = pathlib.Path(script_path).joinpath("outputs", "results.csv")
output_tshc_file = pathlib.Path(script_path).joinpath("outputs", "results_tshc.csv")

hc_df = pd.read_csv(output_hc_file, index_col=0)
min_gen_hc = hc_df[["OV Gen HC (kW)", "OL Gen HC (kW)"]].min(axis=1).values[0]
min_load_hc = hc_df[["UV Load HC (kW)", "OL Load HC (kW)"]].min(axis=1).values[0]

print(f"Max gen HC at C = {min_gen_hc} kW")
print(f"Max load HC at C = {min_load_hc} kW")

tshc_df = pd.read_csv(output_tshc_file)
tshc_df["gen kW"] = tshc_df[["OV Gen HC (kW)", "OL Gen HC (kW)"]].min(axis=1)
tshc_df["load kW"] = -1 * tshc_df[["UV Load HC (kW)", "OL Load HC (kW)"]].min(axis=1)

fig, ax = plt.subplots()  # type: figure.Figure, axes.Axes
ax.plot(range(24), tshc_df["gen kW"], label="HC gen", color="r")
ax.plot(range(24), tshc_df["load kW"], label="HC load", color="b")
ax.set_xlabel('Hour')
ax.set_ylabel('Hosting Capacity kW')
ax.set_title('Envelope')
ax.grid()
ax.legend(loc=0)

plt.show()


