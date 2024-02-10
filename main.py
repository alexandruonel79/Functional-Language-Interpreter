from sys import argv
from .Lexer import Lexer
from .Parser import Lista
from .Interpretor import create_stack, process_stack


def read_file(path) -> str:
    try:
        with open(path, "r") as file:
            file_content = file.read()
            return file_content
    except FileNotFoundError:
        return "File does not exist"

def main():
    # get the argv for checker
    if len(argv) != 2:
        return
    filename = argv[1]
    # the specification
    lexer = Lexer(
        [
            ("Space", "(\\ |\t|\n)+"),
            ("LeftBracket", r"\("),
            ("RightBracket", r"\)"),
            ("Number", r"[0-9]+"),
            ("Lambda", "lambda"),
            ("Id", "[a-z]"),
            ("Plus", r"\+"),
            ("Concat", r"\+\+"),
            ("Colon", r":"),
        ]
    )
    # read the input and get the tokens
    tokens_list = lexer.lex(read_file(filename))
    # the grammar goes from program to list when meeting a left bracket
    if tokens_list[0][0] == "LeftBracket":
        tokens_list.pop(0)
    # create the program, it will return a list
    program = Lista(tokens_list).parse()
    # start the recursive process
    stack = create_stack(program)
    # process the last one
    result = process_stack(stack)
    # print the result
    print(result.generate_output())


if __name__ == "__main__":
    main()
