# -*- coding: utf-8 -*-
# @Time    : 8/6/2021 3:00 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : Methods.py
# @Software: PyCharm


class HostingCapacity:


    def __init__(self, dss, bus, load_mult):
        """

        Parameters
        ----------
        dss
        bus
        load_mult
        circuit_pu
        kva_to_kw
        pf
        """
        self.dss = dss
        self.bus = bus
        self.load_mult = load_mult



    def ov_criteria_hc_calc(self, gen_kv, ov_threshold_pu, p_step, max_p=10000):
        """

        Parameters
        ----------
        ov_threshold_pu
        p_step
        max_p

        Returns
        -------

        """
        self.__new_gen(gen_kv, p_step)

        i = 0
        ov_violation = False

        while not ov_violation and i * p_step <= max_p:
            i += 1
            self.__increment_generator_size(p_step * i)
            self.dss.text("solve")
            max_v = self.__get_max_feeder_voltage()

            if max_v > ov_threshold_pu:
                ov_violation = True

        if ov_violation:
            return (i - 1) * p_step
        else:
            return max_p

    def __new_gen(self, gen_kv, kw):
        self.dss.text(f"new generator.gen phases=3 kv={gen_kv} bus1={self.bus} kw={kw} kva={kw} pf=1")

    def __increment_generator_size(self, kw):
        self.dss.text(f"edit generator.gen kw={kw} kva={kw}")

    def __get_max_feeder_voltage(self):
        voltages = self.dss.circuit_allbusvmagpu()
        return max(voltages)



