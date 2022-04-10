



class DataPacket:
    def __init__(self,source_id,dest_id,packet_size,payload):
        self.source_id = source_id
        self.dest_id = dest_id
        self.packet_size = packet_size # 数据大小，Byte
        self.payload = payload


    @classmethod
    def gen_empty_packet(cls):
        return DataPacket(0,0,0)