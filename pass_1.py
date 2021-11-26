from OPERATION_TABLE import OPTAB

# TAKES PROG AS INPUT RETURNS LOC_CTR & SYM_TAB


def pass_1(lines):
    LOC_CTR = [0]  # in DECIMAL
    SYM_TAB = {}
    for line in lines:

        # REMOVE LEADING SPACES
        line = line.lstrip(" ")
        line = line.rstrip(" ")

        words = line.upper().split()

        # SHOULD ADD FLAGS #TODO LATER
        if "START" in words:
            continue
        if "END" in words:
            break

        # FIND INSTRUCTION FORMAT
        instruct, f_size = find_format(words, list(OPTAB.keys()))

        loc_ctr_step = f_size
        if instruct == "SYMBOL":
            valid, loc_ctr_step = declare_symbol(words, LOC_CTR[-1], SYM_TAB)
            if valid:
                SYM_TAB[words[0]] = LOC_CTR[-1]
            else:
                # INVALID SYMBOL DECLARATION
                stop_process(words[0] + " already declared! \n" + "at : "+line)
                return
        # PRINT TO OUT.txt
        output_outtxt(line, LOC_CTR[-1])

        LOC_CTR.append(LOC_CTR[-1] + loc_ctr_step)

    return LOC_CTR, SYM_TAB


def find_format(words, keys):
    # RETURNS INSTRUCT , FORMAT_SIZE(int) || SYMBOL_NAME
    instruct = [value for value in words if value in keys]

    f_type = 1  # DEF FORMAT_1 FOR NOW
    if instruct:
        instruct = instruct[0]

        f_type = OPTAB[instruct][1]

        # MYSTERY FORMATS CHECK
        is_format_6 = [word for word in words if '$' in word]
        if is_format_6:
            return instruct, 4
        is_format_5 = [word for word in words if '&' in word]
        if is_format_5:
            return instruct, 3

         # format 3 or 4 instruction
        if f_type == 12:
            type_ = [word for word in words if '+' in word]
            if type_:
                return instruct, 4
            return instruct, 3

        return instruct, int(f_type)
    else:
        # SYMBOL DECLARATIONS OR DIRS
        return "SYMBOL", 0


def declare_symbol(line, LOC_CTR, SYM_TAB):
    # returns success , loc_ctr_step(int)
    # Writes to SYMBOL_TABLE FILE
    symbol = line[0]
    type_ = line[1]

    # CHECK IF SYMBOL ALREADY DECLARED
    if symbol in SYM_TAB.keys():
        return False, -1

    # CHECK THE TYPE OF line[2] (default decimal for now)

    success = True

    output_symtab(symbol, LOC_CTR)

    loc_ctr_step = 0
    if type_ == "RESB":
        loc_ctr_step = int(line[2])
    if type_ == "RESW":
        loc_ctr_step = int(line[2])*3
    if type_ == "BYTE":
        loc_ctr_step = 1
    if type_ == "WORD":
        loc_ctr_step = 3

    return success, loc_ctr_step


def output_symtab(symbol, LOC_CTR):
    file = open("out/SYMBOL_TABLE.txt", "a")
    file.write(symbol + " " + hex(int(LOC_CTR)) + "\n")
    file.close()
    return


def output_outtxt(line, current_loc_ctr):
    file = open("out/OUT.txt", "a")
    file.write(hex(int(current_loc_ctr)).ljust(6) + " : " + line)
    file.close()
    return


def stop_process(msg):
    print('\033[91m'
          + "Err : "+msg + '\033[0m')

    # CLEAR SYMBOL_TABLE.txt
    file = open("out/SYMBOL_TABLE.txt", "w")
    file.write("FAILED BUILD FIX YOUR CODE!")
    file.close()

    return
