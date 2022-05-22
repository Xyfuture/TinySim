# 暂时可能用不到这个



class RegFile:
    def __init__(self):
        self.reg_file = [0 for i in range(32)]

        self.dynamic_energy =0
        self.leakage_energy = 0
        self.total_energy = 0


        self.dynamic_per_energy = 0.551915625
        self.leakage_per_energy = 0.10605



    def __getitem__(self, item):
        if item == 0:
            return 0
        self.compute_dynamic_energy()
        return self.reg_file[item]

    def __setitem__(self, key, value):
        if key == 0:
            return
        self.compute_dynamic_energy()
        self.reg_file[key] = value

    def compute_leakage_energy(self,total_cycles):
        self.leakage_energy = self.leakage_per_energy * total_cycles


    def compute_dynamic_energy(self):
        self.dynamic_energy += self.dynamic_per_energy

    def compute_total_energy(self,total_cycles):
        self.compute_leakage_energy(total_cycles)
        self.total_energy = self.dynamic_energy+ self.leakage_energy

        return self.total_energy