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

    # for switch-case
    "WTF?", "OMG", "OMGWTF", "OIC", 

    # for loops and function
    "YR", "TIL", "WILE", "UPPIN", "NERFIN",

    "MEBBE",    # for if-else          
    "NOT",  # for operations
    "DIFFRINT", # for operations
    "SMOOSH",   # for operations
    "AN"    # for operations
    "MKAY", # for operations
    "MAEK", # for typecasting
    "A",    # for typecasting
}

# for multi-word keywords
COMBINED_KEYWORDS = {
    # for if-else
    "O RLY?",
    "YA RLY",
    "NO WAI",

    # for operations
    "SUM OF",
    "DIFF OF",
    "PRODUKT OF",
    "QUOSHUNT OF",
    "MOD OF",
    "BIGGR OF",
    "SMALLR OF",
    "BOTH OF",
    "EITHER OF",
    "WON OF",
    "ALL OF",
    "ANY OF",
    "BOTH SAEM",

    # for typecasting
    "IS NOW A"

    # for loops
    "IM IN YR", "IM OUTTA YR", 
    
    # for functions (definition, calling, and return)
    "HOW IZ I", "IF U SAY SO", "FOUND YR", "I IZ"

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
                pass  # ignore unrecognized tokens
        
            index += 1 # go to next line

        if line_tokens:  # only add if tokens exist
            tokens.append((line_num, line_tokens))

    return tokens

# main program
def main():
    filename = input("\nPlease input your LOL filename: ")
    lines = readInputFile(filename)
    # remove comments first before tokenizing
    cleanedLines = removeComments(lines)

    tokenized = tokenize(cleanedLines)

    print("\nTOKENS (per line):\n")
    # traverse the tokens to print
    for index, line in tokenized:
        if line:  # skip empty lists
            print(f"Line {index}: [{', '.join(str(token) for token in line)}]")

# run main program
main()