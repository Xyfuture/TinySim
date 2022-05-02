import copy
import math

#use data from ISAAC
# run @ 1.28Ghz
class DeviceConfig:
    # Power Unit:  mW
    # Time Unit:   nS
    # energy Unit: nJ
    def __init__(self):
        self.frequency = 1.28 # Ghz

        self.xbar_size = [128,128]
        self.xbar_cell_bit = 2

        self.xbar_power = 0.6  # mW


        self.DAC_bit = 1
        self.DAC_power = 4/1024  # mW
        self.DAC_num = 128

        self.ADC_bit = 8
        self.ADC_power = 2 # mW
        self.ADC_num = 1

        self.shift_add_power = 0.05 # mW



class MeuConfig:
    def __init__(self):
        self.xbar_layout = [4,4]
        self.weight_bit = 8
        self.input_bit = 8

class Xbar:
    def __init__(self, cfg:DeviceConfig):
        self.size = cfg.xbar_size
        self.cell_bit = cfg.xbar_cell_bit
        self.power = cfg.xbar_power
        self.rows,self.columns = self.size


class DAC:
    def __init__(self, cfg:DeviceConfig):
        self.precision = cfg.DAC_bit
        self.power = cfg.DAC_power

class ADC:
    def __init__(self, cfg:DeviceConfig):
        self.precision = cfg.ADC_bit
        self.power = cfg.ADC_power


class SampleHold:
    def __init__(self, cfg:DeviceConfig):
        pass

class ShiftAdd:
    def __init__(self, cfg:DeviceConfig):
        self.power = cfg.shift_add_power


class Reg:
    def __init__(self):
        pass



class IMA:
    def __init__(self, dev_cfg:DeviceConfig,meu_cfg:MeuConfig):
        self.dev_cfg = dev_cfg
        self.meu_cfg = meu_cfg

        self.xbar = Xbar(dev_cfg)
        self.DAC = DAC(dev_cfg)
        self.ADC = ADC(dev_cfg)
        self.shift_add = ShiftAdd(dev_cfg)

        self.big_cycle_latency = math.ceil(1/self.dev_cfg.frequency * self.xbar.columns)
        self.xbar_cnt = self.meu_cfg.xbar_layout[0] * self.meu_cfg.xbar_layout[1]
        self.xbar_layout_row,self.xbar_layout_column = self.meu_cfg.xbar_layout



        self.latency = 0
        self.energy = 0


    def compute_latency(self):
        cycles = math.ceil(self.meu_cfg.input_bit/self.DAC.precision) + 2

        self.latency = cycles * self.big_cycle_latency



    def compute_energy(self):
        run_cycles = self.meu_cfg.input_bit

        DAC_energy = run_cycles * self.big_cycle_latency * self.DAC.power * self.dev_cfg.DAC_num * self.xbar_cnt
        xbar_enery = run_cycles * self.big_cycle_latency * self.xbar.power * self.xbar_cnt

        ADC_energy = run_cycles * self.big_cycle_latency * self.ADC.power * self.dev_cfg.ADC_num * self.xbar_cnt

        shift_add_energy = run_cycles * (self.xbar.columns*self.xbar_cnt +
                                         self.xbar_layout_column * math.ceil(math.log2(self.xbar_layout_row)) *
                                         math.ceil(self.xbar.cell_bit*self.xbar.columns/self.meu_cfg.input_bit))\
                           *(1/self.dev_cfg.frequency) * self.shift_add.power

        self.energy = DAC_energy + xbar_enery + ADC_energy + shift_add_energy

        # self.energy *= 1e-3 # 转换为 nJ


if __name__ == "__main__":
    ima = IMA(DeviceConfig(),MeuConfig())
    ima.compute_energy()
    ima.compute_latency()

    print(ima.latency)
    print(ima.energy)





