

from Top.Chip import ChipTop
from Core.Utils.reg import Register

def reg_test():
    reg = Register()
    reg.a = 1
    print(reg.a)
    reg.a = reg.a + 1
    print(reg.a)
    reg.update()
    print(reg.a)


def chip_test():
    top = ChipTop()
    top.build()
    top.load_dict('inst/')
    # for i in range(20):
    #     print(i)
    #     top.run_cycle()
    top.run_all()


if __name__ == "__main__":
    # top = ChipTop()
    # top.build()
    # top.load_dict('inst/')
    # top.run()
    chip_test()