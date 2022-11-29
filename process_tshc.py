# -*- coding: utf-8 -*-
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : process_tshc.py
# @Software: PyCharm

import py_dss_interface
import pathlib
import os
import math
import pandas as pd
from Methods import HostingCapacity

script_path = os.path.dirname(os.path.abspath(__file__))
dss_file = pathlib.Path(script_path).joinpath("Feeders", "SimpleCircuit", "SimpleCircuit.dss")

dss = py_dss_interface.DSSDLL()

dss.text(f"Compile [{dss_file}]")
# mv_buses, mv_bus_voltage_dict = get_3ph_mv_buses()

bus_name_list = []
ov_gen_hc_list = []
uv_load_hc_list = []
ol_gen_hc_list = []
ol_load_hc_list = []
bus = "C"

dss.circuit_set_active_bus(bus)
bus_kv = dss.bus_kv_base() * math.sqrt(3)
bus_name_list.append(bus)

loadshape = [0.3, 0.32, 0.3, 0.3, 0.35, 0.42, 0.46, 0.59, 0.66, 0.88, 0.94, 0.98, 0.98, 0.98, 0.98, 0.99, 1, 0.95, 0.93, 0.91, 0.78, 0.69, 0.53, 0.47]

for load_level in loadshape:
    hc_obj = HostingCapacity(dss_file, dss, bus, load_level, load_level, 20000, 250)
    ov_gen_hc_list.append(hc_obj.ov_gen_hc_calc(bus_kv, 1.05))
    uv_load_hc_list.append(hc_obj.uv_load_hc_calc(bus_kv, 0.95))
    ol_gen_hc_list.append(hc_obj.ol_gen_hc_calc(bus_kv))
    ol_load_hc_list.append(hc_obj.ol_load_hc_calc(bus_kv))

# Save results in a csv file
dict_to_df = dict()
# dict_to_df["Bus_name"] = bus_name_list
dict_to_df["OV Gen HC (kW)"] = ov_gen_hc_list
dict_to_df["OL Gen HC (kW)"] = ol_gen_hc_list
dict_to_df["UV Load HC (kW)"] = uv_load_hc_list
dict_to_df["OL Load HC (kW)"] = ol_load_hc_list

df = pd.DataFrame().from_dict(dict_to_df)

output_file = pathlib.Path(script_path).joinpath("outputs", "results_tshc.csv")
df.to_csv(output_file, index=False)