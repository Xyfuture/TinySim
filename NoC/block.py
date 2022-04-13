

from NoC.base import NoCBase, PendingEvent
from NoC.packet import DataPacket


class BlockNoc(NoCBase):
    def __init__(self):
        super(BlockNoc, self).__init__()
        pass


    def send(self,packet:DataPacket):
        assert packet.dest_id in self.gateway_dict

        dest_gateway = self.gateway_dict[packet.dest_id]
        src_gateway = self.gateway_dict[packet.source_id]

        transfer_latency = self.compute_transfer_latency(packet)
        self.compute_transfer_energy(packet)

        # 暂时不考虑调用recv_handler了，直接调用recv_finish 和 send_finish就行了
        sender_pending_event = PendingEvent(transfer_latency,packet,src_gateway.outer_send_finish)
        recver_pending_event = PendingEvent(transfer_latency,packet,dest_gateway.outer_recv_finish)

        self.pending_event_dict[packet.dest_id].push(recver_pending_event)
        self.pending_event_dict[packet.source_id].push(sender_pending_event)


    def compute_transfer_energy(self,packet:DataPacket):
        pass

    def compute_transfer_latency(self,packet:DataPacket):
        return 1

