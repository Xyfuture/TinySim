import os,sys

from Top.Chip import ChipTop
from Core.Utils.reg import Register




class net_test:
    def __init__(self,stage_num=0,binary_dir='./binary/'):
        self.stage_num = stage_num
        self.binary_dir = binary_dir
        self.stage_latency_list = []
        self.stage_energy_list = []


    def test_latency_energy(self):

        for i in range(self.stage_num):
            print("Running Stage:{}".format(i))
            # if i != 3:
            #     continue
            top = ChipTop()
            top.build()

            cur_dir = self.binary_dir + "stage_{}/".format(i)
            top.load_dict(cur_dir)

            stage_time = top.run_all()
            stage_energy = top.compute_total_energy()

            self.stage_energy_list.append(stage_energy)
            self.stage_latency_list.append(stage_time)
            print("Stage:{} latency:{} nS energy:{} pJ".format(i,stage_time,stage_energy))

        print("Latency List:")
        print(self.stage_latency_list)
        print("Energy List:")
        print(self.stage_energy_list)

        with open(self.binary_dir+"result.txt",'w') as f:
            f.write("Latency List\n")
            for l in self.stage_latency_list:
                f.write("{} ".format(l))
            f.write("\nEnergy List\n")
            for l in self.stage_energy_list:
                f.write("{} ".format(l))


if __name__ == "__main__":
    test = net_test(6,'./binary/auto_encoder/')
    test.test_latency_energy()


