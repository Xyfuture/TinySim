from Core.Instruction.inst import instruction
from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.misc import ExecInfo
from Core.Utils.reg import Register
from Core.Stage.stall import StallEvent
from Core.PipeLine.packet import InnerPacket

class Transfer(StageBase):
    REG_TRANSFER = ['ld','st','sti','ldi']
    CORE_TRANSFER = ['send','recv']
    def __init__(self):
        super(Transfer, self).__init__()
        self.level = 5

        self.stage_reg.info = ExecInfo(eu='none', inst=instruction())
        self.stage_reg.current_eu = 'none'


        self.inner_reg = Register('neg')
        self.inner_reg.busy_cycle = 0
        self.inner_reg.state = 'idle'
        # 记录一下当前的传输是否已经结束
        self.inner_reg.transfer_unfinished = False

        # self.stall_event = None
        # self.stall_reg = Register()
        # self.stall_reg.stalled = False

    # def _ticktock(self):
    #     if self.inner_reg.state == 'idle':
    #         if self.current_eu == 'dtu':
    #             if self.stage_data.op in self.REG_TRANSFER:
    #                 self.process()
    #             elif self.stage_data.op in self.CORE_TRANSFER:
    #                 cycles = self.set_busy_cycle()
    #                 self.inner_reg.busy_cycles = cycles
    #                 self.state = 'busy'
    #
    #                 if self.stage_data.op == 'send':
    #                     # send应该先读取数据，因此先进行wait cycle才行，这里是不对的
    #                     pass
    #                 elif self.stage_data.op == 'recv':
    #                     dest_id = self.stage_data.imm
    #                     data_size = self.info.rs2_value
    #                     tmp_recv_request = InnerPacket(dest_id,data_size,self.recv_callback,'recv')
    #                     self.gateway.inner_recv_request(tmp_recv_request)
    #                     self.transfer_state = 'start'
    #                     self.inner_reg.transfer_unfinished = True # 开始等待从传输结束
    #
    #     if self.inner_reg.state == 'busy':
    #         # send模式下先循环busy—cycles，模拟读取内存数据，然后等待异步的gateway调用
    #         if self.stage_data.op == 'send':
    #             if self.inner_reg.busy_cycles > 0:
    #                 self.inner_reg.busy_cycles = self.inner_reg.busy_cycles-1
    #             else:
    #                 if not self.inner_reg.transfer_unfinished:
    #                     # 还没有开始传输数据
    #                     self.inner_reg.transfer_unfinished = True
    #                     # 向外发出包
    #                     dest_id = self.stage_data.imm
    #                     data_size = self.info.rs2_value
    #                     tmp_send_request = InnerPacket(dest_id,data_size,self.send_callback)
    #                     self.gateway.inner_send_request(tmp_send_request)
    #                     self.transfer_state = 'start'
    #                 else:
    #                     if self.transfer_state == 'finish':
    #                         # 此时传输结束
    #                         self.inner_reg.transfer_unfinished = False
    #                         self.transfer_state = 'idle' # 重新进入待机状态
    #                         self.inner_reg.state = 'idle'
    #         elif self.stage_data.op == 'recv':
    #             if self.inner_reg.transfer_unfinished:
    #                 if self.transfer_state == 'finish':
    #                     self.inner_reg.transfer_unfinished = False
    #                     self.transfer_state = 'idle'
    #                 else:
    #                     # 外部传输已经结束，转入到内部的传输
    #                     if self.inner_reg.busy_cycles > 0:
    #                         self.inner_reg.busy_cycles = self.inner_reg.busy_cycles -1
    #                     else:
    #                         self.inner_reg.state = 'idle'
    # # def pos_tick(self):
    # #
    # #     self.compute_cycle_energy()
    # #     self.add_cycle_cnt()
    # #
    # #
    # #     self.inner_reg.update()
    #
    #
    # def posedge(self):
    #     if self.check_not_stalled():
    #         if self.inner_reg.state =='idle':
    #             self.current_eu,self.stage_data = self.recv_data['eu'],self.recv_data['inst']
    #             self.info = self.recv_data
    #
    #
    #
    # def negedge(self):
    #     self.stall_event = None
    #
    #     if self.stall_reg.stalled:
    #         if self.inner_reg.state == 'idle':
    #             self.stall_event = StallEvent("DataTransferUnit",False)
    #             self.stall_reg.stalled = False
    #     else:
    #         if self.inner_reg.state == 'busy':
    #             bypass_info = self.bypass_pre_stage_list[0].bypass_ticktock()
    #             eu,inst = bypass_info['eu'],bypass_info['inst']
    #             if eu == 'dtu':
    #                 self.stall_reg.stalled = True
    #                 self.stall_event =  StallEvent("DataTransferUnit",True)
    #
    #     self.stall_reg.update()
    #     return self.stall_event
    #
    # def _ticktock(self):
    #     if self.inner_reg.state == 'idle':
    #         if self.current_eu == 'dtu':
    #             if self.stage_data.op in self.REG_TRANSFER:
    #                 self.process()
    #             elif self.stage_data.op in self.CORE_TRANSFER:
    #                 cycles = self.set_busy_cycle()
    #                 self.inner_reg.busy_cycles = cycles
    #                 self.state = 'busy'
    #
    #                 if self.stage_data.op == 'send':
    #                     # send应该先读取数据，因此先进行wait cycle才行，这里是不对的
    #                     pass
    #                 elif self.stage_data.op == 'recv':
    #                     dest_id = self.stage_data.imm
    #                     data_size = self.info.rs2_value
    #                     tmp_recv_request = InnerPacket(dest_id,data_size,self.recv_callback,'recv')
    #                     self.gateway.inner_recv_request(tmp_recv_request)
    #                     self.transfer_state = 'start'
    #                     self.inner_reg.transfer_unfinished = True # 开始等待从传输结束
    #
    #     if self.inner_reg.state == 'busy':
    #         # send模式下先循环busy—cycles，模拟读取内存数据，然后等待异步的gateway调用
    #         if self.stage_data.op == 'send':
    #             if self.inner_reg.busy_cycles > 0:
    #                 self.inner_reg.busy_cycles = self.inner_reg.busy_cycles-1
    #             else:
    #                 if not self.inner_reg.transfer_unfinished:
    #                     # 还没有开始传输数据
    #                     self.inner_reg.transfer_unfinished = True
    #                     # 向外发出包
    #                     dest_id = self.stage_data.imm
    #                     data_size = self.info.rs2_value
    #                     tmp_send_request = InnerPacket(dest_id,data_size,self.send_callback)
    #                     self.gateway.inner_send_request(tmp_send_request)
    #                     self.transfer_state = 'start'
    #                 else:
    #                     if self.transfer_state == 'finish':
    #                         # 此时传输结束
    #                         self.inner_reg.transfer_unfinished = False
    #                         self.transfer_state = 'idle' # 重新进入待机状态
    #                         self.inner_reg.state = 'idle'
    #         elif self.stage_data.op == 'recv':
    #             if self.inner_reg.transfer_unfinished:
    #                 if self.transfer_state == 'finish':
    #                     self.inner_reg.transfer_unfinished = False
    #                     self.transfer_state = 'idle'
    #                 else:
    #                     # 外部传输已经结束，转入到内部的传输
    #                     if self.inner_reg.busy_cycles > 0:
    #                         self.inner_reg.busy_cycles = self.inner_reg.busy_cycles -1
    #                     else:
    #                         self.inner_reg.state = 'idle'
    # # def pos_tick(self):
    # #
    # #     self.compute_cycle_energy()
    # #     self.add_cycle_cnt()
    # #
    # #
    # #     self.inner_reg.update()
    #
    #
    # def posedge(self):
    #     if self.check_not_stalled():
    #         if self.inner_reg.state =='idle':
    #             self.current_eu,self.stage_data = self.recv_data['eu'],self.recv_data['inst']
    #             self.info = self.recv_data
    #
    #
    #
    # def negedge(self):
    #     self.stall_event = None
    #
    #     if self.stall_reg.stalled:
    #         if self.inner_reg.state == 'idle':
    #             self.stall_event = StallEvent("DataTransferUnit",False)
    #             self.stall_reg.stalled = False
    #     else:
    #         if self.inner_reg.state == 'busy':
    #             bypass_info = self.bypass_pre_stage_list[0].bypass_ticktock()
    #             eu,inst = bypass_info['eu'],bypass_info['inst']
    #             if eu == 'dtu':
    #                 self.stall_reg.stalled = True
    #                 self.stall_event =  StallEvent("DataTransferUnit",True)
    #
    #     self.stall_reg.update()
    #     return self.stall_event
    #

    def compute_cycle_energy(self):
        pass

    def set_busy_cycle(self):
        return 5


    def send_callback(self):
        # self.transfer_state = 'finish'
        pass

    def recv_callback(self):
        # self.transfer_state = 'finish'
        pass

    # def bypass_ticktock(self):
    #     self._ticktock()
    #     if self.inner_reg.value['state'] == 'busy' and self.inner_reg.next_value['state'] == 'idle':
    #         if self.stage_data.op == 'recv':
    #             return (self.info.rs1_addr,self.info.rs1_addr + self.info.length)
    #     return None


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