from OPERATION_TABLE import OPTAB
from REGISTERS import REGISTERS

from utils import output_HTE


def pass_2(lines, sym_tab, loc_ctr):
    meta = {'sym_tab': sym_tab, 'loc_ctr': loc_ctr}
    OBJ_CODE = []
    idx = 0  # Loc_ctr pointer

    # FOR HTE
    global MODIFIED  # Contains {'address': , 'half_byte': ,'value':}
    global prog_name

    MODIFIED = []
    prog_name = ''
    first_exe_loc = -1
    # Get Object Code
    for line in lines:
        # REMOVE LEADING SPACES
        line = line.lstrip(" ")
        line = line.rstrip(" ")

        words = line.upper().split()
        try:
            PC = loc_ctr[idx+1]
        except:
            break

        if "START" in words:
            prog_name = words[0]
            continue

        if "END" in words:
            break

        if not words:  # FOR EMPTY LINES
            continue

        if line[0] == '.':  # FOR COMMENTS
            continue

        if "RESB" in words or "RESW" in words:
            idx = idx + 1
            OBJ_CODE.append(None)
            continue

        if "BASE" in words:
            REGISTERS['B'][1] = sym_tab[words[1]]
            continue

        if "BYTE" in words or "WORD" in words:  # TODO LATER
            idx = idx+1
            OBJ_CODE.append(data_definition(words))
            continue

        # FOR HTE FIRST EXECUTABLE INSTRUCTION
        if first_exe_loc == -1:
            first_exe_loc = hex(loc_ctr[idx])

        # HAS OBJECT CODE & IS INSTRUCTION
        instruct, format_type = find_format(words, list(OPTAB.keys()))

        OPCODE = OPTAB[instruct][0]

        if format_type == 1:
            idx += 1
            OBJ_CODE.append(handle_format_one(OPCODE))
            continue

        if format_type == 2:
            idx += 1
            OBJ_CODE.append(handle_format_two(words, OPCODE))
            continue

        if format_type == 3:
            idx += 1
            OBJ_CODE.append(handle_format_three(words, OPCODE, meta, PC))
            continue

        if format_type == 4:
            idx += 1
            OBJ_CODE.append(handle_format_four(words, OPCODE, meta, PC))
            continue

        if format_type == 5:
            idx += 1
            OBJ_CODE.append(handle_format_five(words, OPCODE, meta, PC))
            continue

        if format_type == 6:
            idx += 1
            OBJ_CODE.append(handle_format_six(words, OPCODE, meta, PC))
            continue

    print('Finished Pass two!')

    # HTE Output
    output_HTE(prog_name, OBJ_CODE, MODIFIED, loc_ctr, first_exe_loc)

    return OBJ_CODE


def find_format(words, keys):
    # RETURNS FORMAT_TYPE
    if len(words) == 3:
        instruct = words[1]
    else:
        instruct = words[0]

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
    return instruct, format_


def handle_format_one(OPCODE):
    return OPCODE


def handle_format_two(words, OPCODE):

    idx = 0
    if (len(words) == 3):
        idx = 1
    r1r2 = words[idx+1].split(',')

    # Check for SHIFTL/R & SVC since they take numbers
    if OPCODE == OPTAB['SHIFTL'][0] or OPCODE == OPTAB['SHIFTR'][0]:
        return hex(OPCODE) + str(REGISTERS[r1r2[0]]) + hex(int(r1r2[1]))[2]

    if OPCODE == OPTAB['SVC'][0]:
        return hex(OPCODE) + hex(int(r1r2[0]))[2] + '0'

    if len(r1r2) == 2:
        return hex(OPCODE) + str(REGISTERS[r1r2[0]]) + str(REGISTERS[r1r2[1]])

    return hex(OPCODE) + str(REGISTERS[r1r2[0]]) + '0'


def handle_format_three(words, OPCODE, meta, PC):
    meta['PC'] = PC
    opni, words = opni_hex(words, OPCODE)

    xbpe, disp = xbpe_hex(words, meta)
    return opni + xbpe + disp


def handle_format_four(words, OPCODE, meta, PC):
    meta['PC'] = PC
    opni, words = opni_hex(words, OPCODE)

    xbpe, addr = xbpe_hex(words, meta)
    return opni + xbpe + addr


def handle_format_five(words, OPCODE, meta, PC):
    meta['PC'] = PC

    opf1f2 = OPCODE

    xbpe, disp = xbpe_hex(words, meta)

    disp_val = int('0x'+disp, 16)
    xbpf3 = xbpe
    # F1 ? disp is even
    if (disp_val % 2 == 0):
        opf1f2 += 2
    # F2 ? disp is -ve (check for signed bit)
    if (disp_val & 0x800):
        opf1f2 += 1

    # F3 ? disp = 0
    if (disp_val == 0):
        xbpf3 = hex(int('0x'+xbpe, 16)+1)[2:]

    return hex(opf1f2) + xbpf3 + disp


def handle_format_six(words, OPCODE, meta, PC):
    meta['PC'] = PC
    opni, words = opni_hex(words, OPCODE)

    not_used, addr = xbpe_hex(words, meta)

    addr_val = int('0x'+addr, 16)

    xbpe = 0
    idx = 0
    if len(words) == 3:
        idx = 1
    # X  ?
    if (words[idx+1].split(',')[-1] == 'X'):
        xbpe += 8

    # F4 ?  addr is odd
    if (addr_val % 2 != 0):
        xbpe += 4

    # F5 ? addr not zero
    if (addr_val != 0):
        xbpe += 2

    # F6 ? addr = BASE
    if (addr_val == REGISTERS['B'][1]):
        xbpe += 1

    return opni + hex(xbpe)[2:] + addr


def data_definition(words):
    # Returns object code of Byte & Word

    varSize = 1  # byte
    if "WORD" in words:
        varSize = 3  # byte

    # Must be VarName : Datatype : Value
    if (len(words) != 3):
        return 'Invalid Data Declaration'

    arrOfData = words[2].split(',')

    obj_code = '0x'
    for data in arrOfData:
        try:
            num = hex(int(data))[2:]
            # check for valid size
            if (len(num) > varSize*2):
                stop_process('Invalid Data Size')
                return

            fillChar = '' if abs(len(num)-varSize*2) == 0 else '0'
            obj_code += fillChar.ljust(abs(len(num)-varSize*2), '0') + num

        except:
            # X' || C'
            if data[0] == 'C':
                arrOfChars = data[2:-1]
                for char in arrOfChars:
                    hexed = hex(ord(char))[2:]
                    fillChar = '' if abs(len(hexed)-varSize*2) == 0 else '0'
                    obj_code += fillChar.ljust(abs(len(hexed) -
                                               varSize*2), '0') + hexed
            if data[0] == 'X':
                hexed = data[2:-1]
                fillChar = '' if abs(len(hexed)-varSize*2) == 0 else '0'
                obj_code += fillChar.ljust(abs(len(hexed) -
                                           varSize*2), '0') + hexed
    return obj_code


def opni_hex(words, OPCODE):
    # Gets __OP6_._ni2_
    ni = 3
    idx = 0
    if len(words) == 3:
        idx = 2
    elif len(words) == 2:
        idx = 1

    if words[idx][0] == '@':
        ni = 2
    elif words[idx][0] == '#':
        ni = 1

    # Remove Sign no more use for it
    if ni != 3:
        words[idx] = words[idx][1:]

    # first_two_hex = OPCODE + ni
    hexed = hex(OPCODE + ni)
    if len(hexed) == 3:  # 0x1
        hexed = hexed[:2] + '0' + hexed[2:]
    return hexed, words


def xbpe_hex(words, meta):
    # Returns xbpe , disp || addr
    # * USES A GLOBAL VARIABLE 'MODIFIED'
    xbpe = 0
    loc_ctr = meta['loc_ctr']
    sym_tab = meta['sym_tab']
    PC = meta['PC']

    idx = 0
    if len(words) == 3:
        idx = 1
    elif len(words) == 2:
        idx = 0
    else:
        # RSUB
        return '0', '000'

    # x ?
    if (words[idx+1].split(',')[-1] == 'X'):
        xbpe += 8
        # remove ,X no use for it
        words[idx+1] = words[idx+1].split(',')[0]

    # e ? or f6
    if (words[idx][0] == '+' or words[idx][0] == '$'):
        xbpe += 1
        addr = 0
        try:
            num = int(words[idx+1])
            addr = num
        except:
            addr = sym_tab[words[idx+1]]
            # To Be Modified in M record
            MODIFIED.append({'address': loc_ctr[loc_ctr.index(
                PC)-1]+1, 'half-byte': '05', 'value': '+'+prog_name})

        # bp = 00 in format_4
        return hex(xbpe)[2:], '0'.ljust(abs(len(hex(addr))-7), '0')+hex(addr)[2:]

    # bp ?
    # var or num
    bp = 0
    disp = 0
    try:
        # number
        num = int(words[idx+1])
        bp = 0
        disp = num
    except:
        # variable
        dest = sym_tab[words[idx+1]]
        if -2048 <= (dest-PC) <= 2047:
            xbpe += 2
            disp = dest - PC
        elif 0 <= dest - REGISTERS['B'][1] <= 4095:
            xbpe += 4
            disp = dest - REGISTERS['B'][1]
        else:
            print('Couldnt reach destination: Bad Code',
                  words[idx], dest, PC, disp)
    xbpe = hex(xbpe)[2:]
    filler = '0'
    if disp < 0:
        disp = hex(twos_complement(disp, 12))[2:]
    else:
        disp = '0'.ljust(abs(len(hex(disp))-5), '0') + hex(disp)[2:]
    return xbpe, disp


def twos_complement(val, nbits):
    """Compute the 2's complement of int value val"""
    if val < 0:
        val = (1 << nbits) + val
    else:
        if (val & (1 << (nbits - 1))) != 0:
            # If sign bit is set.
            # compute negative value.
            val = val - (1 << nbits)
    return val


def stop_process(msg):
    print('\033[91m'
          + "Err : "+msg + '\033[0m')

    # CLEAR SYMBOL_TABLE.txt
    file = open("out/SYMBOL_TABLE.txt", "w")
    file.write("FAILED BUILD FIX YOUR CODE!")
    file.close()

    return
