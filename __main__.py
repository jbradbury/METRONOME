# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 15:35:14 2017

@author: James Bradbury
"""
import argparse
import logging
import time
import tools
import sys
from sbml import sbml
from interfaces.enzymeAssignment import EnzymeAssignment
from interfaces.databaseExtraction import DatabaseExtraction
from interfaces.sbmlExtraction import SBMLExtraction
from network_merging import merge


def main():
    logging.basicConfig(filename='METRONOME.log', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("\n%s\nexecuting METRONOME.\n" % time.ctime())

    args = parse_arguments()
    logging.info("Program arguments: %s" % args)

    # STEP 1 - Assign enzymes
    enzymes = enzyme_assignment(args)
    # STEP 2 - Database extraction
    database_extraction(args, enzymes)
    # STEP 3 - SBML file extraction
    sbml_extraction(args, enzymes)
    # STEP 4 - Network merging
    merge_networks(args, enzymes)

    # GENERATE HTML REPORT


def enzyme_assignment(args):
    try:
        logging.info("\nBeginning enzyme assignment")
        ea_class = tools.load_class("enzymeAssignment." + args.enzymeAssignment, EnzymeAssignment)
        logging.info("E.A. Class: %s" % ea_class)
        ea_class.assign_enzymes(args.enzymeAssignmentFile)
        return ea_class.assigned_enzymes
    except:
        logging.ERROR("Failed to assign enzymes")
        sys.exit(1)


def database_extraction(args, enzymes):
    logging.info("\nBeginning database extraction")
    database_extractor_classes = tools.load_classes('databaseExtraction', DatabaseExtraction, enzymes=enzymes)
    logging.info("Database extraction classes: %s" % database_extractor_classes)
    for database_extractor in database_extractor_classes:
        # Extract reactions and metabolites for the selected database and build a SBML model
            database_extractor.get_reactions()
            sbml.build_sbml(database_extractor, args.outPath, args.name)


def sbml_extraction(args, enzymes):
    sbml_extractor_classes = []
    try:
        for sbml_file in args.sbmlFiles:
            logging.info('')
            sbml_extractor_classes.extend(
                tools.load_classes('sbmlExtraction', SBMLExtraction, enzymes=enzymes, sbml_file=sbml_file))
    except:
        logging.error("Failed to load")

    for sbml_extractor in sbml_extractor_classes:
        sbml_extractor.get_reactions()
        sbml.build_sbml(sbml_extractor, args.outPath, args.name + '_' + sbml_extractor.sbml_file.getModel().getId())


def merge_networks(args, enzymes):
    merged_network = merge.NetworkMerger(path=args.outPath, enzymes=enzymes)
    sbml.build_sbml(merged_network, args.outPath, args.name)


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
                        help="Name of the enzyme assignment module. The module must be inside the enzymeAssignment directory")
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
