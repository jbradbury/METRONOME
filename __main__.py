# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:35:14 2017

@author: James Bradbury
"""
import argparse
from enzymeAssignment import orthoMCL
       
def main():
    print("executing METRONOME.")
    
    parser = argparse.ArgumentParser(description='Pyhton package for', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Model name
    parser.add_argument('-n', '--name',
                          type=str, required=True,
                          help="Name for reconstruction.")
    
    # Enzyme assignment class directory
    parser.add_argument('-e', '--enzymeAssignment',
                        type=str, default= '/enzymeAssingment',
                        help="Path to enzyme assignment class directory")

    args = parser.parse_args()
    print(args)
    
    ##### ENZYME ASSIGNMENT #####
    # dynamic class loading
    print(args.enzymeAssignment)
    
    #o = orthoMCL.OrthoMCL()
    #o.test()
    
        
if __name__ == '__main__':
    main() 