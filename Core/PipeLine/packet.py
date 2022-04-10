




class InnerPacket:
    def __init__(self,dest_id,packet_size,call_back,direction='send'):
        self.dest_id = dest_id
        self.packet_size = packet_size
        self.call_back = call_back
        self.direction = direction



