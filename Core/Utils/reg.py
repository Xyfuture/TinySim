import copy

# 模拟实现寄存器的功能
class Register:
    def __init__(self):
        self.value = {}
        self.next_value = {}


    def __setattr__(self, key, value):
        if key not in self.value:
            self.value[key] = value
            self.next_value[key] = value
        else:
            self.next_value[key] = value
        
    def __getattribute__(self, item):
        return self.value[item]

    def update(self):
        self.value = copy.deepcopy(self.next_value)