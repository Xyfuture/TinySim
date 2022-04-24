


class StallEvent:
    def __init__(self,stage_name,level:int):
        self.stage_name = stage_name
        self.level = level # True则为触发stall，False则为cancel stall


class StallEngine:
    def __init__(self):
        self.stage_list =[]
        self.stall_event = []
        self.stall_level = 0


    def enroll(self,stage):
        self.stage_list.append(stage)

    def update(self):
        self.stall_level = 0
        self.stall_event = []
        for stage in self.stage_list:
            cur_stall = stage.stall_info()
            if cur_stall:
                self.stall_event.append(cur_stall)
                if cur_stall.level > self.stall_level:
                    self.stall_level = cur_stall.level

    def check_not_stall(self,level):
        return level>=self.stall_level

    def check_stall(self,level):
        return level<self.stall_level

