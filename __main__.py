# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:35:14 2017

@author: James Bradbury
"""
import argparse
from . import __version__
       
def main():
    print("executing METRONOME version %s." % __version__)
    
    parser = argparse.ArgumentParser(description='Pyhton package for', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    subparsers = parser.add_subparsers(dest='step')
    
    parser_ea = subparsers.add_parser('enzyme-assignment', help='Assign enzymes to input sequence')
    parser_dm = subparsers.add_parser('data-mining', help='mine enzymatic reactions')
    parser_m = subparsers.add_parser('merging', help='merge the reactions from the different data mining sources using MetaNetX')

    ##################################
    # Enzyme Assignment
    ##################################
    
    ##################################
    # Data mining
    ##################################
    
    ##################################
    # Merging
    ##################################
    
    
    args = parser.parse_args()
    
    print(args)
    
    if args.step == "enzyme-assignment":
        print('ENZMYE ASSIGNMENT')
    elif args.step == "data-mining":
        print('DATA MINING')
    elif args.step == "merging":
        print('MERGING')
        
if __name__ == '__main__':
    main()