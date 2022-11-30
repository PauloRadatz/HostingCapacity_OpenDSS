# -*- coding: utf-8 -*-
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : Methods.py
# @Software: PyCharm


class HostingCapacity:

    def __init__(self, dss_file, dss, bus, load_mult_new_gen, load_mult_new_load, max_p, p_step):
        self.dss_file = dss_file
        self.dss = dss
        self.bus = bus
        self.load_mult_new_gen = load_mult_new_gen
        self.load_mult_new_load = load_mult_new_load
        self.max_p = max_p
        self.p_step = p_step

    def set_feeder(self):
        self.dss.text(f"Compile [{self.dss_file}]")

    def ov_gen_hc_calc(self, gen_kv, ov_threshold_pu):
        self.set_feeder()
        self.__new_gen(gen_kv, self.p_step)

        i = 0
        ov_violation = False

        self.dss.text(f"set loadmult={self.load_mult_new_gen}")
        self.dss.text("solve")
        # self.dss.text("Plot profile phases=all")
        while not ov_violation and i * self.p_step <= self.max_p:
            i += 1
            self.__increment_generator_size(self.p_step * i)
            self.dss.text("solve")
            # self.dss.text("Plot profile phases=all")
            max_v = self.__get_max_feeder_voltage()

            if max_v > ov_threshold_pu:
                ov_violation = True

        if ov_violation:
            return (i - 1) * self.p_step
        else:
            return self.max_p

    def ol_gen_hc_calc(self, gen_kv):
        self.set_feeder()
        self.__new_gen(gen_kv, self.p_step)

        i = 0
        ol_violation = False

        self.dss.text(f"set loadmult={self.load_mult_new_gen}")
        self.dss.text("solve")
        # self.dss.text("Plot profile phases=all")
        while not ol_violation and i * self.p_step <= self.max_p:
            i += 1
            self.__increment_generator_size(self.p_step * i)
            self.dss.text("solve")
            # self.dss.text("Plot profile phases=all")
            for element in self.dss.circuit_all_element_names():
                if element != "Vsource.source":
                    if element.split(".")[0] == "Line":
                        self.dss.circuit_set_active_element(element)
                        rating_current = self.dss.cktelement_read_norm_amps()
                        element_currents = self.dss.cktelement_currents_mag_ang()

                        if self.dss.cktelement_num_phases() == 3:
                            max_phase_current = max(element_currents[0:12:2])
                        elif self.dss.cktelement_num_phases() == 2:
                            max_phase_current = max(element_currents[0:8:2])
                        elif self.dss.cktelement_num_phases() == 1:
                            max_phase_current = max(element_currents[0:4:2])

                        if rating_current > 0:
                            if max_phase_current / rating_current > 1:
                                # print(f"OL Gen element = {element}")
                                ol_violation = True
                                break

        if ol_violation:
            return (i - 1) * self.p_step
        else:
            return self.max_p

    def uv_load_hc_calc(self, load_kv, uv_threshold_pu):
        self.set_feeder()
        self.__new_load(load_kv, self.p_step)

        i = 0
        uv_violation = False

        self.dss.text(f"set loadmult={self.load_mult_new_load}")
        self.dss.text("solve")
        # self.dss.text("Plot profile phases=all")
        while not uv_violation and i * self.p_step <= self.max_p:
            i += 1
            self.__increment_load_size(self.p_step * i)
            self.dss.text("solve")
            # self.dss.text("Plot profile phases=all")
            min_v = self.__get_min_feeder_voltage()

            if min_v < uv_threshold_pu:
                uv_violation = True

        if uv_violation:
            return (i - 1) * self.p_step
        else:
            return self.max_p

    def ol_load_hc_calc(self, load_kv):
        self.set_feeder()
        self.__new_load(load_kv, self.p_step)

        i = 0
        ol_violation = False

        self.dss.text(f"set loadmult={self.load_mult_new_load}")
        self.dss.text("solve")
        # self.dss.text("Plot profile phases=all")
        while not ol_violation and i * self.p_step <= self.max_p:
            i += 1
            self.__increment_load_size(self.p_step * i)
            self.dss.text("solve")
            # self.dss.text("Plot profile phases=all")
            for element in self.dss.circuit_all_element_names():
                if element != "Vsource.source":
                    if element.split(".")[0] == "Line":
                        self.dss.circuit_set_active_element(element)
                        rating_current = self.dss.cktelement_read_norm_amps()
                        element_currents = self.dss.cktelement_currents_mag_ang()

                        if self.dss.cktelement_num_phases() == 3:
                            max_phase_current = max(element_currents[0:12:2])
                        elif self.dss.cktelement_num_phases() == 2:
                            max_phase_current = max(element_currents[0:8:2])
                        elif self.dss.cktelement_num_phases() == 1:
                            max_phase_current = max(element_currents[0:4:2])

                        if rating_current > 0:
                            if max_phase_current / rating_current > 1:
                                # print(f"OL Load element = {element}")
                                ol_violation = True
                                break

        if ol_violation:
            return (i - 1) * self.p_step
        else:
            return self.max_p

    def __new_gen(self, gen_kv, kw):
        self.dss.text(f"new generator.gen "
                      f"phases=3 "
                      f"kv={gen_kv} "
                      f"bus1={self.bus} "
                      f"kw={kw} "
                      f"kva={kw} "
                      f"pf=1 "
                      f"vmaxpu=1.2 "
                      f"vminpu=0.8")

    def __new_load(self, load_kv, kw):
        self.dss.text(f"new load.load "
                      f"phases=3 "
                      f"kv={load_kv} "
                      f"bus1={self.bus} "
                      f"kw={kw} "
                      f"pf=1 "
                      f"status=Fixed "
                      f"vmaxpu=1.2 "
                      f"vminpu=0.8")

    def __increment_generator_size(self, kw):
        self.dss.text(f"edit generator.gen "
                      f"kw={kw} "
                      f"kva={kw}")

    def __increment_load_size(self, kw):
        self.dss.text(f"edit load.load "
                      f"kw={kw}")

    def __get_max_feeder_voltage(self):
        voltages = self.dss.circuit_all_bus_vmag_pu()
        return max(voltages)

    def __get_min_feeder_voltage(self):
        voltages = self.dss.circuit_all_bus_vmag_pu()
        return min(voltages)



