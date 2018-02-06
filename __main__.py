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
from interfaces.sbmlExtraction import SBMLExtraction
from network_merging import merge


def main():
    print("executing METRONOME.")
    args = parse_arguments()
    print(args)

    # ###### ENZYME ASSIGNMENT ###### #
    ea_class = tools.load_class(args.enzymeAssignment, EnzymeAssignment)
    ea_class.assign_enzymes(args.enzymeAssignmentFile)

    merge.NetworkMerger(path=args.outPath, enzymes=ea_class.assigned_enzymes)

    # ###### DATABASE EXTRACTION  ### #
    # load database extractors
    database_extractor_classes = tools.load_classes('databaseExtraction', DatabaseExtraction,
                                                    enzymes=ea_class.assigned_enzymes)
    for database_extractor in database_extractor_classes:
        # Extract reactions and metabolites for the selected database and build a SBML model
        database_extractor.get_reactions()
        sbml.build_sbml(database_extractor, args.outPath, args.name)

    # load SBML extractions
    sbml_extractor_classes = []
    for sbml_file in args.sbmlFiles:
        sbml_extractor_classes.extend(
            tools.load_classes('sbmlExtraction', SBMLExtraction, enzymes=ea_class.assigned_enzymes,
                               sbml_file=sbml_file))

    for sbml_extractor in sbml_extractor_classes:
        sbml_extractor.get_reactions()
        sbml.build_sbml(sbml_extractor, args.outPath, args.name + '_' + sbml_extractor.sbml_file.getModel().getId())

    # ##### MERGE SBML MODELS ###### #
    merge.NetworkMerger(args.outPath)

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
    parser.add_argument('-f', '--sbmlFiles',
                        type=str, nargs='+', required=False,
                        help="Paths of SBML files to extract reactions and metabolites from")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
