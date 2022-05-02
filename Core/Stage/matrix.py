from collections import OrderedDict

from Core.Instruction.inst import instruction
from Core.Stage.Storage.mem import ScratchPad
from Core.Stage.base import StageBase
from Core.Utils.misc import ExecInfo
from Core.Utils.reg import Register
from Core.Stage.stall import StallEvent


class MatrixGroup(StageBase):
    def __init__(self,packet_id,meu_num,scratchpad):
        super(MatrixGroup, self).__init__()
        self.level = 5

        self.packet_id = packet_id
        self.meu_num = meu_num
        self.scratchpad = scratchpad

        self.stage_reg.info = ExecInfo(eu='none', inst=instruction())
        self.stage_reg.current_eu = 'none'

        self.inner_reg = Register('neg')
        self.inner_reg.busy_cycle = 0

        # self.stage_reg.finish = 0

        # 暂时使用固定参数的8bit 乘加运算时间。 不计算访存的时间情况
        self.compute_latency = 1000 # Unit cycle or ns
        self.compute_energy = 40400 # pJ mW * nS

        # 静态功耗低暂时不考虑了。



    def set_pos_reg(self):
        if self.state == 'idle':
            tmp = self.pre_stage_list[0].send_data
            self.stage_reg.info = tmp
            self.stage_reg.current_eu,self.stage_reg.stage_data = tmp['eu'],tmp['inst']

        # if self.inner_reg.busy_cycle == 1:
        #     self.stage_reg.finish = 1
        # else:
        #     self.stage_reg.finish = 0


    def pos_tick(self):
        self.add_cycle_cnt()
        # self.compute_dynamic_energy()



    def set_neg_reg(self):
        if self.state == 'busy':
            self.inner_reg.busy_cycle = self.inner_reg.busy_cycle -1
        elif self.state == 'idle':
            cur_packet_id = self.stage_reg.info.rd_value
            if self.stage_reg.current_eu == 'meu' and cur_packet_id == self.packet_id:
                self.inner_reg.busy_cycle = self.set_busy_cycle()


    @property
    def send_data(self):
        return  0

    @property
    def state(self):
        if self.inner_reg.busy_cycle > 0:
            return 'busy'
        else:
            return 'idle'

    @property
    def finish_interval(self):
        interval = None

        # if self.stage_reg.finish:
        cur_packet_id = self.stage_reg.info.rd_value
        if self.stage_reg.current_eu == 'meu' and self.state == 'idle' and cur_packet_id == self.packet_id:
            start_addr = self.stage_reg.info.write_start_addr
            length = self.stage_reg.info.length

            if start_addr:
                interval = (start_addr,start_addr+length-1)

        return interval


    def stall_info(self):
        if self.state == 'busy':
            info = self.pre_stage_list[0].send_data
            if info['eu'] == 'meu':
                return StallEvent("MatrixExecuteUnit",self.level)
        return None

    def compute_dynamic_energy(self):
        # data_size = self.stage_reg.info.rs2_value
        if self.stage_reg.stage_data.op == 'gemv':
            self.dynamic_energy += self.meu_num * self.compute_energy
        # gvr 没有功耗计算


    def compute_leakage_energy(self):
        # 太小，暂不计算
        pass


    def set_busy_cycle(self):
        # 在这里处理访存相关的事宜
        self.compute_dynamic_energy()

        if self.stage_reg.stage_data.op == 'gemv':
            read_size = self.stage_reg.info.rs2_value
            read_latency = self.scratchpad.read_mem(read_size)
            compute_latency = self.compute_latency

            return read_latency + compute_latency

        elif self.stage_reg.stage_data.op == 'gvr':
            write_size = self.stage_reg.info.rs2_value
            write_latency = self.scratchpad.read_mem(write_size)

            return write_latency

        return 0


    def dump_info(self):
        return ('MatrixGroup_packet_id_{}:\n'
              'inst:{}\n'
              'stall:{}\n'
              'busy_cycle:{}\n'.format(self.packet_id,self.stage_reg.stage_data.op,self.stall_engine.check_stall(self.level),self.inner_reg.busy_cycle))




class Matrix(StageBase):
    def __init__(self,pipeline,scratchpad):
        super(Matrix, self).__init__()
        self.level = 5

        self.stage_reg.info = ExecInfo(eu='none', inst=instruction())
        self.stage_reg.current_eu = 'none'

        self.meu_dict = OrderedDict()

        self.pipeline = pipeline
        self.scratchpad = scratchpad

    def set_pos_reg(self):
        tmp = self.pre_stage_list[0].send_data
        self.stage_reg.info = tmp
        self.stage_reg.current_eu,self.stage_reg.stage_data = tmp['eu'],tmp['inst']



    def pos_tick(self):
        # 这里创建meu，解析一下bind指令
        if self.stage_reg.stage_data.op == 'bind':
            packet_id = self.stage_reg.info.rd_value
            num = self.stage_reg.stage_data.imm

            tmp_meu = MatrixGroup(packet_id, num, self.scratchpad)
            tmp_meu.set_stall_engine(self.stall_engine)
            self.meu_dict[packet_id] = tmp_meu

            for stage in self.pre_stage_list:
                tmp_meu.connect_to(stage)
                # tmp_meu.bypass_connect_to(stage)
                stage.bypass_connect_to(tmp_meu)

            for stage in self.post_stage_list:
                stage.connect_to(tmp_meu)

            self.pipeline.__setattr__("meu_packet_id:".format(packet_id),tmp_meu)


    @property
    def send_data(self):
        return 0

    def stall_info(self):
        return None

    def compute_dynamic_energy(self):
        pass

    def compute_leakage_energy(self):
        pass

    def compute_total_energy(self):
        return 0

    def dump_info(self):
        return ('Matrix:\n'
              'inst:{}\n'
              'stall:{}\n'.format(self.stage_reg.stage_data.dump_asm(),self.stall_engine.check_stall(self.level)))
