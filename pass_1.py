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
            print("Finished Pass one!")
            break
        if not words:  # FOR EMPTY LINES
            continue
        if line[0] == '.':  # FOR COMMENTS
            continue
        if words[0] == "BASE":
            continue

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

    signature_sign = words[0][0]
    # If signature_sign found remove it
    format_ = -1
    # FORMAT 4
    if signature_sign == '+':
        format_ = 4
        words[0] = words[0][1:]
    # FORMAT 5
    if signature_sign == '&':
        format_ = 5
        words[0] = words[0][1:]
    # FORMAT 6
    if signature_sign == '$':
        format_ = 6
        words[0] = words[0][1:]
    instruct = [value for value in words if value in keys]

    if instruct:
        instruct = instruct[0]
        f_type = OPTAB[instruct][1]

        if format_ == 4:
            return instruct, 4
        if format_ == 5:
            return instruct, 3
        if format_ == 6:
            return instruct, 4

         # format 3 or 4 instruction
        if f_type == 12:
            return instruct, 3

        return instruct, int(f_type)
    else:
        # SYMBOL DECLARATIONS OR DIRS
        return "SYMBOL", 0


def is_instruction(word):
    keys = list(OPTAB.keys())
    # RETURNS loc_ctr_step
    loc_ctr_step = -1
    if word[0] == '+':
        loc_ctr_step = 4
        word = word[1:]
    if word[0] == '$':
        loc_ctr_step = 4
        word = word[1:]
    if word[0] == '&':
        loc_ctr_step = 3
        word = word[1:]

    if loc_ctr_step != -1:
        return loc_ctr_step

    if word in keys:
        type_ = OPTAB[word][1]
        if type_ == 12:
            return 3
        return type_
    return -1


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
        if line[2][0:2] == "C'":
            loc_ctr_step = len(line[2][2:])-1
        if line[2][0:2] == "X'":
            loc_ctr_step = len(line[2][2:]) // 2
    if type_ == "WORD":
        loc_ctr_step = 3

    if loc_ctr_step != 0:
        return success, loc_ctr_step
    # CHECK IF ITS A LABEL TO AN INSTRUCTION
    loc_ctr_step = is_instruction(type_)
    return success, loc_ctr_step


def output_symtab(symbol, LOC_CTR):
    file = open("out/SYMBOL_TABLE.txt", "a")
    addr = '0x' + hex(int(LOC_CTR))[2:].upper()
    file.write(addr.ljust(6) + " " + symbol + "\n")
    file.close()
    return


def output_outtxt(line, current_loc_ctr):
    file = open("out/OUT.txt", "a")
    words = line.split()
    addr = '0x' + hex(int(current_loc_ctr))[2:].upper()
    if len(words) == 3:
        file.write(addr.ljust(
            6) + " : " + words[0].ljust(8) + words[1].ljust(6) + " " + words[2].ljust(6) + "\n")
    elif len(words) == 2:
        file.write(addr.ljust(6) + " : " +
                   ' '.ljust(8) + words[0].ljust(6) + " " + words[1].ljust(6) + "\n")
    else:
        file.write(addr.ljust(6) + " : " +
                   ' '.ljust(8) + words[0].ljust(6) + "\n")

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
