"""
    Submitted by ALGOLORDS from CMSC 124 - ST3L

    LEDESMA, Jhuliana
    MANAOAT, Tanya Marinelle
    TIAMZON, Edgar Allan Emmanuel III

--------------------------------------------------------------------------------
LEXICAL ANALYZER

This program tokenizes lexemes and ignore comments given an input LOL file.
It returns a list identifying the lexemes in the file.

--------------------------------------------------------------------------------
"""
import re

# ----- TOKENS ------

# define the LOLCode keywords
KEYWORDS = {
    "HAI", "KTHXBYE", "GTFO",
    "WTF?", "OMG", "OMGWTF", "OIC", 
    "YR", "TIL", "WILE", "UPPIN", "NERFIN", "AN YR"
}

# for multi-word keywords
COMBINED_KEYWORDS = {
    "IM IN YR", "IM OUTTA YR", "HOW IZ I", "IF U SAY SO", "FOUND YR", "I IZ"
}

# helper functions in matching literals and identifiers
def is_numbr(token):
    return re.fullmatch(r"-?\d+", token) is not None

def is_numbar(token):
    return re.fullmatch(r"-?\d+\.\d+", token) is not None

def is_yarn(token):
    return re.fullmatch(r"\".*\"", token) is not None

def is_troof(token):
    return token in {"WIN", "FAIL"}

def is_type_literal(token):
    return token in {"NOOB", "NUMBR", "NUMBAR", "YARN", "TROOF"}

def is_identifier(token):
    return re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", token) is not None


# Token class -- defines how the tokens are displayed when printed
class Token:
    def __init__(self, token_type, value, line):
        self.type = token_type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"{self.type}: {self.value}"

# for reading input LOL file
def readInputFile(filename):
    with open(filename, "r") as file:
        return file.readlines()

# helper function to remove comments
def removeComments(lines):

    cleanedLines = []
    in_block_comment = False

    # traverse each line in file
    for line in lines:

        # look first for in-block comments
        if "OBTW" in line.strip():
            in_block_comment = True
        
        # if found, look for position/line on where it ends and skip
        if in_block_comment:
            if "TLDR" in line.strip():
                in_block_comment = False
            continue

        # handle inline comment (remove everything after BTW)
        if "BTW" in line.strip():
            line = line.split("BTW", 1)[0]
        
        cleanedLines.append(line)
    
    return cleanedLines

# function for tokenizing lexemes per line in file
def tokenize(lines):

    tokens = [] # will hold all the tokens in the file

    for line_num, line in enumerate(lines, start=1):

        # build a token list for the current line
        line_tokens = []

        # split the content of each line except strings
        parts = re.findall(r'"[^"]*"|[\w\?\!\-]+|[^\s]', line)

        index = 0
        while index < len(parts):
            part = parts[index]

            # 01: check for 3-word keyword first
            if index + 2 < len(parts):
                three_word = f"{parts[index]} {parts[index+1]} {parts[index+2]}"  # combine the keywords

                # check if it is part of the defined keywords
                if three_word in COMBINED_KEYWORDS:
                    line_tokens.append(Token("Keyword", three_word, line_num)) #append to tokens if it is
                    index += 3
                    continue
            
            # 02: check for 2-word keyword 
            if index + 1 < len(parts):
                two_word = f"{parts[index]} {parts[index+1]}"  # combine the keywords

                # check if it is part of the defined keywords
                if two_word in COMBINED_KEYWORDS:
                    line_tokens.append(Token("Keyword", two_word, line_num)) #append to tokens if it is
                    index += 2
                    continue

            # 03: classify the single tokens
            if part in KEYWORDS:
                line_tokens.append(Token("Keyword", part, line_num))
            elif is_numbr(part) or is_numbar(part) or is_yarn(part) or is_type_literal(part) or is_troof(part):
                line_tokens.append(Token("Literal", part, line_num))
            elif is_identifier(part):
                line_tokens.append(Token("Identifier", part, line_num))
            else:
                pass  #ignore unrecognized tokens
        
            index += 1 # go to next line

        if line_tokens:  # only add if tokens exist
            tokens.append((line_num, line_tokens))

    return tokens

'''
Tokenizes LOLCode user input statements (GIMMEH varident) 
Based on grammar: <input> ::= gimmeh varident <linebreak>
'''
def tokenize_user_input(lines):
    tokens = []  # list to store all (line number, token list) pairs

    # Enumerate over all lines with their line numbers (starting from 1)
    for line_num, line in enumerate(lines, start=1):
        parts = line.strip().split()  # split the line into words, removing extra spaces

        # Check if the line begins with the keyword "GIMMEH" and has at least one identifier after it
        if len(parts) >= 2 and parts[0].upper() == "GIMMEH":

            # Create two tokens:
            # 1. "GIMMEH" as a Keyword
            # 2. The next word (the variable name) as an Identifier
            tokens.append((line_num, [
                Token("Keyword", "GIMMEH", line_num),
                Token("Identifier", parts[1], line_num)
            ]))

    return tokens

'''
Tokenizes LOLCode user output statements (VISIBLE ...)
Based on grammar: <print> ::= VISIBLE varident | VISIBLE <expr> | VISIBLE <literal>
'''
def tokenize_user_output(lines):
    tokens = []  # list to store all (line number, token list) pairs

    # Enumerate through each line of the code
    for line_num, line in enumerate(lines, start=1):
        # Split the line into two parts:
        # parts[0] = first word (should be "VISIBLE")
        # parts[1] = everything after it (the expression or literal)
        parts = line.strip().split(maxsplit=1)

        # Check if the first word is the keyword "VISIBLE"
        if len(parts) >= 1 and parts[0].upper() == "VISIBLE":
            # Start building the token list for this line
            line_tokens = [Token("Keyword", "VISIBLE", line_num)]

            # If there’s something after "VISIBLE", classify what it is
            if len(parts) > 1:
                expr = parts[1]  # everything after VISIBLE

                # Check if expr matches a literal (string, number, or troof)
                if is_yarn(expr) or is_numbar(expr) or is_numbr(expr) or is_troof(expr):
                    line_tokens.append(Token("Literal", expr, line_num))

                # If not a literal, check if it’s a variable identifier
                elif is_identifier(expr):
                    line_tokens.append(Token("Identifier", expr, line_num))

                # Otherwise, treat it as a complex expression (e.g., SUM OF ...)
                else:
                    line_tokens.append(Token("Expression", expr, line_num))

            # Add this line’s tokens to the overall token list
            tokens.append((line_num, line_tokens))

    # Return all user output tokens found in the LOLCode file
    return tokens

'''
Tokenizes LOLCode variable declarations and assignments.
Based on grammar:
<declaration> ::= I HAS A varident [ITZ <expr>] <linebreak>
<assignment>  ::= varident R <expr> <linebreak>
'''
def tokenize_variables(lines):
    tokens = []  # list to store all variable-related tokens

    # Iterate through each line of LOLCode
    for line_num, line in enumerate(lines, start=1):
        parts = line.strip().split()  # split the line into words

        # Case 1: Variable Declaration
        if len(parts) >= 3 and parts[0].upper() == "I" and parts[1].upper() == "HAS" and parts[2].upper() == "A":
            # Begin a token list for this line
            line_tokens = [
                Token("Keyword", "I HAS A", line_num),  # "I HAS A" is treated as a declaration keyword
                Token("Identifier", parts[3], line_num)  # The next word is the variable name
            ]

            # If "ITZ" appears, there’s an initial value assigned
            if len(parts) > 4 and parts[4].upper() == "ITZ":
                # Combine the rest of the line into a single expression string
                expr = " ".join(parts[5:])
                # Add tokens for the ITZ keyword and its expression value
                line_tokens.append(Token("Keyword", "ITZ", line_num))
                line_tokens.append(Token("Expression", expr, line_num))

            # Add the declaration tokens to the list
            tokens.append((line_num, line_tokens))

        # Case 2: Variable Assignment
        elif len(parts) >= 3 and parts[1].upper() == "R":
            varname = parts[0]             # first word is the variable name
            expr = " ".join(parts[2:])     # everything after 'R' is the expression

            # Create tokens for identifier, assignment keyword, and expression
            line_tokens = [
                Token("Identifier", varname, line_num),  
                Token("Keyword", "R", line_num),         
                Token("Expression", expr, line_num)      
            ]

            # Add assignment tokens to the list
            tokens.append((line_num, line_tokens))

    return tokens

# main program
def main():
    filename = input("\nPlease input your LOL filename: ")
    lines = readInputFile(filename)
    # remove comments first before tokenizing
    cleanedLines = removeComments(lines)

    tokenized = tokenize(cleanedLines)
    user_input_tokens = tokenize_user_input(cleanedLines)
    user_output_tokens = tokenize_user_output(cleanedLines)
    variable_tokens = tokenize_variables(cleanedLines)

    print("\nTOKENS (per line):\n")
    # traverse the tokens to print
    for index, line in tokenized:
        if line:  # skip empty lists
            print(f"Line {index}: [{', '.join(str(token) for token in line)}]")

    print("\nUSER INPUT TOKENS (per line):\n")
    for index, line in user_input_tokens:
        print(f"Line {index}: [{', '.join(str(token) for token in line)}]")

    print("\nUSER OUTPUT TOKENS (per line):\n")
    for index, line in user_output_tokens:
        print(f"Line {index}: [{', '.join(str(token) for token in line)}]")

    print("\nVARIABLE TOKENS (per line):\n")
    for index, line in variable_tokens:
        print(f"Line {index}: [{', '.join(str(token) for token in line)}]")


# run main program
main()
