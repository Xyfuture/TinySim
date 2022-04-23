import copy

# 模拟实现寄存器的功能
class Register(object):
    def __init__(self,clock='pos'):
        self.clock = clock
        self.value = {}
        self.next_value = {}


    def __setattr__(self, key, value):
        # print('setattr')
        # print(key)
        if key == 'value' or key == 'next_value':
            self.__dict__[key] = value
        elif key == 'clock':
            self.__dict__[key] = value
        else:
            if key not in self.value:
                self.value[key] = value
                self.next_value[key] = value
            else:
                self.next_value[key] = value
        
    def __getattr__(self, item):
        if item in self.value:
            return self.value[item]
        raise AttributeError(item)

    def update(self):
        for key  in self.value:
            self.value[key] = self.next_value[key]
