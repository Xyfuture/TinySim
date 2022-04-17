

from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.reg import Register
from Core.Utils.stall import StallEvent
from Core.PipeLine.packet import InnerPacket

class Transfer(StageBase):
    REG_TRANSFER = ['ld','st','sti','ldi']
    CORE_TRANSFER = ['send','recv']
    def __init__(self,reg_file:RegFile):
        super(Transfer, self).__init__()
        self.info = None


        self.reg_file = reg_file
        self.current_eu = None

        self.inner_reg = Register()
        # self.inner_reg.stalled = False
        self.inner_reg.busy_cycle = 0
        self.inner_reg.state = 'idle'
        # 记录一下当前的传输是否已经结束
        self.inner_reg.transfer_unfinished = False

        self.stall_event = None
        self.stall_reg = Register()
        self.stall_reg.stalled = False

        #异步的完成信号
        self.transfer_state = 'idle' # 'idle' 'start' 'finish'


    def ticktock(self):

        self.compute_cycle_energy()
        self.add_cycle_cnt()

        if self.inner_reg.state == 'idle':
            if self.current_eu == 'dtu':
                if self.stage_data.op in self.REG_TRANSFER:
                    self.process()
                elif self.stage_data.op in self.CORE_TRANSFER:
                    cycles = self.set_busy_cycle()
                    self.inner_reg.busy_cycles = cycles
                    self.state = 'busy'

                    if self.stage_data.op == 'send':
                        # send应该先读取数据，因此先进行wait cycle才行，这里是不对的
                        pass
                    elif self.stage_data.op == 'recv':
                        dest_id = self.stage_data.imm
                        data_size = self.reg_file[self.stage_data.rs2]
                        tmp_recv_request = InnerPacket(dest_id,data_size,self.recv_callback,'recv')
                        self.gateway.inner_recv_request(tmp_recv_request)
                        self.transfer_state = 'start'
                        self.inner_reg.transfer_unfinished = True # 开始等待从传输结束

        if self.inner_reg.state == 'busy':
            # send模式下先循环busy—cycles，模拟读取内存数据，然后等待异步的gateway调用
            if self.stage_data.op == 'send':
                if self.inner_reg.busy_cycles > 0:
                    self.inner_reg.busy_cycles = self.inner_reg.busy_cycles-1
                else:
                    if not self.inner_reg.transfer_unfinished:
                        # 还没有开始传输数据
                        self.inner_reg.transfer_unfinished = True
                        # 向外发出包
                        dest_id = self.stage_data.imm
                        data_size = self.reg_file[self.stage_data.rs2]
                        tmp_send_request = InnerPacket(dest_id,data_size,self.send_callback)
                        self.gateway.inner_send_request(tmp_send_request)
                        self.transfer_state = 'start'
                    else:
                        if self.transfer_state == 'finish':
                            # 此时传输结束
                            self.inner_reg.transfer_unfinished = False
                            self.transfer_state = 'idle' # 重新进入待机状态
                            self.inner_reg.state = 'idle'
            elif self.stage_data.op == 'recv':
                if self.inner_reg.transfer_unfinished:
                    if self.transfer_state == 'finish':
                        self.inner_reg.transfer_unfinished = False
                        self.transfer_state = 'idle'
                    else:
                        # 外部传输已经结束，转入到内部的传输
                        if self.inner_reg.busy_cycles > 0:
                            self.inner_reg.busy_cycles = self.inner_reg.busy_cycles -1
                        else:
                            self.inner_reg.state = 'idle'

        self.inner_reg.update()


    def update(self):
        if self.check_not_stalled():
            if self.inner_reg.state =='idle':
                self.current_eu,self.stage_data = self.recv_data['eu'],self.recv_data['inst']
                self.info = self.recv_data



    def stall_out(self):
        self.stall_event = None

        if self.stall_reg.stalled:
            if self.inner_reg.state == 'idle':
                self.stall_event = StallEvent("DataTransferUnit",False)
                self.stall_reg.stalled = False
        else:
            if self.inner_reg.state == 'busy':
                bypass_info = self.bypass_pre_stage_list[0].bypass_ticktock()
                eu,inst = bypass_info['eu'],bypass_info['inst']
                if eu == 'dtu':
                    self.stall_reg.stalled = True
                    self.stall_event =  StallEvent("DataTransferUnit",True)

        self.stall_reg.update()
        return self.stall_event


    def compute_cycle_energy(self):
        pass

    def set_busy_cycle(self):
        return 1

    def process(self):
        if self.stage_data.op == 'ldi':
            self.reg_file[self.stage_data.rd] = self.stage_data.imm
        else:
            pass # 其他暂时不支持，除非实现mem的功能（后续考虑吧

    def send_callback(self):
        self.transfer_state = 'finish'

    def recv_callback(self):
        self.transfer_state = 'finish'

    def bypass_ticktock(self):
        pass # hard to do