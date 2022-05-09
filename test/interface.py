import os,sys

from Top.Chip import ChipTop
from Core.Utils.reg import Register




class net_test:
    def __init__(self,stage_num=0,binary_dir='./binary/'):
        self.stage_num = stage_num
        self.binary_dir = binary_dir
        self.stage_time_list = []


    def test_latency(self):

        for i in range(self.stage_num):
            print("Running Stage:{}".format(i))
            # if i != 3:
            #     continue
            top = ChipTop()
            top.build()

            cur_dir = self.binary_dir + "stage_{}/".format(i)
            top.load_dict(cur_dir)

            stage_time = top.run_all()
            self.stage_time_list.append(stage_time)
            print("Stage:{} latency:{}".format(i,stage_time))

        print(self.stage_time_list)


if __name__ == "__main__":
    test = net_test(8)
    test.test_latency()


