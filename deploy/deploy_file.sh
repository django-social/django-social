#!/bin/bash
cd ..

#for I in 1
for I in {2..7}
do
    for FILE in $@ 
    do
        scp $FILE appserver@as$I.modnoemesto.ru:~/app/$FILE
    done
done

