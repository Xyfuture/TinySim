


class SimConfig:
    def __init__(self,path=None ):
        self.path = path

        self.meu_cell_bit = 2
        self.meu_rows = 512
        self.meu_columns = 512

        self.meu_cnt = 8
        self.omu_size = 100000000

        self.reg_cnt = 32

        self.mesh_layout = (1,2) # mesh结构下，横向上和竖向上各自有几个核
        self.core_cnt = self.mesh_layout[0] * self.mesh_layout[1]




    def read_config(self,path):
        pass