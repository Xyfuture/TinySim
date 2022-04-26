from inst import Inst,gen_inst


core_0 = [
    Inst('ldi', rd=1, imm=12),
    Inst('ldi', rd=2, imm=1000),
    Inst('ldi', rd=3, imm=128),
    Inst('ldi', rd=4, imm=2000),
    Inst('ldi', rd=5, imm=128),

    Inst('send', rs1=2, rs2=3, imm=1),
    # Inst('send',rs1=4,rs2=5,imm=1),
    Inst('ldi', rd=6, imm=123)
]

core_1 = [
    Inst('ldi', rd=1, imm=12),
    Inst('ldi', rd=2, imm=1000),
    Inst('ldi', rd=3, imm=128),

    # instruction('bind',rd=1,rs1=2,rs2=3,imm=4,bitwidth=1),
    # instruction('gemv',rd=1,rs1=4,rs2=5,bitwidth=1),
    Inst('recv', rs1=2, rs2=3, imm=0),
    Inst('ldi', rd=6, imm=456)
]



if __name__ == "__main__":
    gen_inst(core_0,0)
    gen_inst(core_1,1)