"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

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
        self.input_lines = [line.replace(' ', '') for line in self.input_lines]

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
         command.
        Should be called only if has_more_commands() is true.
        """
        # Your code goes here!
        self.current_command = self.input_lines[self.index]
        self.index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal
             number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a
             symbol
        """
        # Your code goes here!
        if self.current_command.startswith("@"):
            return "A_COMMAND"
        elif self.current_command.startswith("("):
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!
        if self.command_type() == "C_COMMAND":
            return ""
        symbol = ""
        if self.current_command.startswith("@"):
            symbol = self.current_command.split("@")[1]
        elif self.current_command.startswith("("):
            symbol = self.current_command.split("(")[1].rstrip(")")
        return symbol

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if self.command_type() == "A_COMMAND" or \
                self.command_type() == "L_COMMAND" or \
                "=" not in self.current_command:
            return ""
        return self.current_command.split("=")[0]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if self.command_type() == "A_COMMAND" or \
                self.command_type() == "L_COMMAND":
            return ""
        temp = []
        if "=" in self.current_command and ";" not in self.current_command:
            temp = self.current_command.split("=")
        elif ";" in self.current_command and "=" not in self.current_command:
            temp = self.current_command.split(";")
            return temp[0]
        elif "=" in self.current_command and ";" in self.current_command:
            temp = self.current_command.split("=")[1].split(";")
            return temp[0]
        return temp[1]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        if self.command_type() == "A_COMMAND" or \
                self.command_type() == "L_COMMAND" or \
                ";" not in self.current_command:
            return ""
        temp = []
        if ";" in self.current_command and "=" not in self.current_command:
            temp = self.current_command.split(";")
            return temp[1]
        elif "=" in self.current_command and ";" in self.current_command:
            temp = self.current_command.split("=")[1].split(";")
            return temp[1]
        return ""
