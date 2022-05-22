

# from Core.Stage.Storage.regFile import
from Core.Instruction.inst import instruction
from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase

# 加上 寄存器的功耗


class Scalar(StageBase):
    def __init__(self,reg_file:RegFile):
        super(Scalar, self).__init__()
        self.level = 4

        self.reg_file = reg_file
        self.stage_reg.current_eu = 'none'

        self.dynamic_per_energy = 0 # 暂时没有计算
        self.leakage_per_energy = 1.1171



    def set_pos_reg(self):
        if self.stall_engine.check_not_stall(self.level):
            recv_data = self.pre_stage_list[0].send_data
            self.stage_reg.current_eu,self.stage_reg.stage_data = recv_data['eu'],recv_data['inst']





    def pos_tick(self):
        self.add_cycle_cnt()
        self.compute_dynamic_energy()

        if self.stage_reg.current_eu == 'seu':
            self.scalar_execute()

    def stall_info(self):
        return None

    @property
    def send_data(self):
        return 0

    def compute_dynamic_energy(self):
        if self.stage_reg.current_eu == 'seu':
            self.dynamic_energy += self.dynamic_per_energy

    def compute_leakage_energy(self):
        self.leakage_energy = self.leakage_per_energy * self.total_cycles

    def scalar_execute(self):
        stage_data = self.stage_reg.stage_data
        
        
        rd = stage_data.rd
        rs1 = stage_data.rs1
        rs2 = stage_data.rs2
        imm = stage_data.imm
        if stage_data.op == 'sadd':
            self.reg_file[rd] = self.reg_file[rs1] + self.reg_file[rs2]
        elif stage_data.op == 'ssub':
            self.reg_file[rd] = self.reg_file[rs1] - self.reg_file[rs2]
        elif stage_data.op == 'smul':
            self.reg_file[rd] = self.reg_file[rs1] * self.reg_file[rs2]
        elif stage_data.op == 'sdiv':
            self.reg_file[rd] = self.reg_file[rs1] // self.reg_file[rs2]
        elif stage_data.op == 'saddi':
            self.reg_file[rd] = self.reg_file[rs1] + imm
        elif stage_data.op == 'ssubi':
            self.reg_file[rd] = self.reg_file[rs1] - imm
        elif stage_data.op == 'smuli':
            self.reg_file[rd] = self.reg_file[rs1] * imm

        # load-store 指令
        if stage_data.op == 'ldi':
            self.reg_file[rd] = imm
        # 其他几个暂时不考虑执行，否则就是完全模拟了 emmm




    def dump_info(self):
        return ('Scalar:\n'
              'inst:{}\n'
              'stall:{}\n'.format(self.stage_reg.stage_data.dump_asm(), self.stall_engine.check_stall(self.level)))