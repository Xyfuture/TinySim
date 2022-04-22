import copy

# 模拟实现寄存器的功能
class Register:
    def __init__(self):
        self.value = {}
        self.next_value = {}


    def __setattr__(self, key, value):
        # print('setattr')
        # print(key)
        if key == 'value' or key == 'next_value':
            super(Register, self).__setattr__(key,value)
        else:
            if key not in self.value:
                self.value[key] = value
                self.next_value[key] = value
            else:
                self.next_value[key] = value
        
    def __getattribute__(self, item):
        value = super(Register, self).__getattribute__('value')
        # next_value = super(Register, self).__getattribute__('next_value')

        if item in value:
            return value[item]

        return super(Register, self).__getattribute__(item)

    def update(self):
        self.value = copy.deepcopy(self.next_value)