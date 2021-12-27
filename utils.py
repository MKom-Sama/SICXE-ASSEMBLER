
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
