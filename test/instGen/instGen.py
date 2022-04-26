from inst import Inst,gen_inst


core_0 = [
    Inst('ldi',rd=1,imm=1000),
    Inst('ldi',rd=2,imm=128),
    Inst('ldi',rd=3,imm=2000),
    Inst('ldi',rd=4,imm=3000),
    Inst('ldi',rd=5,imm=2),

    Inst('bind',rd=5,rs1=1,rs2=2,imm=4,bitwidth=1),
    Inst('gemv',rd=5,rs1=3,rs2=2,bitwidth=1),
    Inst('gvr',rd=5,rs1=3,rs2=2),

    Inst('vvset',rd=2,bitwidth=1),
    Inst('vvadd',rd=1,rs1=3,rs2=4),
    Inst("vvsub",rd=3,rs1=1,rs2=4)
]

core_1 = [



]



if __name__ == "__main__":
    gen_inst(core_0,0)
    # gen_inst(core_1,1)