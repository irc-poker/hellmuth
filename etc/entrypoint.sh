#!/usr/bin/env ash

mkdir ~/.sopel/

ln -s /modules ~/.sopel/

for f in /state/*
do
    ln -s $f /home/hellmuth/.sopel/
done

sopel

