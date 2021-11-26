OPTAB = {
    # Mnemonic : Opcode , Format
    "ADD": [0x18, 3*4],
    "ADDF": [0x58, 3*4],
    "ADDR": [0x90, 2],
    "AND": [0x40, 3*4],
    "CLEAR": [0x40, 2],
    "COMP": [0xB4, 2],
    "LDA": [0x00, 3*4],
    "STA": [0x0C, 3*4],
    "LDX": [0x04, 3*4],
    "SIO": [0xF0, 1]
}
