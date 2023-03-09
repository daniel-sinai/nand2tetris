"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

from JackTokenizer import *
from SymbolTable import *
from VMWriter import *

unary_op = {'-', '~', '^', '#'}
keyword_constant = {'true', 'false', 'null', 'this'}
keyword_statements = {"let", "if", "while", "do", "return"}
keyword_subroutine = {"function", "method", "constructor"}
op = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
op_dict = {'+': "add", '-': "sub", '*': "Math.multiply",
           '/': "Math.divide", '&': "and", '|': "or", '<': "lt", '>': "gt",
           '=': "eq"}
unary_op_dict = {'-': "neg", '~': "not", '^': "shiftleft", '#': "shiftright"}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.writer = VMWriter(output_stream)
        self.table = SymbolTable()
        self.class_name = ""
        self.subroutine_name = ""
        self.while_counter = 0
        self.if_counter = 0

    def __advance(self):
        self.tokenizer.advance()
        return self.tokenizer.current_token

    def __write_push(self, name):
        if name in self.table.subroutine_table.keys():
            if self.table.kind_of(name) == "ARG":
                self.writer.write_push("ARG", self.table.index_of(name))
            elif self.table.kind_of(name) == "VAR":
                self.writer.write_push("LOCAL", self.table.index_of(name))
        else:
            if self.table.kind_of(name) == "STATIC":
                self.writer.write_push("STATIC", self.table.index_of(name))
            elif self.table.kind_of(name) == "FIELD":
                self.writer.write_push("THIS", self.table.index_of(name))

    def __write_pop(self, name):
        if name in self.table.subroutine_table.keys():
            if self.table.kind_of(name) == "ARG":
                self.writer.write_pop("ARG", self.table.index_of(name))
            elif self.table.kind_of(name) == "VAR":
                self.writer.write_pop("LOCAL", self.table.index_of(name))
        else:
            if self.table.kind_of(name) == "STATIC":
                self.writer.write_pop("STATIC", self.table.index_of(name))
            elif self.table.kind_of(name) == "FIELD":
                self.writer.write_pop("THIS", self.table.index_of(name))

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.__advance()  # keyword "class"
        self.__advance()  # get class name
        self.class_name = self.tokenizer.identifier()
        self.__advance()  # symbol "{"
        if self.tokenizer.next_value() == "static" or \
                self.tokenizer.next_value() == "field":
            self.compile_class_var_dec()
        while self.tokenizer.next_value() in keyword_subroutine:
            self.compile_subroutine()
        self.__advance()  # symbol "}"

    def __handle_vars(self):
        self.__advance()  # get var kind
        kind = self.tokenizer.keyword()
        self.__advance()  # get var type
        var_type = self.tokenizer.identifier()
        self.__advance()  # get var name
        name = self.tokenizer.identifier()
        self.table.define(name, var_type, kind.upper())
        while self.tokenizer.next_value() == ",":  # if there are more vars
            self.__advance()  # get "," symbol
            self.__advance()  # get var name
            name = self.tokenizer.identifier()
            self.table.define(name, var_type, kind.upper())
        self.__advance()  # get ";" at the end

    def __write_class_var_dec(self):
        self.__handle_vars()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        while self.tokenizer.next_value() == "static" or \
                self.tokenizer.next_value() == "field":
            self.__write_class_var_dec()

    def __set_pointer(self, subroutine_type):
        if subroutine_type == "method":
            self.writer.write_push("ARG", 0)
            self.writer.write_pop("POINTER", 0)
        elif subroutine_type == "constructor":
            n_vars = self.table.var_count("FIELD")
            self.writer.write_push("CONST", n_vars)
            self.writer.write_call("Memory.alloc", 1)
            self.writer.write_pop("POINTER", 0)

    def compile_subroutine_body(self, subroutine_type):
        self.__advance()  # get symbol "{"
        while self.tokenizer.next_value() == "var":
            self.compile_var_dec()
        n_vars = self.table.var_count("VAR")
        self.writer.write_function(self.subroutine_name, n_vars)
        self.__set_pointer(subroutine_type)
        self.compile_statements()
        self.__advance()  # get symbol "}"

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.__advance()  # get keyword of subroutine type
        subroutine_type = self.tokenizer.keyword()
        self.__advance()  # get return type
        self.__advance()  # get subroutine name
        self.subroutine_name = self.class_name + \
                             "." + self.tokenizer.identifier()
        self.table.start_subroutine()
        self.__advance()  # get symbol "("
        self.compile_parameter_list(subroutine_type)
        self.__advance()  # get symbol ")"
        self.compile_subroutine_body(subroutine_type)

    def __write_single_param(self):
        self.__advance()  # get parameter type
        param_type = self.tokenizer.keyword()
        self.__advance()  # get parameter name
        param_name = self.tokenizer.identifier()
        self.table.define(param_name, param_type, "ARG")
        if self.tokenizer.next_value() == ",":  # if exist more parameters
            self.__advance()  # get symbol ","

    def compile_parameter_list(self, subroutine_type) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        if subroutine_type == "method":
            self.table.define("this", self.class_name, "ARG")
        while self.tokenizer.next_token_type() != "symbol":
            self.__write_single_param()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.__handle_vars()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokenizer.next_value() in keyword_statements:
            if self.tokenizer.next_value() == "let":
                self.compile_let()
            elif self.tokenizer.next_value() == "if":
                self.compile_if()
            elif self.tokenizer.next_value() == "while":
                self.compile_while()
            elif self.tokenizer.next_value() == "do":
                self.compile_do()
            else:
                self.compile_return()

    def compile_subroutine_call(self):
        n_vars = 0
        first_name = last_name = full_name = ""
        self.__advance()  # get subroutine/class/var name
        first_name = self.tokenizer.identifier()
        if self.tokenizer.next_value() == ".":
            self.__advance()  # get symbol "."
            self.__advance()  # get subroutine name
            last_name = self.tokenizer.identifier()
            if first_name in self.table.subroutine_table or \
               first_name in self.table.class_table:
                self.__write_push(first_name)
                n_vars += 1
                full_name = self.table.type_of(first_name) + "." + last_name
            else:
                full_name = first_name + "." + last_name
        else:
            full_name = self.class_name + "." + first_name
            n_vars += 1
            self.writer.write_push("POINTER", 0)
        self.__advance()  # get symbol "("
        n_vars += self.compile_expression_list()
        self.__advance()  # get symbol ")"
        self.writer.write_call(full_name, n_vars)

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.__advance()  # get keyword do
        self.compile_subroutine_call()
        self.writer.write_pop("TEMP", 0)
        self.__advance()  # get symbol ";"

    def __compile__array_index(self, name):
        self.__advance()  # get symbol "["
        self.compile_expression()  # compile expression 1 in the "[]"
        self.__advance()  # get symbol "]"
        self.__write_push(name)  # push array base address
        self.writer.write_arithmetic("add")  # get final address

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.__advance()  # get keyword let
        is_arr = False
        self.__advance()  # get var name
        name = self.tokenizer.identifier()
        if self.tokenizer.next_value() == "[":
            is_arr = True
            self.__compile__array_index(name)
        self.__advance()  # get symbol "="
        self.compile_expression()
        if is_arr:
            self.writer.write_pop("TEMP", 0)
            self.writer.write_pop("POINTER", 1)
            self.writer.write_push("TEMP", 0)
            self.writer.write_pop("THAT", 0)
        else:
            self.__write_pop(name)
        self.__advance()  # get symbol ";"

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.__advance()  # get keyword while
        self.__advance()  # get symbol "("
        label = str(self.while_counter)
        self.while_counter += 1
        self.writer.write_label("WHILE_EXP" + label)
        self.compile_expression()
        self.writer.write_arithmetic("not")
        self.writer.write_if("WHILE_END" + label)
        self.__advance()  # get symbol ")"
        self.__advance()  # get symbol "{"
        self.compile_statements()
        self.writer.write_goto("WHILE_EXP" + label)
        self.writer.write_label("WHILE_END" + label)
        self.__advance()  # get symbol "}"

    def __is_expression(self):
        value = self.tokenizer.next_value()
        return self.tokenizer.next_token_type() == "integerConstant" or \
            self.tokenizer.next_token_type() == "stringConstant" or \
            self.tokenizer.next_token_type() == "identifier" or \
            value in unary_op or value in keyword_constant or value == "("

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.__advance()  # get keyword return
        is_void = True
        while self.__is_expression():
            self.compile_expression()
            is_void = False
        if is_void:
            self.writer.write_push("CONST", 0)
        self.writer.write_return()
        self.__advance()  # get symbol ";"

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        label = str(self.if_counter)
        self.if_counter += 1
        self.__advance()  # get keyword "if"
        self.__advance()  # get symbol "("
        self.compile_expression()
        self.__advance()  # get symbol ")"
        self.writer.write_if("IF_TRUE" + label)
        self.writer.write_goto("IF_FALSE" + label)
        self.writer.write_label("IF_TRUE" + label)
        self.__advance()  # get symbol "{"
        self.compile_statements()
        self.__advance()  # get symbol "}"
        if self.tokenizer.next_value() == "else":
            self.writer.write_goto("IF_END" + label)
            self.writer.write_label("IF_FALSE" + label)
            self.__advance()  # get keyword "else"
            self.__advance()  # get symbol "{"
            self.compile_statements()
            self.__advance()  # get symbol "}"
            self.writer.write_label("IF_END" + label)
        else:
            self.writer.write_label("IF_FALSE" + label)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.tokenizer.next_value() in op:
            self.__advance()  # get the operator symbol
            operator = self.tokenizer.symbol()
            self.compile_term()
            if operator == "*" or operator == "/":
                self.writer.write_call(op_dict[operator], 2)
            else:
                self.writer.write_arithmetic(op_dict[operator])

    def __is_term(self):
        return self.__is_expression()

    def __handle_int_constant(self):
        self.__advance()  # get the integer constant
        integer = self.tokenizer.int_val()
        self.writer.write_push("CONST", integer)

    def __handle_string_constant(self):
        self.__advance()  # get the string constant
        string = self.tokenizer.identifier()
        self.writer.write_push("CONST", len(string))
        self.writer.write_call("String.new", 1)  # create new string
        for letter in string:
            self.writer.write_push("CONST", ord(letter))
            self.writer.write_call("String.appendChar", 2)

    def __handle_keyword_constant(self):
        self.__advance()  # get the keyword constant
        name = self.tokenizer.keyword()
        if name == "this":
            self.writer.write_push("POINTER", 0)
        else:
            self.writer.write_push("CONST", 0)
            if name == "true":
                self.writer.write_arithmetic("not")

    def __handle_method_call(self, name, n_vars):
        self.writer.write_push("POINTER", 0)  # push the object base address
        n_vars += 1
        self.__advance()  # get symbol "("
        n_vars += self.compile_expression_list()
        self.__advance()  # get symbol ")"
        self.writer.write_call(self.class_name + "." + name, n_vars)

    def __handle_subroutine_call(self, name, n_vars):
        self.__advance()  # get symbol "."
        self.__advance()  # get subroutine name
        subroutine_name = self.tokenizer.identifier()
        if name in self.table.subroutine_table or \
                name in self.table.class_table:
            self.__write_push(name)
            name = self.table.type_of(name) + "." + subroutine_name
            n_vars += 1
        else:
            name = name + "." + subroutine_name
        self.__advance()  # get symbol "("
        n_vars += self.compile_expression_list()
        self.__advance()  # get symbol ")"
        self.writer.write_call(name, n_vars)

    def __handle_identifier(self, is_array):
        n_vars = 0
        self.__advance()  # get class/var name
        name = self.tokenizer.identifier()
        if self.tokenizer.next_value() == "[":
            self.__compile__array_index(name)
            is_array = True
        if self.tokenizer.next_value() == "(":
            self.__handle_method_call(name, n_vars)
        elif self.tokenizer.next_value() == ".":
            self.__handle_subroutine_call(name, n_vars)
        else:
            if is_array:
                self.writer.write_pop("POINTER", 1)
                self.writer.write_push("THAT", 0)
            else:
                self.__write_push(name)

    def __handle_unary_op(self):
        self.__advance()  # get the unary operator
        unary = self.tokenizer.symbol()
        self.compile_term()
        self.writer.write_arithmetic(unary_op_dict[unary])

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "."
        suffices to distinguish between the three possibilities. Any other
        token is not part of this term and should not be advanced over.
        """
        is_array = False
        if self.tokenizer.next_token_type() == "integerConstant":
            self.__handle_int_constant()
        elif self.tokenizer.next_token_type() == "stringConstant":
            self.__handle_string_constant()
        elif self.tokenizer.next_value() in keyword_constant:
            self.__handle_keyword_constant()
        elif self.tokenizer.next_token_type() == "identifier":
            self.__handle_identifier(is_array)
        elif self.tokenizer.next_value() in unary_op:
            self.__handle_unary_op()
        elif self.tokenizer.next_value() == "(":
            self.__advance()  # get symbol "("
            self.compile_expression()
            self.__advance()  # get symbol ")"

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        num_of_vars = 0
        if self.__is_expression():
            self.compile_expression()
            num_of_vars += 1
        while self.tokenizer.next_value() == ",":
            self.__advance()  # get symbol ","
            self.compile_expression()
            num_of_vars += 1
        return num_of_vars
