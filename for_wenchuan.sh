#!/bin/bash
# the way
../bin/ertid <<EOF 
2010 1 0 
2012 1 0
0.03333333333333333
t 
31.1
103.7
0 
0 
2
0
90
azi0
azi90
EOF
paste azi0 azi90 > xue_tides_2021