from Core.Instruction.inst import instruction
from Core.Stage.Storage.mem import ScratchPad
from Core.Stage.base import StageBase
from Core.Utils.misc import ExecInfo
from Core.Utils.reg import Register
from Core.Stage.stall import StallEvent
from Core.PipeLine.packet import InnerPacket

class Transfer(StageBase):
    REG_TRANSFER = ['ld','st','sti','ldi']
    CORE_TRANSFER = ['send','recv']
    def __init__(self,scratchpad):
        super(Transfer, self).__init__()
        self.level = 5
        self.scratchpad = scratchpad

        self.stage_reg.info = ExecInfo(eu='none', inst=instruction())
        self.stage_reg.current_eu = 'none'


        self.inner_reg = Register('neg')
        self.inner_reg.busy_cycle = 0
        self.inner_reg.state = 'idle'
        # 记录一下当前的传输是否已经结束
        self.inner_reg.transfer_unfinished = False

    def compute_dynamic_energy(self):
        pass

    def compute_leakage_energy(self):
        pass

    def set_busy_cycle(self):
        self.compute_dynamic_energy()

        if self.stage_reg.stage_data.op == 'send':
            data_size = self.stage_reg.info.rs2_value
            read_latency = self.scratchpad.read_mem(data_size)
            return read_latency
        elif self.stage_reg.stage_data.op == 'recv':
            data_size = self.stage_reg.info.rs2_value
            write_latency = self.scratchpad.write_mem(data_size)
            return write_latency

        return 0


    def send_callback(self):
        # self.transfer_state = 'finish'
        pass

    def recv_callback(self):
        # self.transfer_state = 'finish'
        pass



    def set_pos_reg(self):
        if self.state == 'idle':
            tmp = self.pre_stage_list[0].send_data
            self.stage_reg.info = tmp
            self.stage_reg.current_eu,self.stage_reg.stage_data = tmp['eu'],tmp['inst']





    def pos_tick(self):
        inst = self.stage_reg.stage_data
        info = self.stage_reg.info
        if self.state == 'idle':
            if self.stage_reg.stage_data.op == 'recv':
                dest_id = inst.imm
                data_size = info.rs2_value
                tmp_recv_request = InnerPacket(dest_id,data_size,self.recv_callback)
                self.gateway.inner_recv_request(tmp_recv_request)

        elif self.state == 'busy':
            if self.stage_reg.stage_data.op == 'send':
                if self.inner_reg.busy_cycle == 0 and self.transfer_state == 'idle':
                    dest_id = inst.imm
                    data_size = info.rs2_value
                    tmp_send_request = InnerPacket(dest_id,data_size,self.send_callback)
                    self.gateway.inner_send_request(tmp_send_request)





    def set_neg_reg(self):
        if self.state == 'idle':
            if self.stage_reg.stage_data.op == 'send':
                self.inner_reg.busy_cycle = self.set_busy_cycle()
                self.inner_reg.transfer_unfinished = True
            elif self.stage_reg.stage_data.op == 'recv':
                self.inner_reg.transfer_unfinished = True

        elif self.state == 'busy':
            if self.stage_reg.stage_data.op == 'send':
                if self.inner_reg.busy_cycle > 0:
                    self.inner_reg.busy_cycle = self.inner_reg.busy_cycle -1
                if self.inner_reg.busy_cycle == 0  :
                    if self.transfer_state == 'finish':
                        self.inner_reg.transfer_unfinished = False
                        self.reset_transfer_state()
            elif self.stage_reg.stage_data.op == 'recv':

                if self.transfer_state == 'finish':
                    self.inner_reg.busy_cycle = self.set_busy_cycle()
                    self.reset_transfer_state()
                elif self.transfer_state == 'idle':
                    if self.inner_reg.busy_cycle > 0:
                        self.inner_reg.busy_cycle = self.inner_reg.busy_cycle-1

                    if self.inner_reg.busy_cycle <= 1:
                        self.inner_reg.transfer_unfinished = False


    # def neg_tick(self):
    #     if self.stage_reg.stage_data.op == 'send':
    #         print('send:'+self.state)
    #         print('inst:'+self.stage_reg.stage_data.dump_asm())
    #     if self.stage_reg.stage_data.op == 'recv':
    #         print('recv:' + self.state)



    def stall_info(self):
        if self.state == 'busy':
            info = self.pre_stage_list[0].send_data
            if info['eu'] == 'dtu':
                return StallEvent("VectorExecuteUnit", self.level)
        return None


    @property
    def finish_interval(self):
        interval = None
        if self.stage_reg.stage_data.op in ['send','recv']:
            if not self.inner_reg.transfer_unfinished:
                start_addr = self.stage_reg.info.start_addr
                length = self.stage_reg.info.length

                if start_addr:
                    interval = (start_addr,start_addr+length-1)

        return interval


    @property
    def send_data(self):
        return 0


    @property
    def state(self):
        if self.inner_reg.busy_cycle > 0 or self.inner_reg.transfer_unfinished :
            return 'busy'
        else:
            return 'idle'

    @property
    def transfer_state(self):
        return self.gateway.transfer_state

    def reset_transfer_state(self):
        self.gateway.set_idle()


    def dump_info(self):
        return ('Transfer:\n'
              'inst:{}\n'
              'stall:{}\n'
              'busy_cycle:{}\n'.format(self.stage_reg.stage_data.dump_asm(), self.stall_engine.check_stall(self.level),
                                       self.inner_reg.busy_cycle))