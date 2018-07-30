// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
(ADDRESSINIT)
    @SCREEN
    D=A
    @address
    M=D
(SCAN)
    @KBD
    D=M
    @SETWHITE
    D;JEQ
(SETBLACK)
    @color
    M=-1
    @DISPLAY
    0;JMP
(SETWHITE)
    @color
    M=0
(DISPLAY)
    @color
    D=M
    @address
    A=M
    M=D
    @address
    M=M+1   // i + 1
    D=M
    @24576  //8192+16384
    D=A-D
    @ADDRESSINIT
    D;JEQ
    @SCAN
    0;JMP
(END)    
    @END
    0;JMP
