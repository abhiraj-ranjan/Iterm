#!/bin/bash
while getopts p:g: flag
do
    case "${flag}" in
        p) python=${OPTARG};;
        g) get=${OPTARG};;
    esac
done

if [ "$get" = "os" ]
then
    echo `$python ../scripts/get_backend.py os`;
else
    echo `$python ../scripts/get_backend.py backend`;
fi

