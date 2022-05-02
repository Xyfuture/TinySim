import math

from NoC.base import NoCBase, PendingEvent
from NoC.packet import DataPacket


# 10Gbps on Chip Router
# 2byte/ns cycle

class BlockedNoc(NoCBase):
    def __init__(self,mesh_layout):
        super(BlockedNoc, self).__init__(mesh_layout)

        self.switch_bandwidth = 2 # byte/ns

        pass

    def manhattan_distance(self,src_id,dst_id):
        src_r,src_c = src_id//self.mesh_column, src_id%self.mesh_column
        dst_r,dst_c = dst_id//self.mesh_column, dst_id%self.mesh_column

        distance = abs(src_c - dst_c) + abs(src_r-dst_r)

        return distance



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
        return 0

    def compute_transfer_latency(self,packet:DataPacket):
        data_size = packet.packet_size
        src_id,dst_id = packet.source_id,packet.dest_id
        distance_latency = self.manhattan_distance(src_id,dst_id)
        transfer_latency = math.ceil(data_size/self.switch_bandwidth)

        return distance_latency + transfer_latency



