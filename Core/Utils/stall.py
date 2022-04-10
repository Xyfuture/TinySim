

class StallEvent:
    def __init__(self,stage_name,state:bool):
        self.stage_name = stage_name
        self.state = state # True则为触发stall，False则为cancel stall
