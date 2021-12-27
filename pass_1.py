from OPERATION_TABLE import OPTAB

# TAKES PROG AS INPUT RETURNS LOC_CTR & SYM_TAB
def pass_1(lines):
    LOC_CTR = []  # in DECIMAL
    SYM_TAB = {}
    for line in lines:

        # REMOVE LEADING SPACES
        line = line.lstrip(" ")
        line = line.rstrip(" ")

        words = line.upper().split()

        # SHOULD ADD FLAGS #TODO LATER
        if "START" in words:
            if not LOC_CTR:         
                LOC_CTR.append(int(words[2],16));
                continue;
            else:
                stop_process("Found another START , not good")
                break;
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
        instruct, f_size, is_label = find_format(words, list(OPTAB.keys()))

        loc_ctr_step = f_size

        valid_symbol_declaration = False
        declared_symbol = False

        # FOR SYMBOLS AND LABELS
        if is_label == True:
            declared_symbol = True
            valid_symbol_declaration, not_used = declare_symbol(
                words, LOC_CTR[-1], SYM_TAB, True)
        elif instruct == "SYMBOL":
            declared_symbol = True
            valid_symbol_declaration, loc_ctr_step = declare_symbol(
                words, LOC_CTR[-1], SYM_TAB, False)

        # CHECK FOR REDECLARATION ERRORS

        if declared_symbol and (valid_symbol_declaration):
            SYM_TAB[words[0]] = LOC_CTR[-1]
        elif declared_symbol and (not valid_symbol_declaration):
            # INVALID SYMBOL DECLARATION
            stop_process(words[0] + " already declared! \n" + "at : "+line)
            return

        LOC_CTR.append(LOC_CTR[-1] + loc_ctr_step)

    return LOC_CTR, SYM_TAB


def find_format(words, keys):
    # RETURNS INSTRUCT, FORMAT_SIZE(int), IS_LABEL
    is_label = False
    if len(words) == 3:
        instruct = words[1]
        is_label = True
    else:
        instruct = words[0]

    # IF ITS BYTE | RESB | WORD | RESW
    if is_symbol_declare(instruct):
        return "SYMBOL", 0, False

    signature_sign = instruct[0]
    # If signature_sign found remove it
    format_ = -1
    # FORMAT 4
    if signature_sign == '+':
        format_ = 4
        instruct = instruct[1:]
    # FORMAT 5
    if signature_sign == '&':
        format_ = 5
        instruct = instruct[1:]
    # FORMAT 6
    if signature_sign == '$':
        format_ = 6
        instruct = instruct[1:]

    # OTHER FORMATS
    try:
        find_format = OPTAB[instruct][1]
        if format_ == -1:
            format_ = find_format
            if find_format == 12:
                format_ = 3
    except:
        stop_process('Invalid Instruction')
        return

    # RETURNING INSTRUCTION SIZE

    if format_ == 1:
        return instruct, 1, is_label
    if format_ == 2:
        return instruct, 2, is_label
    if format_ == 3:
        return instruct, 3, is_label
    if format_ == 4:
        return instruct, 4, is_label
    if format_ == 5:
        return instruct, 3, is_label
    if format_ == 6:
        return instruct, 4, is_label

    # SHOULDN'T REACH THIS RETURN
    return "Symbol", 0, False


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


def is_symbol_declare(word):
    return word == "BYTE" or word == "RESB" or word == "WORD" or word == "RESW"


def declare_symbol(line, LOC_CTR, SYM_TAB, is_label):
    # returns SUCESS , LOC_CTR_STEP(int)

    # Writes to SYMBOL_TABLE FILE
    symbol = line[0]
    type_ = line[1]


    # CHECK IF SYMBOL ALREADY DECLARED
    if symbol in SYM_TAB.keys():
        return False, -1

    # DECLARING JUST A LABEL
    if is_label:
        output_symtab(symbol, LOC_CTR)
        return True, -1

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
    file.write('-'.ljust(23,'-')+'\n')
    file.write('| ' +symbol.ljust(8) + " : " + addr.ljust(8) + ' | \n')
    file.write('-'.ljust(23,'-')+'\n')
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
