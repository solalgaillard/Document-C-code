# Document-C-code
Program that documents ANSI C code

Takes as arguments as many C files as wanted.

List all functions, global variables, file inclusions, typedef with their call, declaration, assignment, etc...

What it doesn't do:
1- if variable name and functions are the same, the name will be recorded as a function.
2- Structs are not dealt with.
3- No analysis of what functions call what variables or other functions.
4- variable types are poorly dealt with when composed of many words as in "unsigned char" for exemple.

What it takes care of:
1- line continuation with forward slash
2- Parse out double backslash comments
3- Dictionanary organization of all functions and global variables, notably declaration, assignment, type, call referencing and for functions, their parameters lists and their types.

Exemple Output:

File name: cx19.2.c

0001: inclusion ---> stdio.h

0002: inclusion ---> stdlib.h

0003: inclusion ---> string.h

0005: typedef ---> type: char *, alias: str

Functions:

Name usage    Type: void
Parameters:
    Parameter 1    Name: None    Type: str
Initialisation: 0007    Definition: 0030
Referencing:
    0034

Name main    Type: int
Parameters:
    Parameter 1    Name: k    Type: int
    Parameter 2    Name: LDC[]    Type: const str
Initialisation: 0019    Definition: 0019
Referencing:
    No referencing
    
.........

Name: PC    Type: unsigned char    Value: 0x00
Initialisation: 0021 Assignment: 0021
Referencing:
    0042, 0050, 0051, 0052, 0100, 0104, 0105, 0106, 0106, 0108, 0108, 0111, 0111, 0113, 0114, 0115, 0116, 0117, 0118, 0121, 0122, 0123, 0124, 0125, 0126, 0127, 0130, 0131, 0132, 0133, 0135, 0144, 0150, 0154, 0158, 0189, 0192, 0194, 0244, 0245, 0245, 0251, 0251, 0255, 0260, 0260, 0261

Name: run_through    Type:  int    Value: 0
Initialisation: 0024 Assignment: 0024
Referencing:
    0192, 0193, 0206
    
 ......


