from typing import Literal, NoReturn
from OPERATION_TABLE import OPTAB

# TAKES PROG AS INPUT RETURNS LOC_CTR & SYM_TAB


def pass_1(lines):
    LOC_CTR = [0]  # in DECIMAL
    SYM_TAB = {}
    LIT_TAB = {}
    ltctr = 0
    for line in lines:
        
        # REMOVE LEADING SPACES
        line = line.lstrip(" ")
        line = line.rstrip(" ")

        words = line.upper().split()

        # SHOULD ADD FLAGS #TODO LATER
        if "START" in words:
            continue
        if "END" in words: 
            for i in range (ltctr,len(list(LIT_TAB.values()))):
                CTR_DUP= LOC_CTR[-1]
                BRUH = list(LIT_TAB.keys())[i]
                LOC_CTR[-1] = LOC_CTR[-1] + int(list(LIT_TAB.values())[i]) 
                LIT_TAB[BRUH]=hex(CTR_DUP)
            print("Finished Pass one!")
            break
        if not words:  # FOR EMPTY LINES
            continue
        if line[0] == '.':  # FOR COMMENTS
            continue
        if words[0] == "BASE":
            continue
        if words[0] == "LTORG":
            for i in range (ltctr,len(list(LIT_TAB.values()))):
                CTR_DUP= LOC_CTR[-1]
                BRUH = list(LIT_TAB.keys())[i]
                LOC_CTR[-1] = LOC_CTR[-1] + int(list(LIT_TAB.values())[i]) 
                LIT_TAB[BRUH]= hex(CTR_DUP)
                ltctr=ltctr+1
            
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
        lit_find(words,LIT_TAB)
        
        # PRINT TO OUT.txt
        output_outtxt(line, LOC_CTR[-1])
       

        LOC_CTR.append(LOC_CTR[-1] + loc_ctr_step)
    print(LIT_TAB.items())
    output_littab(LIT_TAB)
    return LOC_CTR, SYM_TAB,LIT_TAB


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
    # returns SUCESSs , LOC_CTR_STEP(int)

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

def lit_find(words,LIT_TAB): 
    Literal_1=""
    Literal_=""
    if len(words) == 3:
        Literal_1 = words[2]
        
    elif len(words) == 2:
        Literal_1= words[1]
        
    if  '=' in Literal_1:
        Literal_=Literal_1
        LIT_TAB[Literal_]=-1
    loc_ctr_step = -1
    if "=C" in Literal_:
        loc_ctr_step = len(Literal_1)-4
        LIT_TAB[Literal_1]=loc_ctr_step
        return Literal_
    if "=X" in Literal_:
        loc_ctr_step= int((len(Literal_1)-4)/2)
        LIT_TAB[Literal_1]= loc_ctr_step
        return Literal_
   
    return Literal_




def output_littab(lttab):  
    file = open("out/LIT_TABLE.txt", "a")
    file.write("LITERALS"+"\t"+"ADDRESSES"+"\n")
    for i in range (0,len(list(lttab.values()))):
        file.write(str(list(lttab.keys())[i]).ljust(6) + "" +str(list(lttab.values())[i]).rjust(12) +"\n" )
    file.close()
    return
    

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
