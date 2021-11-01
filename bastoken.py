"""Tokenizes an AppleSoft BASIC program into memory representation.

See http://www.txbobsc.com/scsc/scdocumentor/D52C.html for original source.

TODO: add tests
"""

import argparse
import sys

TOKENS = {}

for i, t in enumerate([
    "END", "FOR", "NEXT", "DATA", "INPUT", "DEL", "DIM", "READ", "GR", "TEXT",
    "PR#", "IN#", "CALL", "PLOT", "HLIN", "VLIN", "HGR2", "HGR", "HCOLOR=",
    "HPLOT", "DRAW", "XDRAW", "HTAB", "HOME", "ROT=", "SCALE=", "SHLOAD",
    "TRACE", "NOTRACE", "NORMAL", "INVERSE", "FLASH", "COLOR=", "POP", "VTAB",
    "HIMEM:", "LOMEM:", "ONERR", "RESUME", "RECALL", "STORE", "SPEED=", "LET",
    "GOTO", "RUN", "IF", "RESTORE", "&", "GOSUB", "RETURN", "REM", "STOP", "ON",
    "WAIT", "LOAD", "SAVE", "DEF", "POKE", "PRINT", "CONT", "LIST", "CLEAR",
    "GET", "NEW", "TAB(", "TO", "FN", "SPC(", "THEN", "AT", "NOT", "STEP", "+",
    "-", "*", "/", "^", "AND", "OR", ">", "=", "<", "SGN", "INT", "ABS", "USR",
    "FRE", "SCRN(", "PDL", "POS", "SQR", "RND", "LOG", "EXP", "COS", "SIN",
    "TAN", "ATN", "PEEK", "LEN", "STR$", "VAL", "ASC", "CHR$", "LEFT$",
    "RIGHT$", "MID$"]):
    TOKENS[t] = 0x80 + i


class Tokenizer:
    def __init__(self, canonicalize_case=False):
        self.canonicalize_case = canonicalize_case

    def tokenize_program(self, lines):
        """Tokenizes a program consisting of multiple lines."""

        addr = 0x801
        for line in lines:
            if not line.strip():
                # Skip lines that entirely consist of other whitespace,
                # though we want to keep this for actual program lines
                continue
            linenum, tokenized = self.tokenize_line(line.rstrip("\n\r"))
            tokenized = list(tokenized)
            addr += len(tokenized) + 4
            # Starting address of next program line (or EOF)
            yield addr % 256
            yield int(addr / 256)
            # Line number
            yield linenum % 256
            yield int(linenum / 256)
            # Statement body
            yield from tokenized
        # No more lines
        yield 0x00
        yield 0x00

    def tokenize_line(self, line: str):
        """Tokenizes a program line consisting of line number and statement body."""

        line_num_str = ""
        for idx, char in enumerate(line):
            if '0' <= char <= '9':
                line_num_str += char
            else:
                break
        line_num = int(line_num_str)
        if line_num > 65535:
            raise ValueError(line_num)

        return int(line_num), self.tokenize_statements(line[idx:])

    def tokenize_statements(self, line: str):
        """Emits sequence of tokens for a line statement body."""

        data_mode = False  # Are we inside a DATA statement?
        rem_mode = False  # Are we inside a REM statement?
        quote_mode = False  # Are we inside a quoted string?

        char_idx = 0
        while char_idx < len(line):
            char = line[char_idx]

            if char == " " and not (data_mode or rem_mode or quote_mode):
                char_idx += 1
                continue

            if char == '"':
                quote_mode = not quote_mode

            if char == ':':
                data_mode = False
                yield ord(char)
                char_idx += 1
                continue

            if quote_mode or rem_mode or data_mode:
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

            tokens, char_idx = self.read_token(line, char_idx)
            for token in tokens:
                if token == TOKENS["DATA"]:
                    data_mode = True
                elif token == TOKENS["REM"]:
                    rem_mode = True
                yield token
        yield 0x00

    def read_token(self, line: str, idx: int):
        """Reads forward from idx and emits next matching token(s)."""
        for token in TOKENS:
            lookahead_idx = idx
            token_idx = 0
            token_match = False
            while lookahead_idx < len(line) and token_idx < len(token):
                char = self.canonicalize(line[lookahead_idx])
                if char == " ":
                    lookahead_idx += 1
                    continue

                if char != token[token_idx]:
                    break
                if token_idx == len(token) - 1:
                    token_match = True
                    break

                lookahead_idx += 1
                token_idx += 1
            if token_match:
                break

        if not token_match:
            # Didn't find one, next character must be a literal
            return [ord(self.canonicalize(line[idx]))], idx + 1

        # need to read one more char to disambiguate "AT/ATN/A TO"
        if token == "AT" and lookahead_idx < (len(line) - 1):
            if self.canonicalize(line[lookahead_idx + 1]) == "N":
                return [TOKENS["ATN"]], lookahead_idx + 2
            elif self.canonicalize(line[lookahead_idx + 1]) == "O":
                return [ord("A"), TOKENS["TO"]], lookahead_idx + 2
        return [TOKENS[token]], lookahead_idx + 1

    def canonicalize(self, char):
        return char.upper() if self.canonicalize_case else char


def main():
    parser = argparse.ArgumentParser(
        description="Tokenizes an AppleSoft BASIC program")
    parser.add_argument(
        "input", type=str,
        help="A text file containing the AppleSoft BASIC program")
    parser.add_argument(
        "output", type=str,
        help="Will contain the tokenized program, suitable for running on an "
             "Apple II")
    parser.add_argument(
        "-c", "--canonicalize_case", action="store_false",
        help="(Default: False) Whether to accept AppleSoft tokens in "
             "lower-case (e.g. 'home').  Enabling this matches behaviour of an "
             "enhanced //e (and later).  The original (unenhanced) //e did not "
             "canonicalize input case, meaning that lower-case input would not "
             "be recognized as valid tokens (i.e. would not usually produce a "
             "valid program).  The enhanced //e (and later models) "
             "canonicalizes input case except within string literals, REMarks "
             "and DATA statements.")
    args = parser.parse_args()
    tokenizer = Tokenizer(args.canonicalize_case)
    with open(args.input, "r") as data_input:
        with open(args.output, "wb") as data_output:
            for c in tokenizer.tokenize_program(data_input.readlines()):
                data_output.write(bytes([c]))


if __name__ == "__main__":
    main()
