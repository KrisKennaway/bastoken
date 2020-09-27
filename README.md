# bastoken
Tokenizer for AppleSoft BASIC

## Usage

`python bastoken.py <input> <output>`

where
* `<input>` is a text file containing the AppleSoft BASIC program
* `<output>` will contain the tokenized program, suitable for running on an Apple II

The output file can be written back to a disk image, e.g. using [AppleCommander](https://applecommander.github.io/):

`java -jar /path/to/AppleCommander.jar -p <disk> <file> BAS 0x801 < <output>`

where
* `<disk>` is the name of the disk image to write to
* `<file>` is the filename on this disk image to which the BASIC file should be written
* `<output>` is the file created by bastoken.py