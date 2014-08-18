#!/bin/bash

# Script to loop over te sources in file test_sources.txt and test if they 
#  exist on some catalogues

FILE="test_sources.csv"
CMD="python ../conesearch.py" 
cats=$($CMD --list)
for cat in $cats
do
    echo "---"
    echo "-> Running searches for catalog $cat"
    while IFS=, read src ra dec
    do
        echo " -> looking for source $src ($ra , $dec)"
        ${CMD} --catalog "$cat" --ra "$ra" --dec "$dec" --radius 5 --runit arcsec --short
        echo "-"
    done < ${FILE}
    echo "---"
    echo ""
done
