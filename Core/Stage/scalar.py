

# from Core.Stage.Storage.regFile import
from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase


class Scalar(StageBase):
    def __init__(self,reg_file:RegFile):
        super(Scalar, self).__init__()

        self.reg_file = reg_file
        self.current_eu = None

    def ticktock(self):
        self.add_cycle_cnt()
        self.compute_cycle_energy()

        if self.current_eu == 'seu':
            self.scalar_excute()

    def update(self):
        self.current_eu = self.recv_data['eu']
        self.stage_data = self.recv_data['inst']

    def stall_out(self):
        return None

    def compute_cycle_energy(self):
        pass

    def scalar_excute(self):
        rd = self.stage_data.rd
        rs1 = self.stage_data.rs1
        rs2 = self.stage_data.rs2
        imm = self.stage_data.imm
        if self.stage_data.op == 'sadd':
            self.reg_file[rd] = self.reg_file[rs1] + self.reg_file[rs2]
        elif self.stage_data.op == 'ssub':
            self.reg_file[rd] = self.reg_file[rs1] - self.reg_file[rs2]
        elif self.stage_data.op == 'smul':
            self.reg_file[rd] = self.reg_file[rs1] * self.reg_file[rs2]
        elif self.stage_data.op == 'sdiv':
            self.reg_file[rd] = self.reg_file[rs1] // self.reg_file[rs2]
        elif self.stage_data.op == 'saddi':
            self.reg_file[rd] = self.reg_file[rs1] + imm
        elif self.stage_data.op == 'ssubi':
            self.reg_file[rd] = self.reg_file[rs1] - imm
        elif self.stage_data.op == 'smuli':
            self.reg_file[rd] = self.reg_file[rs1] * imm