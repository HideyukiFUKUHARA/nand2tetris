// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

    @i
    M=0    // i=0
    @R2
    M=0    // R2=0

(LOOP)
    @R1
    D=M     // D = R1
    @i
    D=D-M   // D = R1 - i
    @END
    D;JLE
    @R0
    D=M     // D = R0
    @R2
    M=M+D   // R2 = R2 + R0
    @i
    M=M+1
    @LOOP
    0;JMP
(END)
    @END
    0;JMP
