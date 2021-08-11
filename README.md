# bastoken

Tokenizes an AppleSoft BASIC program

## Usage

`usage: bastoken.py [-h] [-l] input output`

positional arguments:

* `input` is a text file containing the AppleSoft BASIC program
* `output` will contain the tokenized program, suitable for running on an Apple II

optional arguments:
* `-l`, `--allow_lower`: Whether to accept lower-case input without canonicalizing to upper-case. The original
  (unenhanced) //e did not canonicalize program input, meaning that lower-case would be accepted (but not
  recognized as valid tokens, i.e. would not usually produce a valid program).  The enhanced //e (and later
  models) canonicalize input except within string literals, REMarks and DATA statements.

The output file can be written back to a disk image, e.g. using [AppleCommander](https://applecommander.github.io/):

`java -jar /path/to/AppleCommander.jar -p <disk> <file> BAS 0x801 < <output>`

where
* `<disk>` is the name of the disk image to write to
* `<file>` is the filename on this disk image to which the BASIC file should be written
* `<output>` is the file created by bastoken.py