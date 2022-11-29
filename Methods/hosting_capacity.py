# -*- coding: utf-8 -*-
# @Time    : 8/6/2021 3:00 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : Methods.py
# @Software: PyCharm


class HostingCapacity:

    def __init__(self, dss_file, dss, bus, offpeak_load_mult, peak_load_mult, max_p, p_step):
        self.dss_file = dss_file
        self.dss = dss
        self.bus = bus
        self.offpeak_load_mult = offpeak_load_mult
        self.peak_load_mult = peak_load_mult
        self.max_p = max_p
        self.p_step = p_step

    def set_feeder(self):
        # self.dss.text(f"Compile [{self.dss_file}]")
        # self.dss.text("Set Maxiterations=100")
        # self.dss.text("Edit Vsource.Source pu=1.03")
        # self.dss.text("edit Reactor.MDV_SUB_1_HSB x=0.0000001")
        # self.dss.text("edit Transformer.MDV_SUB_1 %loadloss=0.0000001 xhl=0.00000001")
        # self.dss.text("Set controlmode=Off")

        self.dss.text(f"Compile [{self.dss_file}]")
        # self.dss.text("Set Maxiterations=100")
        # self.dss.text("Set Maxcontroli=100")
        # self.dss.text("Edit Vsource.Source pu=1.04")
        # self.dss.text("edit Reactor.MDV_SUB_1_HSB x=0.0000001")
        # self.dss.text("edit Transformer.MDV_SUB_1 %loadloss=0.0000001 xhl=0.00000001")
        # self.dss.text("Set controlmode=Off")
        # self.dss.text("batchedit load..* mode=1")
        # self.dss.text("batchedit load..* vmaxpu=1.25")
        # self.dss.text("batchedit load..* vminpu=0.75")
        # self.dss.text("New Energymeter.m1 Line.ln5815900-1 1")
        # self.dss.text("batchedit capacitor..* enabled=no")


    def ov_gen_hc_calc(self, gen_kv, ov_threshold_pu):
        self.set_feeder()
        self.__new_gen(gen_kv, self.p_step)

        i = 0
        ov_violation = False

        self.dss.text(f"set loadmult={self.offpeak_load_mult}")
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

        self.dss.text(f"set loadmult={self.offpeak_load_mult}")
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
                                print(f"OL Gen element = {element}")
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

        self.dss.text(f"set loadmult={self.peak_load_mult}")
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

        self.dss.text(f"set loadmult={self.peak_load_mult}")
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
                                print(f"OL Load element = {element}")
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
                      f"pf=1")

    def __new_load(self, load_kv, kw):
        self.dss.text(f"new load.load "
                      f"phases=3 "
                      f"kv={load_kv} "
                      f"bus1={self.bus} "
                      f"kw={kw} "
                      f"pf=1 "
                      f"status=Fixed")

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



