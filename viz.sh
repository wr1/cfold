
#shell2gif -t 0.05 -s 20 -w 125 -h 38 -d 1.8 -o demo.gif

# cfold cli help
cfold -h
clear 

# fold the current project
cfold fold 
clear 

# fold the current project, but only the documentation 
cfold fold -d doc
clear 

# fold a set of files using wildcards
cfold fold src/cfold/*/*py
clear

