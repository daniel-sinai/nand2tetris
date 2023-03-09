"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing
import re

KEYWORDS = {"class", "constructor", "function", "method", "field", "static",
            "var", "int", "char", "boolean", "void", "true", "false", "null",
            "this", "let", "do", "if", "else", "while", "return"}

SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
           '&', '|', '<', '>', '=', '~', '^', '#'}

INT = range(32768)


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
        'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
        'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 'while' |
         'return'
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

    # Regex
    int_regex = r'\d+'
    strings_regex = r'"[^"\n]*"'
    keywords_regex = '(?!\w)|'.join(KEYWORDS) + '(?!\w)'
    symbols_regex = '[' + re.escape('|'.join(SYMBOLS)) + ']'
    identifiers_regex = r'[\w]+'
    single_word = re.compile(keywords_regex + '|' + symbols_regex + '|' +
                             int_regex + '|' + strings_regex + '|' +
                             identifiers_regex)

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_lines = input_stream.read()
        self.current_token = ()
        self.__remove_comments()
        self.tokens = [self.__get_token(word) for word
                       in self.__my_split(self.input_lines)]
        self.index = 0

    def __remove_comments(self):
        cur_index = 0
        end_index = 0
        filtered_text = ""
        while cur_index < len(self.input_lines):
            cur_char = self.input_lines[cur_index]
            if cur_char == "\"":
                end_index = self.input_lines.find("\"", cur_index + 1)
                filtered_text += self.input_lines[cur_index:end_index + 1]
                cur_index = end_index + 1
            elif cur_char == "/":
                if self.input_lines[cur_index + 1] == "/":
                    end_index = self.input_lines.find("\n", cur_index + 1)
                    cur_index = end_index + 1
                    filtered_text += " "
                elif self.input_lines[cur_index + 1] == "*":
                    end_index = self.input_lines.find("*/", cur_index + 1)
                    cur_index = end_index + 2
                    filtered_text += " "
                else:
                    filtered_text += self.input_lines[cur_index]
                    cur_index += 1
            else:
                filtered_text += self.input_lines[cur_index]
                cur_index += 1
        self.input_lines = filtered_text

    def __my_split(self, line):
        return self.single_word.findall(line)

    def __get_token(self, word):
        if re.match(self.keywords_regex, word) is not None:
            return "keyword", word
        elif re.match(self.symbols_regex, word) is not None:
            return "symbol", word
        elif re.match(self.int_regex, word) is not None:
            return "integerConstant", word
        elif re.match(self.strings_regex, word) is not None:
            return "stringConstant", word[1:-1]
        return "identifier", word

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.tokens != []

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.current_token = self.tokens.pop(0)

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        return self.current_token[0]

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.token_type() == "keyword":
            return self.current_token[1]
        return ""

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        if self.token_type() == "symbol":
            return self.current_token[1]
        return ""

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        if self.token_type() == "identifier":
            return self.current_token[1]
        return ""

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        if self.token_type() == "integerConstant":
            return int(self.current_token[1])
        return -1

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        if self.token_type() == "stringConstant":
            return self.current_token[1]
        return ""

    def next_value(self):
        if self.has_more_tokens():
            return self.tokens[0][1]

    def next_token_type(self):
        if self.has_more_tokens():
            return self.tokens[0][0]
