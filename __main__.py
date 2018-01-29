# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:35:14 2017

@author: James Bradbury
"""
import argparse
import os
import tools
from sbml import sbml
from interfaces.enzymeAssignment import EnzymeAssignment
from interfaces.databaseExtraction import DatabaseExtraction
from interfaces.sbmlExtraction import SBMLExtraction


def main():
    print("executing METRONOME.")

    args = parse_arguments()
    print(args)

    # ###### ENZYME ASSIGNMENT ###### #
    ea_class = tools.load_class(args.enzymeAssignment, EnzymeAssignment)
    ea_class.assign_enzymes(args.enzymeAssignmentFile)

    # ###### DATABASE EXTRACTION  ### #
    # load SBML extractions
    sbml_extractor_classes = tools.load_classes('sbmlExtraction', SBMLExtraction, enzymes=ea_class.assigned_enzymes, sbml_path=args.sbmlFolder)
    for sbml_extractor in sbml_extractor_classes:
        # extract reactions and metabolites from the selected sbml file and build a SBML model
        sbml_extractor.extract_reactions()
        sbml.build_sbml(sbml_extractor, args.outPath, args.name)


    # load database extractors
    database_extractor_classes = tools.load_classes('databaseExtraction', DatabaseExtraction, enzymes=ea_class.assigned_enzymes)
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
    # sbml folder path
    parser.add_argument('-f', '--sbmlFolder',
                        type=str, required=False,
                        help="Path to folder containing SBML files to extract reactions and metabolites from")
    # sbml config file path
    parser.add_argument('-c', '--sbmlNotesConfig',
                        type=str, required=False, default=os.path.dirname(__file__)+'/sbmlNotesConfig.csv',
                        help="Path to file containing sbml notes tags for sbml extraction")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
