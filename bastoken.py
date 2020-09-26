"""Tokenizes an AppleSoft BASIC program into memory representation.

See http://www.txbobsc.com/scsc/scdocumentor/D52C.html for original source.

TODO: add tests
"""

import sys

TOKENS = {}

for i, t in enumerate([
    "END",
    "FOR",
    "NEXT",
    "DATA",
    "INPUT",
    "DEL",
    "DIM",
    "READ",
    "GR",
    "TEXT",
    "PR#",
    "IN#",
    "CALL",
    "PLOT",
    "HLIN",
    "VLIN",
    "HGR2",
    "HGR",
    "HCOLOR=",
    "HPLOT",
    "DRAW",
    "XDRAW",
    "HTAB",
    "HOME",
    "ROT=",
    "SCALE=",
    "SHLOAD",
    "TRACE",
    "NOTRACE",
    "NORMAL",
    "INVERSE",
    "FLASH",
    "COLOR",
    "POP",
    "VTAB",
    "HIMEM:",
    "LOMEM:",
    "ONERR",
    "RESUME",
    "RECALL",
    "STORE",
    "SPEED=",
    "LET",
    "GOTO",
    "RUN",
    "IF",
    "RESTORE",
    "&",
    "GOSUB",
    "RETURN",
    "REM",
    "STOP",
    "ON",
    "WAIT",
    "LOAD",
    "SAVE",
    "DEF",
    "POKE",
    "PRINT",
    "CONT",
    "LIST",
    "CLEAR",
    "GET",
    "NEW",
    "TAB(",
    "TO",
    "FN",
    "SPC(",
    "THEN",
    "AT",
    "NOT",
    "STEP",
    "+",
    "-",
    "*",
    "/",
    "^",
    "AND",
    "OR",
    ">",
    "=",
    "<",
    "SGN",
    "INT",
    "ABS",
    "USR",
    "FRE",
    "SCRN(",
    "PDL",
    "POS",
    "SQR",
    "RND",
    "LOG",
    "EXP",
    "COS",
    "SIN",
    "TAN",
    "ATN",
    "PEEK",
    "LEN",
    "STR$",
    "VAL",
    "ASC",
    "CHR$",
    "LEFT$",
    "RIGHT$",
    "MID$"
]):
    TOKENS[t] = 0x80+i

def parse_program(lines):
    yield 0x00
    addr = 0x801
    for line in lines:
        linenum, tokenized = parse_line(line.rstrip("\n"))
        tokenized = list(tokenized)
        addr += len(tokenized) + 4
        yield addr % 256
        yield int(addr / 256)
        yield linenum % 256
        yield int(linenum / 256)
        yield from tokenized
    yield 0x00
    yield 0x00

def parse_line(line):
    line_num_str = ""
    for idx, char in enumerate(line):
        if char >= '0' and char <= '9':
            line_num_str += char
        else:
            break
    line_num = int(line_num_str)
    if line_num > 65535:
        raise ValueError(line_num)

    return int(line_num), parse_statements(line[idx:])

def parse_statements(line):
    dataFlag = False
    remFlag = False
    quoteFlag = None

    char_idx = 0
    while char_idx < len(line):
        char = line[char_idx]

        if char == " " and not (dataFlag or remFlag or quoteFlag):
            char_idx += 1
            continue

        if char == '"':
            quoteFlag = not quoteFlag

        if char == ':':
            dataFlag = False
            yield ord(char)
            char_idx += 1
            continue

        if quoteFlag or remFlag or dataFlag:
            yield ord(char)
            char_idx += 1
            continue

        if char == '?':
            yield TOKENS["PRINT"]
            char_idx += 1
            continue

        if '0' <= char <= ';':
            yield ord(char)
            char_idx += 1
            continue

        tokens, char_idx = read_token(line, char_idx)
        for token in tokens:
            if token == TOKENS["DATA"]:
                dataFlag = True
            elif token == TOKENS["REM"]:
                remFlag = True
            yield token
    yield 0x00


def read_token(line:str, idx:int):
    for token in TOKENS:
        lookahead_idx = idx
        token_idx = 0
        token_match = False
        while lookahead_idx < len(line) and token_idx < len(token):
            char = line[lookahead_idx]
            if char == " ":
                lookahead_idx += 1
                continue

            if char.upper() != token[token_idx]:
                break
            if token_idx == len(token)-1:
                token_match = True
                break

            lookahead_idx += 1
            token_idx += 1
        if token_match:
            break

    if not token_match:
        # Didn't find one, next character must be a literal
        return [ord(line[idx])], lookahead_idx+1

    # need to read one more char to disambiguate "AT/ATN/A TO"
    if token == "AT":
        if line[lookahead_idx + 1] == "N":
            return [TOKENS["ATN"]], lookahead_idx+2
        elif line[lookahead_idx + 1] == "O":
            return [ord("A"), TOKENS["TO"]], lookahead_idx+2
    return [TOKENS[token]], lookahead_idx+1


def main(argv):
    sys.stdout.write("0800: ")
    with open(argv[1], "r") as f:
        for c in parse_program(f.readlines()):
            sys.stdout.write("%02x " % c)
    print()

if __name__ == "__main__":
    main(sys.argv)