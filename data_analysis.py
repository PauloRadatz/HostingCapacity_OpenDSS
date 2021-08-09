# -*- coding: utf-8 -*-
# @Time    : 8/9/2021 11:07 AM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : data_analysis.py
# @Software: PyCharm

import pandas as pd
import pathlib
import os
import matplotlib.pyplot as plt

script_path = os.path.dirname(os.path.abspath(__file__))
output_file = pathlib.Path(script_path).joinpath("outputs", "results.csv")

df = pd.read_csv(output_file, index_col=0)

print(df["Hosting_Capacity_kW"].describe())

df.plot.hist(bins=15)
plt.grid()
plt.show()