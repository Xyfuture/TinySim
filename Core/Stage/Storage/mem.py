


class ScratchPad:
    def __init__(self):

        self.bus_bitwidth = 0
        self.mem_size = 0

        self.total_leakage_energy = 0
        self.total_dynamic_energy = 0

        self.read_dynamic_energy = 0
        self.write_dynamic_energy = 0

        self.total_cycles = 0
        self.total_energy = 0

        self.leakage_power = 0


    def read_mem(self,rdata)->int:
        # 返回需要的时间
        pass

    def write_mem(self,):
        # 返回需要的时间
        pass

    def compute_leakage_energy(self,total_cycles):
        # Unit: nJ = W*nS
        self.total_cycles = total_cycles

        self.total_leakage_energy = self.leakage_power * self.total_cycles * 1e-9

        return self.total_leakage_energy

    def compute_total_energy(self):
        # Unit: nJ

        self.total_dynamic_energy = self.read_dynamic_energy+self.write_dynamic_energy
        self.total_energy = self.total_dynamic_energy + self.total_leakage_energy

        return self.total_energy