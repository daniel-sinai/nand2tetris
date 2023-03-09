"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    An Xxx .jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of space characters,
    newline characters, and comments, which are ignored. There are three
    possible comment formats: /* comment until closing */ , /** API comment
    until closing */ , and // comment until the line’s end.

    ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’);
    xxx: regular typeface is used for names of language constructs
    (‘non-terminals’);
    (): parentheses are used for grouping of language constructs;
    x | y: indicates that either x or y can appear;
    x?: indicates that x appears 0 or 1 times;
    x*: indicates that x appears 0 or more times.

    ** Lexical elements **
    The Jack language includes five types of terminal elements (tokens).
    1. keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
        'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' | 'false'
        | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 'while' | 'return'
    2. symbol:  '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
        '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    3. integerConstant: A decimal number in the range 0-32767.
    4. StringConstant: '"' A sequence of Unicode characters not including
        double quote or newline '"'
    5. identifier: A sequence of letters, digits, and underscore ('_') not
        starting with a digit.


    ** Program structure **
    A Jack program is a collection of classes, each appearing in a separate
    file. The compilation unit is a class. A class is a sequence of tokens
    structured according to the following context free syntax:

    class: 'class' className '{' classVarDec* subroutineDec* '}'
    classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    type: 'int' | 'char' | 'boolean' | className
    subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    subroutineName '(' parameterList ')' subroutineBody
    parameterList: ((type varName) (',' type varName)*)?
    subroutineBody: '{' varDec* statements '}'
    varDec: 'var' type varName (',' varName)* ';'
    className: identifier
    subroutineName: identifier
    varName: identifier


    ** Statements **
    statements: statement*
    statement: letStatement | ifStatement | whileStatement | doStatement |
        returnStatement
    letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
        statements '}')?
    whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    doStatement: 'do' subroutineCall ';'
    returnStatement: 'return' expression? ';'


    ** Expressions **
    expression: term (op term)*
    term: integerConstant | stringConstant | keywordConstant | varName |
        varName '['expression']' | subroutineCall | '(' expression ')' |
        unaryOp term
    subroutineCall: subroutineName '(' expressionList ')' | (className |
        varName) '.' subroutineName '(' expressionList ')'
    expressionList: (expression (',' expression)* )?
    op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    unaryOp: '-' | '~' | '^' | '#'
    keywordConstant: 'true' | 'false' | 'null' | 'this'

    If you are wondering whether some Jack program is valid or not, you should
    use the built-in JackCompiler to compiler it. If the compilation fails, it
    is invalid. Otherwise, it is valid.
    """

    keywords_set = {"class", "constructor", "function", "method",
                      "field", "static", "var", "int", "char", "boolean",
                      "void", "true", "false", "null", "this", "let", "do",
                      "if", "else", "while", "return"}
    symbols_set = {"{", "}", "(", ")", "[", "]", ".", ",", ";", "+",
                     "-", "*", "/", "&", "|", "<", ">", "=", "~", "^", "#"}

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        # input_lines = input_stream.read().splitlines()
        self.__input = input_stream.read()
        self.__og = self.__input
        self.__no_split = self.__clean_source()
        self.__input = self.__clean_source().splitlines()
        self.__cur_line = 0
        self.__lines_tokens = list()
        self.__cur_token_ind = 0
        self.__tokenize_lines()
        self.type_func = {"keyword": self.keyword, "symbol": self.symbol, "integerConstant": self.int_val,
                          "stringConstant": self.string_val, "identifier": self.identifier}

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return self.__cur_line < len(self.__input)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        # Your code goes here!
        if self.__cur_token_ind < len(self.get_line()) - 1:
            self.__cur_token_ind += 1
        else:
            self.__cur_token_ind = 0
            self.__cur_line += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        token = self.get_line()[self.__cur_token_ind]
        if token in JackTokenizer.keywords_set:
            return "keyword"
        elif token in JackTokenizer.symbols_set:
            return "symbol"
        elif token.isnumeric():
            return "integerConstant"
        elif token[0] == '"' and token[-1] == '"':
            return "stringConstant"
        else:
            return "identifier"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.get_line()[self.__cur_token_ind]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!

        token = self.get_line()[self.__cur_token_ind]
        if token == "<":
            return "&lt;"
        elif token == ">":
            return "&gt;"
        elif token == "&":
            return "&amp;"
        else:
            return token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        # Your code goes here!
        return self.get_line()[self.__cur_token_ind]

    def int_val(self) -> str:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        # Your code goes here!
        return self.get_line()[self.__cur_token_ind]

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        # Your code goes here!
        return self.get_line()[self.__cur_token_ind][1:-1]

    def __clean_source(self) -> str:
        """
        function cleans the source empty lines, comments, tabs and redundant spaces
        """
        groups = r"(^[\n\t ]*//[^\n]*\n)|(^[\n \t]*)|(/\*.*?\*/[\n \t]*)|([\n\t ]*//[^\n]*\n)|(\".*?\")|(\t)|" \
                 r"(  +)|([\n \t]+\n)"
        # group 1 = (//[^\n]*\n) - // comments - all line
        # group 2 = (^[\n \t]*) - start spaces
        # group 3 = (/\*.*?\*//n?) - /* comments
        # group 4 = (//[^\n]*\n) - // comments - middle line
        # group 5 = (\".*?\") - for strings
        # group 6 = (\t) - for middle tabs
        # group 7 = (  +) - double space
        # group 8 = ([\n \t]+\n) - end spaces

        regex = re.compile(groups, re.M | re.S)

        def repl(match) -> str:
            if match.group(1) is not None:
                return ""
            elif match.group(2) is not None:
                return ""
            elif match.group(3) is not None:
                return ""
            elif match.group(4) is not None:
                return "\n"
            elif match.group(5) is not None:
                return match.group(5)
            elif match.group(6) is not None:
                return ""
            elif match.group(7) is not None:
                # return match.group(7)[0] + " " + match.group(7)[-1]
                return " "
            elif match.group(8) is not None:
                return "\n"
            return "BUG*BUG*BUG"
        return regex.sub(repl, str(self.__input))

    def __tokenize_lines(self):
        '''create anothe list of lists where each item is a token'''
        for i in range(len(self.__input)):
            if self.__input[i] and self.__input[i] != " ":
                temp_line = re.split(r"(\".*\"|\W)", self.__input[i])
                temp_line = [i.strip() for i in temp_line if i and i != " "]
                self.__lines_tokens.append(temp_line)

    def get_token(self, ahead=0) -> str:
        '''
        return the current token if ahead is 0 and the current + ahead token otherwise
        '''
        if ahead == 0:
            return self.type_func[self.token_type()]()
        else:
            pos = self.__cur_token_ind + ahead
            # handle the case we are at the end of the line
            if pos >= len(self.get_line()):
                return self.__lines_tokens[self.__cur_line + 1][0]
            else:
                return self.get_line()[self.__cur_token_ind + ahead]

    def get_line(self):
        '''
        returning the current line
        '''
        return self.__lines_tokens[self.__cur_line]

