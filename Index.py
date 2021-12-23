from pass_1 import pass_1
from pass_2 import pass_2


# READING INPUT FILE
with open('assembly.txt') as f:
    lines = f.readlines()

# CLEARING OUTPUT FILES
open("out/SYMBOL_TABLE.txt", "w").close()
open("out/OUT.txt", "w").close()

# PASS 1
loc_ctr = []
sym_tab = []

if "START" not in lines[0].upper().split(" "):
    print("First line needs to have start keyword")

loc_ctr, sym_tab = pass_1(lines)

# PASS 2
obj_code = []
obj_code = pass_2(lines,sym_tab,loc_ctr)

