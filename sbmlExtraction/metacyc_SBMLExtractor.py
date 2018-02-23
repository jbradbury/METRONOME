import re

from interfaces import sbmlExtraction, databaseExtraction
from tools import notes2dict


class MetaCycSBMLExtraction(sbmlExtraction.SBMLExtraction):
    """
    Database extraction module to extract reactions and metabolites from the Metacyc SBML file
    This module extends the databaseExtraction interface
    """

    def metabolite_inchi_key(self, **kwargs):
        pass

    def database_name(self):
        """

        :return:
        """
        return "MetaCyc"

    def metabolite_compartment(self, **kwargs):
        pass

    def metabolite_inchi(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        try:
            inchi = kwargs['metabolite_notes_dict']['INCHI']
        except KeyError:
            inchi = 'NA'
        return inchi

    def metabolite_charge(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        try:
            charge = kwargs['metabolite_notes_dict']['CHARGE']
        except KeyError:
            charge = 'NA'
        return charge

    def metabolite_smiles(self, **kwargs):
        pass

    def metabolite_formula(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        try:
            formula = kwargs['metabolite_notes_dict']['FORMULA']
        except KeyError:
            formula = 'NA'
        return formula

    def metabolite_name(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        return [kwargs['metabolite'].getName()]

    def metabolite_dblinks(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        db_links = kwargs['notes_dict']
        if 'CHARGE' in db_links.keys():
            del db_links['CHARGE']
        if 'FORMULA' in db_links.keys():
            del db_links['FORMULA']
        if 'INCHI' in db_links.keys():
            del db_links['INCHI']
        return db_links

    def reaction_products(self, **kwargs):
        products = {}
        for product in kwargs['reaction'].getListOfProducts():
            # metabolite_id = self.get_species_id(product.getSpecies())
            products[product.getSpecies()] = self.extract_metabolite(product.getSpecies())
            print("\t\tAdding %s as product to %s" % (product.getSpecies(), kwargs['reaction'].getId()))
        return products

    def reaction_substrates(self, **kwargs):
        substrates = {}
        for substrate in kwargs['reaction'].getListOfReactants():
            # metabolite_id = self.get_species_id(substrate.getSpecies())
            substrates[substrate.getSpecies()] = self.extract_metabolite(substrate.getSpecies())
            print("\t\tAdding %s as substrate to %s" % (substrate.getSpecies(), kwargs['reaction'].getId()))
        return substrates

    def get_species_id(self, species):
        return notes2dict(self.sbml_file.getModel().getSpecies(species).getNotesString())['BIOCYC']

    def reaction_dblinks(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        db_links = kwargs['notes_dict']
        if 'EC Number' in db_links.keys():
            del db_links['EC Number']
        if 'GENE_ASSOCIATION' in db_links.keys():
            del db_links['GENE_ASSOCIATION']
        if 'SUBSYSTEM' in db_links.keys():
            del db_links['SUBSYSTEM']
        return db_links

    def reaction_pathways(self, **kwargs):
        try:
            return kwargs['notes_dict']['SUBSYSTEM'].split(', ')
        except KeyError:
            return []

    def extract_metabolite(self, metabolite_id):
        """

        :param metabolite_id:
        :return:
        """
        if metabolite_id not in self.metabolites:
            metabolite_notes_dict = notes2dict(
                self.sbml_file.getModel().getListOfSpecies().get(metabolite_id).getNotesString())
            name = self.metabolite_name(
                metabolite=self.sbml_file.getModel().getListOfSpecies().get(metabolite_id))
            charge = self.metabolite_charge(metabolite_notes_dict=metabolite_notes_dict)
            formula = self.metabolite_formula(metabolite_notes_dict=metabolite_notes_dict)
            inchi = self.metabolite_inchi(metabolite_notes_dict=metabolite_notes_dict)
            db_links = self.metabolite_dblinks(notes_dict=metabolite_notes_dict)

            metabolite = databaseExtraction.MetaboliteDict(metabolite_id, name, formula, db_links, charge=charge,
                                                           inchi=inchi)
            self.metabolites[metabolite_id] = metabolite

            return metabolite
        else:
            return self.metabolites[metabolite_id]

    def get_reactions(self):
        """

        :return:
        """
        print("Executing MetaCyc SBML Extractor")
        for ec_number in self.enzymes.keys():
            print("Extracting reactions linked to %s" % ec_number)
            for reaction in self.sbml_file.getModel().getListOfReactions():
                if len(re.findall('\\b' + ec_number + '\\b', reaction.getNotesString())) > 0:
                    for ec in re.findall('\\b' + ec_number + '\\b', reaction.getNotesString()):
                        if ec == ec_number:
                            if reaction.getId() not in self.reactions:
                                print('\tExtracting reaction: %s' % reaction.getId())
                                notes_dict = notes2dict(reaction.getNotesString())
                                name = self.reaction_name(reaction=reaction)
                                substrates = self.reaction_substrates(reaction=reaction)
                                products = self.reaction_products(reaction=reaction)
                                reversible = self.reaction_reversibility(reaction=reaction)
                                stoichiometry = self.reaction_stoichiometry(reaction=reaction)
                                pathways = self.reaction_pathways(notes_dict=notes_dict)

                                db_links = self.reaction_dblinks(notes_dict=notes_dict)

                                r = databaseExtraction.ReactionDict(reaction.getId(), name, substrates, products,
                                                                    reversible, ec_number, self.enzymes[ec_number],
                                                                    db_links, stoichiometry, pathways)
                                self.reactions[reaction.getId()] = r
                            else:
                                print(
                                    '\tReaction %s is already extracted .... appending E.C. number and Gene IDs' %
                                    reaction.getId())
                                r = self.reactions[reaction.getId()]
                                r.append_enzyme(ec_number)
                                r.append_gene(self.enzymes[ec_number])


