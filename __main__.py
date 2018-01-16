# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:35:14 2017

@author: James Bradbury
"""
import argparse
import tools
from sbml import sbml
from interfaces.enzymeAssignment import EnzymeAssignment
from interfaces.databaseExtraction import DatabaseExtraction


def main():
    print("executing METRONOME.")

    args = parse_arguments()
    print(args)

    # ###### ENZYME ASSIGNMENT ###### #
    ea_class = tools.load_class(args.enzymeAssignment, EnzymeAssignment)
    ea_class.assign_enzymes(args.enzymeAssignmentFile)

    # ###### DATABASE EXTRACTION  ### #
    # load database extractors
    database_extractor_classes = tools.load_classes('databaseExtraction', DatabaseExtraction, ea_class.assigned_enzymes)
    for database_extractor in database_extractor_classes:
        # Extract reactions and metabolites for the selected database and build a SBML model
        database_extractor.extract_reactions()
        sbml.build_sbml(database_extractor, args.outPath, args.name)

    # ##### MERGE SBML MODELS ###### #
    print()


def parse_arguments():
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
    return args


if __name__ == '__main__':
    main()
