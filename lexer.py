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

# define the LOLCode keywords and their classification
LEXEMES_CLASSIFICATION = {
    # code delimeters
    "HAI": "Code Delimeter",
    "KTHXBYE": "Code Delimiter",

    # variable declaration delimeters
    "WAZZUP": "Variable Declaration Delimiter",
    "BUHBYE": "Variable Declaration Delimiter",

    # variable declaration and assignment
    "I HAS A": "Variable Declaration",
    "ITZ": "Variable Assignment",

    # input and output
    "VISIBLE": "Output Keyword",
    "GIMMEH": "Input Keyword",

    # operations
    "SUM OF": "Arithmetic Operator",
    "DIFF OF": "Arithmetic Operator",
    "PRODUKT OF": "Arithmetic Operator",
    "QUOSHUNT OF": "Arithmetic Operator",
    "MOD OF": "Arithmetic Operator",
    "BIGGR OF": "Arithmetic Operator",
    "SMALLR OF": "Arithmetic Operator",
    "BOTH OF": "Boolean Operator",
    "EITHER OF": "Boolean Operator",
    "WON OF": "Boolean Operator",
    "NOT": "Boolean Operator",
    "ALL OF": "Boolean Operator",
    "ANY OF": "Boolean Operator",
    "BOTH SAEM": "Comparison Operator",
    "DIFFRINT": "Comparison Operator",
    "SMOOSH": "String Concatenation Operator",
    "MKAY": "Expression End",
    "AN": "Conjunction",

    # typecasting
    "MAEK": "Explicit Typecasting",
    "IS NOW A": "Type Recasting",
    "A" : "Type Declaration",

    # assignment
    "R": "Assignment Operation",

    # if-then statements
    "O RLY?": "Conditional Start",
    "YA RLY": "If Branch",
    "NO WAI": "Else Branch",
    "OIC": "Statement End",
    "MEBBE": "Else-If Clause",

    # switch-case statements
    "WTF?": "Switch Start", 
    "OMG": "Switch Cases", 
    "OMGWTF": "Default Case",

    # loops
    "IM IN YR": "Loop Start", 
    "IM OUTTA YR": "Loop End",
    "YR": "Loop Variable Reference",
    "TIL": "Loop Until Condition",
    "WILE": "Loop While Condition",
    "UPPIN": "Loop Increment",
    "NERFIN": "Loop Decrement",

    # functions
    "HOW IZ I": "Function Definition",
    "IF U SAY SO": "Function End",
    "I IZ": "Function Call",
    "FOUND YR": "Function Return",
    "GTFO": "Return/Break Statement",

    # general
    "\"": "String Delimeter"
}

# flatten keywords for lookup
KEYWORDS = set(LEXEMES_CLASSIFICATION.keys())

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
    def __init__(self, value, category, line):
        self.value = value
        self.category = category
        self.line = line

    def __repr__(self):
        return f"{self.value}:{self.category}"

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
            cleanedLines.append("") # add it first as an empty string
            continue

        # handle inline comment (remove everything after BTW)
        if "BTW" in line.strip():
            line = line.split("BTW", 1)[0]
        
        cleanedLines.append(line.rstrip("\n")) # to keep original lines and indexes (removed newline in the right-end of each text)
    
    return cleanedLines

# function for tokenizing lexemes per line in file
def tokenize(lines):

    tokens = [] # will hold all the tokens in the file

    for line_num, line in enumerate(lines, start=1):

        # build a token list for the current line
        line_tokens = []

        # split the content of each line except strings
        parts = re.findall(r'"|[^"\s]+', line)

        index = 0
        prev_category = None  # track the last keyword’s category

        while index < len(parts):
            part = parts[index]

            # 01: check for 3-word keyword first
            if index + 2 < len(parts):
                three_word = f"{parts[index]} {parts[index+1]} {parts[index+2]}"  # combine the keywords

                # check if it is part of the defined keywords
                if three_word in KEYWORDS:
                    category = LEXEMES_CLASSIFICATION[three_word]
                    line_tokens.append(Token(three_word, category, line_num)) #append to tokens if it is part of the defined keywords
                    prev_category = category
                    index += 3
                    continue
            
            # 02: check for 2-word keyword 
            if index + 1 < len(parts):
                two_word = f"{parts[index]} {parts[index+1]}"  # combine the keywords

                # check if it is part of the defined keywords
                if two_word in KEYWORDS:
                    category = LEXEMES_CLASSIFICATION[two_word]
                    line_tokens.append(Token(two_word, category, line_num)) #append to tokens if it is part of the defined keywords
                    prev_category = category
                    index += 2
                    continue

            # 03: classify the single tokens
            if part in KEYWORDS:
                category = LEXEMES_CLASSIFICATION[part]
                line_tokens.append(Token(part, category, line_num))
                prev_category = category
            
            elif is_numbr(part) or is_numbar(part) or is_yarn(part) or is_type_literal(part) or is_troof(part):
                line_tokens.append(Token(part, "Literal", line_num))
                prev_category = "Literal"
            
            elif is_identifier(part):
                # identify the type of identifer based on category of preceeding text

                if prev_category in {"Loop Start", "Loop End"}:
                    category = "Loop Identifier"
                elif prev_category in {"Function Definition", "Function Call", "Function Return"}:
                    category = "Function Identifier"
                else:
                    category = "Variable Identifier"  #default case

                line_tokens.append(Token(part, category, line_num))
                prev_category = category
            elif part == '"':
                line_tokens.append(Token(part, "String Delimiter", line_num))
            else:
                pass  #ignore unrecognized tokens
        
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
