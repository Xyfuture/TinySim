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
        self.compute_energy = 40400*16 # pJ mW * nS

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
            if self.stage_reg.stage_data.op == 'gemv' and cur_packet_id == self.packet_id:
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
        if self.stage_reg.stage_data.op == 'gemv' and self.state == 'idle' and cur_packet_id == self.packet_id:
            start_addr = self.stage_reg.info.write_start_addr
            length = self.stage_reg.info.length

            if start_addr:
                interval = (start_addr,start_addr+length-1)

        return interval

    @property
    def fifo_cnt(self):
        cur_packet_id = self.stage_reg.info.rd_value
        if self.stage_reg.stage_data.op == 'gemv' and self.state == 'idle' and cur_packet_id == self.packet_id:
            # print('finish one window')
            return 1
        return 0


    def stall_info(self):
        if self.state == 'busy':
            info = self.pre_stage_list[0].send_data
            if info['inst'].op == 'gemv' and info['rd_value'] == self.packet_id:
                return StallEvent("MatrixExecuteUnit",self.level)
        return None

    def compute_dynamic_energy(self):
        # data_size = self.stage_reg.info.rs2_value
        if self.stage_reg.stage_data.op == 'gemv':
            self.dynamic_energy += self.meu_num * self.compute_energy


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
              'busy_cycle:{}\n'.format(self.packet_id,self.stage_reg.stage_data.dump_asm(),self.stall_engine.check_stall(self.level),self.inner_reg.busy_cycle))






class MatrixGVR(StageBase):
    def __init__(self,packet_id,meu_num,scratchpad):
        super(MatrixGVR, self).__init__()
        self.level = 5
        self.packet_id = packet_id
        self.meu_num = meu_num
        self.scratchpad = scratchpad

        self.stage_reg.info = ExecInfo(eu='none', inst=instruction())
        self.stage_reg.current_eu = 'none'
        self.stage_reg.fifo_cnt = 0

        self.inner_reg = Register('neg')
        self.inner_reg.busy_cycle = 0
        self.inner_reg.read_fifo = 0

    def set_pos_reg(self):
        for stage in self.bypass_pre_stage_list:
            cur_fifo_cnt = self.stage_reg.fifo_cnt
            add_fifo_cnt = stage.fifo_cnt
            sub_fifo_cnt = self.inner_reg.read_fifo
            #
            # if add_fifo_cnt == 1:
            #     print('get 1')
            # if sub_fifo_cnt == 1:
            #     print('release 1')

            self.stage_reg.fifo_cnt = cur_fifo_cnt + add_fifo_cnt - sub_fifo_cnt


        if self.state == 'idle':
            tmp = self.pre_stage_list[0].send_data
            self.stage_reg.info = tmp
            self.stage_reg.current_eu, self.stage_reg.stage_data = tmp['eu'], tmp['inst']

    def pos_tick(self):
        self.add_cycle_cnt()
        # self.compute_dynamic_energy()

    def set_neg_reg(self):
        self.inner_reg.read_fifo = 0
        if self.state == 'busy':
            self.inner_reg.busy_cycle = self.inner_reg.busy_cycle -1
            if self.inner_reg.busy_cycle == 1:
                self.inner_reg.read_fifo = 1 # 去掉该队列内容
        elif self.state == 'idle':
            cur_packet_id = self.stage_reg.info.rd_value
            if self.stage_reg.stage_data.op == 'gvr' and cur_packet_id == self.packet_id:
                self.inner_reg.busy_cycle = self.set_busy_cycle()



    @property
    def send_data(self):
        return  0

    @property
    def state(self):
        if self.stage_reg.stage_data.op == 'gvr' and self.stage_reg.info.rd_value == self.packet_id and self.stage_reg.fifo_cnt < 1:
            return 'wait'

        if self.inner_reg.busy_cycle > 0:
            return 'busy'
        else:
            return 'idle'

    @property
    def finish_interval(self):
        interval = None

        # if self.stage_reg.finish:
        cur_packet_id = self.stage_reg.info.rd_value
        if self.stage_reg.stage_data.op == 'gvr' and self.state == 'idle' and cur_packet_id == self.packet_id:
            start_addr = self.stage_reg.info.write_start_addr
            length = self.stage_reg.info.length

            if start_addr:
                interval = (start_addr,start_addr+length-1)


        return interval

    def stall_info(self):
        if  self.state == 'wait':
            info = self.pre_stage_list[0].send_data
            if info['inst'].op == 'gvr' and info['rd_value'] == self.packet_id:
                print('here')


        if self.state == 'busy' or self.state == 'wait':
            info = self.pre_stage_list[0].send_data
            if info['inst'].op == 'gvr' and info['rd_value'] == self.packet_id:
                return StallEvent("MatrixGVRUnit",self.level)
        return None

    def compute_dynamic_energy(self):
        pass

    def compute_leakage_energy(self):
        pass

    def compute_total_energy(self):
        return 0

    def set_busy_cycle(self):
        # 在这里处理访存相关的事宜
        # self.compute_dynamic_energy()
        if self.stage_reg.stage_data.op == 'gvr':
            write_size = self.stage_reg.info.rs2_value
            write_latency = self.scratchpad.read_mem(write_size)
            return write_latency

        return 0


    def dump_info(self):
        return ('MatrixGVR_packet_id_{}:\n'
              'inst:{}\n'
              'stall:{}\n'
              'busy_cycle:{}\n'.format(self.packet_id,self.stage_reg.stage_data.dump_asm(),self.stall_engine.check_stall(self.level),self.inner_reg.busy_cycle))





class Matrix(StageBase):
    def __init__(self,pipeline,scratchpad):
        super(Matrix, self).__init__()
        self.level = 5

        self.stage_reg.info = ExecInfo(eu='none', inst=instruction())
        self.stage_reg.current_eu = 'none'

        self.meu_dict = OrderedDict()
        self.meu_gvr_dict = OrderedDict()

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

            fifo_cnt = [0]

            tmp_meu = MatrixGroup(packet_id, num, self.scratchpad)
            tmp_meu.set_stall_engine(self.stall_engine)
            self.meu_dict[packet_id] = tmp_meu

            tmp_meu_gvr = MatrixGVR(packet_id, num, self.scratchpad)
            tmp_meu_gvr.set_stall_engine(self.stall_engine)
            self.meu_gvr_dict[packet_id] = tmp_meu_gvr

            tmp_meu_gvr.bypass_connect_to(tmp_meu)

            for stage in self.pre_stage_list:
                tmp_meu.connect_to(stage)
                tmp_meu.bypass_connect_to(stage)
                stage.bypass_connect_to(tmp_meu)

                tmp_meu_gvr.connect_to(stage)
                stage.bypass_connect_to(tmp_meu_gvr)


            for stage in self.post_stage_list:
                stage.connect_to(tmp_meu)
                stage.connect_to(tmp_meu_gvr)

            self.pipeline.__setattr__("meu_packet_id_{}".format(packet_id),tmp_meu)
            self.pipeline.__setattr__("meu_gvr_packet_id_{}".format(packet_id),tmp_meu_gvr)


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
