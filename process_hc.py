# -*- coding: utf-8 -*-
# @Time    : 8/6/2021 3:41 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : process_hc.py
# @Software: PyCharm

import py_dss_interface
import pathlib
import os
import math
import pandas as pd
from Methods import HostingCapacity

def set_baseline():
    dss.text("Set Maxiterations=100")
    dss.text("edit Reactor.MDV_SUB_1_HSB x=0.0000001")
    dss.text("edit Transformer.MDV_SUB_1 %loadloss=0.0000001 xhl=0.00000001")
    dss.text("Set controlmode=Off")

script_path = os.path.dirname(os.path.abspath(__file__))
dss_file = pathlib.Path(script_path).joinpath("Feeders", "ckt5", "Master_ckt5.dss")

dss = py_dss_interface.DSSDLL()

dss.text(f"Compile [{dss_file}]")
set_baseline()

buses = dss.circuit_allbusnames()
mv_buses = list()
mv_bus_voltage_dict = dict()
for bus in buses:
    dss.circuit_setactivebus(bus)
    if bus == "sourcebus":
        pass
    elif dss.bus_kVbase() >= 1.0 and len(dss.bus_nodes()) == 3:
        mv_buses.append(bus)
        mv_bus_voltage_dict[bus] = dss.bus_kVbase() * math.sqrt(3)

bus_name_list = []
hc_list = []
for bus in mv_buses:
    dss.text(f"Compile [{dss_file}]")
    set_baseline()
    bus_name_list.append(bus)
    hc_obj = HostingCapacity(dss, bus, 0.3)
    p_max = hc_obj.ov_criteria_hc_calc(mv_bus_voltage_dict[bus], 1.05, 100)
    hc_list.append(p_max)

dict_to_df = dict()
dict_to_df["Bus_name"] = bus_name_list
dict_to_df["Hosting_Capacity_kW"] = hc_list

df = pd.DataFrame().from_dict(dict_to_df)

output_file = pathlib.Path(script_path).joinpath("outputs", "results.csv")
df.to_csv(output_file, index=False)