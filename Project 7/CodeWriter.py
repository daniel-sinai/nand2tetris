"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing
from Parser import ARITHMETIC

POINTERS = ["local", "argument", "this", "that"]
translate_dict = {"local": "LCL", "argument": "ARG", "this": "THIS",
                  "that": "THAT", "pointer": "3", "temp": "5"}


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        self.output = output_stream
        self.filename = ""
        self.eq_counter = 0
        self.pos_neg_counter = 0
        self.compare_counter = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(
        # input_file.name))
        self.filename = filename
        print("Start translating file: " + filename)

    def __shift(self, command, to_write):
        if command == "shiftleft":
            to_write += "// shift left\n@SP\nAM=M-1\nM=M<<\n@SP\nM=M+1\n"
        elif command == "shiftright":
            to_write += "// shift right\n@SP\nAM=M-1\nM=M>>\n@SP\nM=M+1\n"
        return to_write

    def __arithmetic(self, command, to_write):
        if command == "add":
            to_write += "// add\n@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M\n"
        elif command == "sub":
            to_write += "// subtract\n@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n"
        elif command == "neg":
            to_write += "// negate\n@SP\nAM=M-1\nM=-M\n@SP\nM=M+1\n"
        return to_write

    def __equal(self, to_write):
        self.eq_counter += 1
        to_write += "// equal\n"
        to_write += "@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@EQUAL" + \
                    str(self.eq_counter) + "\nD;JEQ" + \
                    "\nD=0\n@RESULTEQ" + str(self.eq_counter) + \
                    "\n0;JMP\n(EQUAL" + str(self.eq_counter) + \
                    ")\nD=-1\n(RESULTEQ" + str(self.eq_counter) + \
                    ")\n@SP\nA=M-1\nM=D\n"
        return to_write

    def __pos_neg(self):
        return "D=M\n@POSITIVE" + str(self.pos_neg_counter) \
                    + "\nD;JGE\n@NEGATIVE" + str(self.pos_neg_counter) + \
                    "\nD;JLT\n(POSITIVE" + str(self.pos_neg_counter) + \
                    ")\nD=1\n@ADVANCE" + str(self.pos_neg_counter) + "\n" + \
                    "0;JMP\n(NEGATIVE" + str(self.pos_neg_counter) + ")\n" + \
                    "D=-1\n(ADVANCE" + str(self.pos_neg_counter) + ")\n"

    def __same_or_diff(self, command):
        return "(SAMESIGN" + str(self.compare_counter) + ")\n" + \
                    "@SP\nA=M\nD=M\n@SP\nA=M-1\nD=M-D\n@CONTINUE" + \
                    str(self.compare_counter) + "\n0;JMP\n(DIFFSIGN" + \
                    str(self.compare_counter) + ")\n@SP\nA=M-1\nD=M\n" + \
                    "@CONTINUE" + str(self.compare_counter) + "\n0;JMP\n" + \
                    "(CONTINUE" + str(self.compare_counter) + ")\n" + \
                    "@CORRECT" + str(self.compare_counter) + "\nD;J" + \
                    command.upper() + "\nD=0\n@RESULT" + \
                    str(self.compare_counter) + "\n0;JMP\n(CORRECT" + \
                    str(self.compare_counter) + ")\nD=-1\n(RESULT" + \
                    str(self.compare_counter) + ")\n@SP\nA=M-1\nM=D\n"

    def __comparison(self, command, to_write):
        if command == "eq":
            return self.__equal(to_write)
        elif command == "gt":
            to_write += "// greater than\n"
        elif command == "lt":
            to_write += "// less than\n"
        self.compare_counter += 1
        to_write += "@SP\nAM=M-1\nA=A-1\nD=M\n@SAMESIGN" + \
                    str(self.compare_counter) + "\nD;JEQ\n"
        self.pos_neg_counter += 1
        to_write += "@SP\nA=M\n" + self.__pos_neg() + "@R14\nM=D\n"
        self.pos_neg_counter += 1
        to_write += "@SP\nA=M-1\n" + self.__pos_neg() + "@R14\nM=M+D\n"
        to_write += "D=M\n@DIFFSIGN" + str(self.compare_counter) + "\n" + \
                    "D;JEQ\n@SAMESIGN" + str(self.compare_counter) + "\n" + \
                    "D;JNE\n"
        to_write += self.__same_or_diff(command)
        return to_write

    def __logic(self, command, to_write):
        if command == "and":
            to_write += "// and\n@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n"
        elif command == "or":
            to_write += "// or\n@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n"
        elif command == "not":
            to_write += "// not\n@SP\nAM=M-1\nM=!M\n@SP\nM=M+1\n"
        return to_write

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        if command not in ARITHMETIC:
            return
        to_write = ""
        if command == "add" or command == "sub" or command == "neg":
            to_write = self.__arithmetic(command, to_write)
        elif command == "eq" or command == "gt" or command == "lt":
            to_write = self.__comparison(command, to_write)
        elif command == "and" or command == "or" or command == "not":
            to_write = self.__logic(command, to_write)
        elif command == "shiftleft" or command == "shiftright":
            to_write = self.__shift(command, to_write)
        self.output.write(to_write)

    def __push_to_stack(self, arg):
        to_write = "@SP\nA=M\nM=" + arg + "\n@SP\nM=M+1\n"
        return to_write

    def __write_push(self, segment, index, to_write):
        to_write += "// push " + segment + " " + str(index) + "\n"
        if segment == "constant":
            to_write += "@" + str(index) + \
                        "\nD=A\n" + self.__push_to_stack("D")
        elif segment in POINTERS:
            to_write += "@" + str(index) + "\nD=A\n@" + \
                        translate_dict[segment] + "\nA=D+M\nD=M\n" + \
                        self.__push_to_stack("D")
        elif segment == "static":
            to_write += "@" + self.filename + "." + str(index) + \
                        "\nD=M\n" + self.__push_to_stack("D")
        elif segment == "temp" or segment == "pointer":
            to_write += "@" + str(index) + "\nD=A\n@" + \
                        translate_dict[segment] + "\nA=A+D\nD=M\n" + \
                        self.__push_to_stack("D")
        return to_write

    def __write_pop(self, segment, index, to_write):
        if segment == "constant":
            return
        to_write += "// pop " + segment + " " + str(index) + "\n"
        if segment == "static":
            to_write += "@SP\nAM=M-1\nD=M\n@" + self.filename + "." + \
                        str(index) + "\nM=D\n"
            return to_write
        to_write += "@" + str(index) + "\nD=A\n@" + \
                    translate_dict[segment] + "\n"
        if segment in POINTERS:
            to_write += "A=M\n"
        to_write += "D=D+A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n"
        return to_write

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to static i appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        if command != "C_PUSH" and command != "C_POP":
            return
        to_write = ""
        if command == "C_POP":
            to_write = self.__write_pop(segment, index, to_write)
        elif command == "C_PUSH":
            to_write = self.__write_push(segment, index, to_write)
        self.output.write(to_write)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        pass

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        pass

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        pass

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        pass

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "foo" be a function within the file Xxx.vm.
        The handling of each "call" command within foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
