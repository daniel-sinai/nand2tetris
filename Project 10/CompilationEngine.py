"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    var_dec_set = {"static", "field"}
    sub_dec_set = {"constructor", "function", "method"}
    statment_set = {"let", "do", "if", "else", "while", "return"}
    op_set = {"+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="}
    unaryop_set = {"~", "-", "^", "#"}

    def __init__(self, input_stream: JackTokenizer, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        self.__tokenizer = input_stream
        self.__output_stream = output_stream
        self.__statment_dict = {"let": self.compile_let, "do": self.compile_do, "if": self.compile_if,
                                "return": self.compile_return, "while": self.compile_while}

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        # write class

        # write the start label
        self.__write("<class>\n")
        # write class, className, '{' - X3
        self.__write_token(3)
        # inner class compilation
        while self.__get_token() in CompilationEngine.var_dec_set:
            self.compile_class_var_dec()
        while self.__get_token() in CompilationEngine.sub_dec_set:
            self.compile_subroutine()
        # write '}'
        self.__write_token()
        # write the end label
        self.__write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!

        # write the start label
        self.__write("<classVarDec>\n")
        # write static\field, type, varName - X3
        self.__write_token(3)
        # write additional varname(s)
        while self.__get_token() != ";":
            # write ",", varName
            self.__write_token(2)
        # write ";"
        self.__write_token()
        # write the end label
        self.__write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!

        # write the start label
        self.__write("<subroutineDec>\n")
        # write constructor\function\method, void\type, subroutineName, "(" - 4X
        self.__write_token(4)
        # write parameter list if not empty
        self.compile_parameter_list()
        # write ")"
        self.__write_token()
        # write the start label
        self.__write("<subroutineBody>\n")
        # write "{"
        self.__write_token()
        # compile vecDec
        while self.__get_token() == "var":
            self.compile_var_dec()
        # compile statements
        self.compile_statements()
        # write "}"
        self.__write_token()
        # write the end label
        self.__write("</subroutineBody>\n")
        # write the end label
        self.__write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!

        # write the start label
        self.__write("<parameterList>\n")
        # if the parameter list is not empty
        if self.__get_token() != ")":
            # write type, varName - 2x
            self.__write_token(2)
            # additional parameters
            while self.__get_token() != ")":
                # write ",", type, varName
                self.__write_token(3)
        # write the end label
        self.__write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!

        # write the start label
        self.__write("<varDec>\n")
        # write var, type, varName - X3
        self.__write_token(3)
        # additional varNames
        while self.__get_token() != ";":
            # write ",", varName - 2x
            self.__write_token(2)
        # write ";"
        self.__write_token()
        # write the end label
        self.__write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # write the start label
        self.__write("<statements>\n")
        # Your code goes here!
        while self.__get_token() in CompilationEngine.statment_set:
            self.__statment_dict[self.__get_token()]()
        # write the end label
        self.__write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!

        # write the start label
        self.__write("<doStatement>\n")
        # write do
        self.__write_token()
        # write subroutine call
        self.__subroutinecall()
        # write ";"
        self.__write_token()
        # write the end label
        self.__write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        # write the start label
        self.__write("<letStatement>\n")
        # write let and varName - 2x
        self.__write_token(2)
        # if array
        if self.__get_token() == "[":
            # write "["
            self.__write_token()
            # compile expression
            self.compile_expression()
            # write "]"
            self.__write_token()
        # write "="
        self.__write_token()
        # write expression
        self.compile_expression()
        # write ";"
        self.__write_token()
        # write the end label
        self.__write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!

        # write the start label`
        self.__write("<whileStatement>\n")
        # write while, ( - 2X
        self.__write_token(2)
        # write expression
        self.compile_expression()
        # write ")", "{" - 2X
        self.__write_token(2)
        # write statements
        self.compile_statements()
        # write "}"
        self.__write_token()
        # write the end label
        self.__write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!

        # write the start label
        self.__write("<returnStatement>\n")
        # write return
        self.__write_token()
        # write expression if not empty
        if self.__get_token() != ";":
            self.compile_expression()
        # write ";"
        self.__write_token()
        # write the end label
        self.__write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!

        # write the start label
        self.__write("<ifStatement>\n")
        # write if, '(' - 2x
        self.__write_token(2)
        # write expression
        self.compile_expression()
        # write ')', '{' - 2x
        self.__write_token(2)
        # write statments
        self.compile_statements()
        # write '}'
        self.__write_token()
        # if there is else cond
        if self.__get_token() == "else":
            # write else, "{" - 2x
            self.__write_token(2)
            # write statments
            self.compile_statements()
            # write "}"
            self.__write_token()
        # write the end label
        self.__write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!

        # write the start label
        self.__write("<expression>\n")
        # write term
        self.compile_term()
        # additional op and term
        while self.__get_token() in CompilationEngine.op_set:
            # write op
            self.__write_token()
            # write term
            self.compile_term()
        # write the end label
        self.__write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!

        # write the start label
        self.__write("<term>\n")
        token = self.__get_token()
        next_token = self.__get_token(1)
        # expression case
        if token == "(":
            # write "("
            self.__write_token()
            # compile expression
            self.compile_expression()
            # write ")"
            self.__write_token()
        # array case
        elif next_token == "[":
            # write varName
            self.__write_token()
            self._array()
        # unary case
        elif token in CompilationEngine.unaryop_set:
            # write unary
            self.__write_token()
            # write term
            self.compile_term()
        # subroutine call case
        elif next_token == "(" or next_token == ".":
            self.__subroutinecall()
        # identifier case
        else:
            # write identefier
            self.__write_token()
        # write the end label
        self.__write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # write the start label
        self.__write("<expressionList>\n")
        if self.__get_token() != ")":
            # write expression
            self.compile_expression()
        while self.__get_token() != ")":
            # write ","
            self.__write_token()
            # write expression
            self.compile_expression()
        # write the end label
        self.__write("</expressionList>\n")

    def __write(self, string: str) -> None:
        self.__output_stream.write(string)

    def __write_token(self, amount=1) -> None:
        '''
        the function write the next token and advance to the next one
        '''
        for i in range(amount):
            type = self.__tokenizer.token_type()
            token = self.__get_token()
            self.__write("<" + type + ">" + " " + token + " " + "</" + type + ">\n")
            self.__tokenizer.advance()

    def __get_token(self, ahead=0):
        '''
        return the current token if ahead is 0 and the current + ahead token otherwise
        '''
        return self.__tokenizer.get_token(ahead)

    def __subroutinecall(self):
        # subroutine call case
        next_token = self.__get_token(1)
        if next_token == ".":
            # write className\varName, "." - 2x
            self.__write_token(2)
        # write subroutinename, "(" - 2x
        self.__write_token(2)
        # write expression
        self.compile_expression_list()
        # write ")"
        self.__write_token()

    def _array(self):
        # array case
        next_token = self.__get_token(1)
        # write "["
        self.__write_token()
        # compile expression
        self.compile_expression()
        # write "]"
        self.__write_token()
