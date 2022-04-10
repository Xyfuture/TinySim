# 暂时可能用不到这个



class RegFile:
    def __init__(self):
        self.reg_file = [0 for i in range(32)]

    def __getitem__(self, item):
        if item == 0:
            return 0
        return self.reg_file[item]

    def __setitem__(self, key, value):
        if key == 0:
            return
        self.reg_file[key] = value

