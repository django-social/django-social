#!/bin/bash
# скрипт для выполнения fab команд на аппсерверах с временным отключением от балансеров
# если первый агрумент wait - ждёт нажатия клавиши после каждого сервера

if [ "$1" = "wait" ]
then
    WAIT="yes"
    shift
fi

for I in {2..7}
do
    fab -R bal bal_disable_server:$I
    fab -H as$I.modnoemesto.ru $@
    fab -R bal bal_enable_server:$I

    if [ "$WAIT" = "yes" ]
    then
        echo press any key for continue at as$(( $I + 1 )) or ^C for interrupt
        read
    fi
done

