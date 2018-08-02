#!/bin/bash

tool="./MyAssembler/MyAssembler.py"
golden="../../tools/Assembler.bat"

list="
    ./add/Add.asm
    ./max/Max.asm
    ./max/MaxL.asm
    ./pong/Pong.asm
    ./pong/PongL.asm
    ./rect/Rect.asm
    ./rect/RectL.asm
"

for i in $list ; do
    cygstart $golden $i
    sleep 1
    mv ${i%.asm}.hack ${i%.asm}.golden.hack
done

for i in $list ; do
    $tool $i > /dev/null
    mv ${i%.asm}.hack ${i%.asm}.my.hack
done

for i in $list ; do
    echo $i
    diff -q ${i%.asm}.golden.hack ${i%.asm}.my.hack
done

