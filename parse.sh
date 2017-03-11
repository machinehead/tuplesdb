#!/bin/bash

cat $1 | sed -r 's/NumberLong\(([0-9]+)\)/\1/g' | python parseresult.py
