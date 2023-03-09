"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

ARITHMETIC = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not",
              "shiftleft", "shiftright"}


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        input_file.seek(0)
        self.input_lines = input_file.read().splitlines()
        self.index = 0
        self.current_command = ""
        self.input_lines = [line.replace('\n', '').replace('\t', '') for line
                            in self.input_lines]
        self.input_lines = [line.split("//")[0].strip() for line in
                            self.input_lines]
        self.input_lines = [line for line in self.input_lines if line != '']

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        if self.index == len(self.input_lines):
            return False
        return True

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true.
        Initially there is no current command.
        """
        # Your code goes here!
        self.current_command = self.input_lines[self.index]
        self.index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Your code goes here!
        if self.current_command in ARITHMETIC:
            return "C_ARITHMETIC"
        elif self.current_command.startswith("push"):
            return "C_PUSH"
        elif self.current_command.startswith("pop"):
            return "C_POP"
        elif self.current_command.startswith("label"):
            return "C_LABEL"
        elif self.current_command.startswith("goto"):
            return "C_GOTO"
        elif self.current_command.startswith("if-goto"):
            return "C_IF"
        elif self.current_command.startswith("function"):
            return "C_FUNCTION"
        elif self.current_command == "return":
            return "C_RETURN"
        elif self.current_command.startswith("call"):
            return "C_CALL"
        return ""

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!
        if self.command_type() == "C_RETURN":
            return ""
        if self.command_type() == "C_ARITHMETIC":
            return self.current_command
        split = self.current_command.split()
        return split[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        if self.command_type() != "C_PUSH" and self.command_type() != "C_POP" \
                and self.command_type() != "C_FUNCTION" \
                and self.command_type() != "C_CALL":
            return -1

        return int(self.current_command.split()[2])
