from abc import ABCMeta,abstractmethod

from Core.PipeLine.packet import InnerPacket
from NoC.packet import DataPacket



class GatewayBase(metaclass=ABCMeta):
    def __init__(self,bus,gateway_id):
        self.bus = bus
        self.gateway_id = gateway_id

    # 内部想要发送什么数据
    @abstractmethod
    def inner_send_request(self,request):
        pass

    # 内部想要接收什么数据
    @abstractmethod
    def inner_recv_request(self,request):
        pass
    # 实现发送和接收后都要提供一个回调函数保证数据传输完成

    # @abstractmethod
    # def inner_send_handler(self,request):
    #     pass
    #
    # @abstractmethod
    # def inner_recv_handler(self,request):
    #     pass

    # 数据由gateway向外发送
    @abstractmethod
    def outer_send_request(self,packet=None):
        pass

    # @abstractmethod
    # def outer_recv_request(self):
    #     pass
    #
    # @abstractmethod
    # def outer_send_handler(self,):
    #     pass

    # 收到数据包应该的操作
    @abstractmethod
    def outer_recv_handler(self,packet):
        pass


    @abstractmethod
    def outer_send_finish(self,packet):
        pass

    @abstractmethod
    def outer_recv_finish(self,packet):
        pass



class BlockedGateway(GatewayBase):
    def __init__(self,bus,gateway_id):
        super(BlockedGateway, self).__init__(bus,gateway_id)
        self.wait_send_packet = None
        self.wait_recv_packet = None

        self.dest_ready ={}

    def inner_send_request(self,request:InnerPacket):
        assert not self.wait_send_packet
        self.wait_send_packet = request

        # 检测是否能直接发送，不能的话就直接跳出，等到收到ready再说
        self.inner_check_ready_send()

    def inner_check_ready_send(self):
        request = self.wait_send_packet
        if not request: #没有需要发送的数据时直接退出
            return
        if self.dest_ready.get(request.dest_id):
            tmp_packet = DataPacket(self.gateway_id, request.dest_id, request.packet_size, 'data')
            self.outer_send_request(tmp_packet)
            self.dest_ready[request.dest_id] = False
            # 清除的工作交给finish函数操作


    def inner_recv_request(self,request):
        assert not self.wait_recv_packet
        self.wait_recv_packet = request

        tmp_ready_packet = DataPacket(self.gateway_id,request.dest_id,-1,"ready")
        self.outer_send_request(tmp_ready_packet)


    def outer_send_request(self,packet=None):
        self.bus.send(packet) # 直接发出去就完了


    # 刚刚收到数据数据时的操作
    def outer_recv_handler(self,packet:DataPacket):
        if packet.payload == 'data':
            assert self.wait_recv_packet
        elif packet.payload == 'ready':
            pass # 在finish部分进行处理了

    # 数据接收完毕
    def outer_recv_finish(self,packet:DataPacket):
        if packet.payload == 'data':
            assert self.wait_recv_packet
            self.wait_recv_packet.call_back()
            self.wait_recv_packet = None # 完成接收

        elif packet.payload == 'ready':
            self.dest_ready[packet.source_id] = True
            self.inner_check_ready_send()

    def outer_send_finish(self,packet:DataPacket):
        if packet.payload == 'data':
            # 自身发送了数据，因此需要设置wait_send_request
            assert self.wait_send_packet
            self.wait_send_packet.call_back()
            self.wait_send_packet = None
        elif packet.payload == 'ready':
            assert self.wait_recv_packet
            # 只有设置类wait_recv_packet之后才能发ready