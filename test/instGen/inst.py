import pickle



class Inst:
    def __init__(self,op='none',rd=0,rs1=0,rs2=0,imm=0,bitwidth=0):
        self.op = op
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.bitwidth = bitwidth

    def dump_dict(self):
        default_args = ['op','rd','rs1','rs2','imm','bitwidth']
        default_dict = {}

        for arg in default_args:
            default_dict[arg] = self.__dict__[arg]

        return default_dict

    def print_dict(self):
        print(self.dump_dict())




def gen_inst(inst_list,core_id=0,path='E:\\code\\TinySim\\test\\inst\\'):
    dict_list = [i.dump_dict() for i in inst_list]
    file_name = path + str(core_id) + '.pkl'

    with open(file_name,'wb') as f:
        pickle.dump(dict_list,f)

    for i in inst_list:
        i.print_dict()