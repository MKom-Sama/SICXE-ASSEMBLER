
def output_HTE(prog_name, OBJ_CODE, MODIFIED, loc_ctr, first_exe):
    # opening File
    file = open("out/HTE.txt", "w")

    # H Record
    file.write('H.' + prog_name.ljust(6) + '.' + format_hex_size(
        hex(loc_ctr[0]), 6) + '.' + format_hex_size(hex(loc_ctr[-1]-loc_ctr[0]), 6) + '\n')

    # T Record
    max_size = 30*2  # Hex char
    i = 0
    while i < len(OBJ_CODE):
        # New T Record
        T_code = ''
        start_addr = -1
        end_addr = -1
        j = i
        while j < len(OBJ_CODE):
            # Check if no Obj_code
            if OBJ_CODE[j] == None:
                start_addr = loc_ctr[i]
                end_addr = loc_ctr[j]
                # Start new T record at next valid loc
                while OBJ_CODE[j] == None:
                    j += 1
                i = j
                break
            # count number of bytes
            if len(T_code + OBJ_CODE[j][2:]) > max_size:
                # Start new T record
                start_addr = loc_ctr[i]
                end_addr = loc_ctr[j]
                i = j
                break

            T_code += OBJ_CODE[j][2:].upper()
            j += 1
        # End Of Program
        if j == len(OBJ_CODE):
            # Last T Record
            file.write('T.' + format_hex_size(hex(loc_ctr[i]), 6).upper() + '.' +
                       format_hex_size(hex(loc_ctr[j]-loc_ctr[i]), 2).upper() + '.' + T_code + '\n')
            break
        # Output T Record
        file.write('T.' + format_hex_size(hex(start_addr), 6).upper() + '.' +
                   format_hex_size(hex(end_addr-start_addr), 2).upper() + '.' + T_code + '\n')

    # M Record
    for mod in MODIFIED:
        file.write(
            'M.'+format_hex_size(hex(mod['address']), 6)+'.'+mod['half-byte']+mod['value']+'\n')

    # E Record
    file.write('E.'+format_hex_size(first_exe, 6).upper() + '\n')

    file.close()
    return


def format_hex_size(object_code, size):
    fillChar = '' if abs(len(object_code[2:])-size) == 0 else '0'
    return fillChar.ljust(abs(len(object_code[2:])-size), '0') + object_code[2:]


def output_symtab(symbol, LOC_CTR):
    file = open("out/SYMBOL_TABLE.txt", "a")
    addr = '0x' + hex(int(LOC_CTR))[2:].upper()
    file.write(addr.ljust(6) + " " + symbol + "\n")
    file.close()
    return


def output_outtxt(loc_ctr, lines, obj_code, lit_tab):
    file = open("out/OUT.txt", "a")

    idx = 0
    lit_idx = 0
    for line in lines:
        # REMOVE LEADING SPACES
        line = line.lstrip(" ")
        line = line.rstrip(" ")

        words = line.upper().split()

        if "START" in words:
            continue
        if "END" in words:
            print_dashed_line(file)
            file.write('| ' + ' '.ljust(6) + ' : ')
            file.write(
                ' '.ljust(8) + words[0].ljust(6) + " " + words[1].ljust(10))
            file.write('-'.ljust(12).upper()[2:] + ' |' + '\n')
            break
        if "BASE" in words:
            file.write('-'.ljust(48, '-') + '\n')
            file.write('| ' + ' '.ljust(6) + ' : ')
            file.write(
                ' '.ljust(8) + words[0].ljust(6) + " " + words[1].ljust(10))
            file.write('-'.ljust(12).upper()[2:] + ' |' + '\n')
            continue
        if not words:
            continue

        if line[0] == '.':  # FOR COMMENTS
            continue

        if "LTORG" in words:
            print_dashed_line(file)
            file.write('| ' + ' '.ljust(6) + ' : ')
            file.write(
                ' '.ljust(8) + words[0].ljust(6) + " " + ' '.ljust(20) + ' |' + '\n')
            if lit_idx < len(list(lit_tab.keys())):
                # Print Literals
                while lit_tab[list(lit_tab.keys())[lit_idx]] == loc_ctr[idx]:
                    addr = '0x' + hex(loc_ctr[idx])[2:].upper()
                    print_dashed_line(file)
                    file.write('| ' + addr.ljust(6) + ' : ')
                    file.write(
                        ' '.ljust(8) + '*'.ljust(6) + " " + list(lit_tab.keys())[lit_idx].ljust(10))
                    file.write(obj_code[idx].ljust(
                        12).upper()[2:] + ' |' + '\n')
                    idx += 1
                    lit_idx += 1     
                    # Prevent idx out of range err
                    if lit_idx == len(list(lit_tab.keys())):
                        break
                continue
            else:
                print_dashed_line(file)
            continue

        addr = '0x' + hex(loc_ctr[idx])[2:].upper()

        file.write('-'.ljust(48, '-') + '\n')

        file.write('| ' + addr.ljust(6) + ' : ')
        if len(words) == 3:
            file.write(words[0].ljust(8) +
                       words[1].ljust(6) + " " + words[2].ljust(10))
        elif len(words) == 2:
            file.write(
                ' '.ljust(8) + words[0].ljust(6) + " " + words[1].ljust(10))
        else:
            file.write(
                ' '.ljust(8) + words[0].ljust(6) + " " + ' '.ljust(10))

        if(idx == len(obj_code)):
            file.write('-'.ljust(12).upper()[2:] + ' |' + '\n')
            break

        obj = '-' if obj_code[idx] == None else obj_code[idx]
        file.write(obj.ljust(12).upper()[2:] + ' |' + '\n')

        idx += 1

    # Default LTORG after
    if lit_idx < len(list(lit_tab.keys())):
        while lit_tab[list(lit_tab.keys())[lit_idx]] == loc_ctr[idx]:
            # Print Literals
            addr = '0x' + hex(loc_ctr[idx])[2:].upper()
            print_dashed_line(file)
            file.write('| ' + addr.ljust(6) + ' : ')
            file.write(
                ' '.ljust(8) + '*'.ljust(6) + " " + list(lit_tab.keys())[lit_idx].ljust(10))
            file.write(obj_code[idx].ljust(
                12).upper()[2:] + ' |' + '\n')

            lit_idx += 1
            idx += 1
            # Prevent idx out of range err
            if lit_idx == len(list(lit_tab.keys())):
                break

    file.write('-'.ljust(48, '-') + '\n')
    file.close()
    return

# * TESTING FUNCTIONS


def output_objcode(OBJ_CODE):
    file = open("out/OBJECT_CODE.txt", "w")
    for obj in OBJ_CODE:
        if obj == None:
            file.write('NONE \n')
            continue
        file.write('0x' + obj[2:].upper() + "\n")

    file.close()
    return


def print_dashed_line(file):
    file.write('-'.ljust(48, '-') + '\n')


def output_loc_ctr(loc_ctr):
    file = open("out/LOC_CTR.txt", "w")
    for obj in loc_ctr:
        file.write(hex(obj) + "\n")

    file.close()
