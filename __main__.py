# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:35:14 2017

@author: James Bradbury
"""
import argparse
import tools
from interfaces.enzymeAssignment import EnzymeAssignment
from interfaces.databaseExtraction import DatabaseExtraction


def main():
    print("executing METRONOME.")

    parser = argparse.ArgumentParser(description='Pyhton package for',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Model name
    parser.add_argument('-n', '--name',
                        type=str, required=True,
                        help="Name for reconstruction.")

    # Output path
    parser.add_argument('-o', '--outPath',
                        type=str, required=True,
                        help="Path to output folder")

    # Enzyme assignment module
    parser.add_argument('-ea', '--enzymeAssignment',
                        type=str, required=True,
                        help="Path to enzyme assignment module")

    # Enzyme assignment module
    parser.add_argument('-eaf', '--enzymeAssignmentFile',
                        type=str, required=False,
                        help="Path to input file for selected enzyme assignment module (ea argument)")

    args = parser.parse_args()
    print(args)

    # ###### ENZYME ASSIGNMENT ###### #
    # load enzyme assignment classes

    # ea_classes = tools.load_classes('enzymeAssignment', EnzymeAssignment)
    # print(ea_classes)

    # loop through enzyme assignment and call the methods
    # for ea_class in ea_classes:
    #    ea_class.assign_enzymes()
    #    print(ea_class.assigned_enzymes)

    ea_class = tools.load_class(args.enzymeAssignment, EnzymeAssignment)
    ea_class.assign_enzymes(args.enzymeAssignmentFile)

    #load database extractors
    database_extractor_classes = tools.load_classes('databaseExtraction', DatabaseExtraction, ea_class.assigned_enzymes)
    for c in database_extractor_classes:
        x = c.extract_reactions
    #keggExtraction_proto.extract_reactions(ea_class.assigned_enzymes)
    print()


if __name__ == '__main__':
    main()
