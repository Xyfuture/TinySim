from collections import OrderedDict
from abc import ABCMeta,abstractmethod

from Core.Instruction.inst import instruction


# 在这个里面不仅记录了每个stage传输的信息还记录了各个stage之间的连接关系
# 遍历应该遵循bfs的顺序，不能直接在这个类里面实现
from Core.Utils.reg import Register
from Core.Utils.stall import StallEvent


class StageBase(metaclass=ABCMeta):
    def __init__(self):
        self._neg_regs = []
        self._pos_regs = []

        self.stage_reg = Register()

        self.stage_reg.stage_data = instruction()
        # self.stage_reg.recv_data = instruction()
        # self.stage_reg.send_data = instruction()


        # 本身用于记录的信息 （其实也应该弄成另一个类）
        self.total_energy = 0
        self.total_cycles = 0
        self.stall_cycles = 0

        # 构建连接关系
        self.pre_stage_list = [] # 构建连接关系
        self.post_stage_list = []

        self.bypass_pre_stage_list = []

        # self.stall_info_dict = OrderedDict()

        # 与外部连接的网关
        self.gateway = None

        # stall 引擎
        self.stall_engine = None


    def __setattr__(self, key, value):
        if isinstance(value,Register):
            if value.clock == 'neg':
                self._neg_regs.append(value)
            elif value.clock == 'pos':
                self._pos_regs.append(value)

        super(StageBase, self).__setattr__(key,value)


    @abstractmethod
    def set_pos_reg(self):
        pass

    # 时钟的上升沿,更新上升沿的数据
    def posedge(self):
        for reg in self._pos_regs:
            reg.update()

    # 建议进行其他的处理，不进行流水线相关的
    def pos_tick(self):
        pass

    # 这个可能没有
    def set_neg_reg(self):
        pass

    # 时钟的下降沿，更新下降沿的数据
    def negedge(self):
        for reg in self._neg_regs:
            reg.update()

    # 进行其他的处理
    def neg_tick(self):
        pass


    # 输出的数据，组合逻辑电路
    @property
    @abstractmethod
    def send_data(self):
        pass

    # 实际上是一个组合电路，应该声明为property，但受限于python，定义为函数
    @abstractmethod
    def stall_info(self):
        pass


    # 计算一个周期或者多个周期的功耗
    @abstractmethod
    def compute_cycle_energy(self):
        pass



    # 构建连接关系
    def connect_to(self,*pre_stages):
        for stage in pre_stages:
            self.pre_stage_list.append(stage)
            stage.add_post_stage(self)

    def add_pre_stage(self,s):
        self.pre_stage_list.append(s)

    def add_post_stage(self,s):
        self.post_stage_list.append(s)

    def compute_total_energy(self):
        return self.total_energy

    def add_cycle_cnt(self):
        self.total_cycles += 1



    # 与Core外进行数据传输
    def set_gateway(self,g):
        self.gateway = g

    def bypass_connect_to(self,*pre_stages):
        for stage in pre_stages:
            self.bypass_pre_stage_list.append(stage)
            # 这个不维持完整的连接了，只保证后面的可以连接到前面的。

    # uncertain
    def set_stall_engine(self,engine):
        self.stall_engine = engine
        pass