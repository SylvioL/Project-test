#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue March 7 2017

@author: LAVENTURE Sylvio
"""

import sys

def sum_list(a, b):
    """
    Function to sum 2 lists
    """
    
    c = []
    for i in range(len(a)):
        c.append(a[i]+b[i])
    
    return c

def open_files(files):
    """
    Function to open and read a file. It return a list. 
    """
    
    input_line = [] # Variable to stock input lines
    # Open the input file
    f_in = open(files, 'r')
    for line in f_in:
        input_line.append(line.replace('\n','').replace('\r','')) # Stock input line
    f_in.close()
    
    return input_line
    
if __name__ == "__main__":    
    
    if len(sys.argv) == 1:
    
        print "example : python %s /path/to/the/file_parameters "%sys.argv[0]
        sys.exit(-1)
        
    elif len(sys.argv) == 2:
        
        input_files = sys.argv[1]
        
        f_line = open_files(input_files)
        
        # Cardinal command
        card_cmd = ['N', 'E', 'S', 'W']
        index_card = 0 # Initialization : North = 0
        coord_cmd = [[0,1], [1,0], [-1,0], [0,-1]] # Coordinate movement
        
        # Grid size
        grid_size = [int(x) for x in f_line[0].split(' ')]
        
        # Hooker's position
        i_pos = [int(x) for x in f_line[1].split(' ')[:2]]
        i_direction = f_line[1].split(' ')[2]
        
        # Movement
        move = [x for x in f_line[2]]
        
        # Loop on movement
        for m in move:
            
            index_card = card_cmd.index(i_direction)
                
            if m == 'D':
                # Condition for the border
                if index_card == len(card_cmd)-1:
                    index_card = -1 # Transform the extent in loop
                i_direction = card_cmd[index_card + 1]
            elif m == 'G':
                i_direction = card_cmd[index_card - 1]
            else:
                i_pos = sum_list(i_pos, coord_cmd[index_card])
                
        print "%d %d %s"%(i_pos[0],i_pos[1],i_direction)
        
    else:
        
        print "There are too many parameters !"
        