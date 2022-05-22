import math

#eDRAM
#use destiny simulator
# 1MB 128Bytes/3ns
# low leakage power
#Unit nS mW pJ


class ScratchPad:
    def __init__(self):

        self.bus_bitwidth = 128 # Byte # 1024 bit
        self.mem_size = 1024*1024  # Byte

        self.access_latency = 3 # cycle or ns

        self.refresh_energy = 0
        self.pure_leakage_energy = 0
        self.total_leakage_energy = 0


        self.read_dynamic_energy = 0
        self.write_dynamic_energy = 0
        self.total_dynamic_energy = 0


        self.total_cycles = 0
        self.total_energy = 0


        self.leakage_power = 31.291 # mW

        self.read_per_energy = 329.038 # pJ
        self.write_per_energy = 1.462 * 1e3 # pJ
        self.refresh_per_energy = 126.521 * 1e3 #pJ



    def read_mem(self,rdata_size)->int:
        # 返回需要的时间
        self.compute_dynamic_energy(rdata_size,'read')

        return math.ceil(rdata_size/self.bus_bitwidth) * self.access_latency



    def write_mem(self,wdata_size)->int:
        # 返回需要的时间
        self.compute_dynamic_energy(wdata_size, 'write')

        return math.ceil(wdata_size / self.bus_bitwidth) * self.access_latency


    def compute_dynamic_energy(self,data_size,access_type='read'):

        if access_type == 'read':
            self.read_dynamic_energy += self.read_per_energy * math.ceil(data_size/self.bus_bitwidth)
        elif access_type == 'write':
            self.write_per_energy += self.write_per_energy * math.ceil(data_size/self.bus_bitwidth)


    def compute_leakage_energy(self,total_cycles):
        # Unit: nJ = W*nS
        self.total_cycles = total_cycles

        self.pure_leakage_energy = self.leakage_power * self.total_cycles # Unit pJ = mW * nS
        self.refresh_energy = self.refresh_per_energy * (self.total_cycles/1e6 /8) # 8ms 刷新一次

        self.total_leakage_energy = self.pure_leakage_energy + self.refresh_energy

        return self.total_leakage_energy

    def compute_total_energy(self,total_cycles):
        # Unit: pJ

        self.compute_leakage_energy(total_cycles)

        self.total_dynamic_energy = self.write_dynamic_energy + self.read_dynamic_energy
        self.total_energy += self.total_leakage_energy + self.total_dynamic_energy

        return self.total_energy