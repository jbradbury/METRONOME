import re
from interfaces import sbmlExtraction, databaseExtraction


class MetaCycSBMLExtraction(sbmlExtraction.SBMLExtraction):
    """
    Database extraction module to extract reactions and metabolites from the Metacyc SBML file
    This module extends the databaseExtraction interface
    """

    def database_name(self):
        """

        :return:
        """
        return "MetaCyc"

    def extract_metabolite_compartment(self, **kwargs):
        pass

    def extract_metabolite_inchi(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        try:
            inchi = kwargs['metabolite_notes_dict']['INCHI']
        except KeyError:
            inchi = 'NA'
        return inchi

    def extract_metabolite_charge(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        try:
            charge = kwargs['metabolite_notes_dict']['CHARGE']
        except KeyError:
            charge = 'NA'
        return charge

    def extract_metabolite_smiles(self, **kwargs):
        pass

    def extract_metabolite_formula(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        try:
            formula = kwargs['metabolite_notes_dict']['FORMULA']
        except KeyError:
            formula = 'NA'
        return formula

    def extract_metabolite_name(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        return [kwargs['metabolite'].getName()]

    def extract_metabolite_dblinks(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        db_links = kwargs['metabolite_notes_dict']
        if 'CHARGE' in db_links.keys():
            del db_links['CHARGE']
        if 'FORMULA' in db_links.keys():
            del db_links['FORMULA']
        if 'INCHI' in db_links.keys():
            del db_links['INCHI']
        return db_links

    def extract_reaction_name(self, **kwargs):
        pass

    def extract_reaction_reversibility(self, **kwargs):
        pass

    def extract_reaction_products(self, **kwargs):
        products = {}
        for product in kwargs['reaction'].getListOfProducts():
            products[product.getSpecies()] = self.extract_metabolite(product.getSpecies())
            print("\t\tAdding %s as product to %s" % (product.getSpecies(), kwargs['reaction'].getId()))
        return products

    def extract_reaction_substrates(self, **kwargs):
        substrates = {}
        for substrate in kwargs['reaction'].getListOfReactants():
            substrates[substrate.getSpecies()] = self.extract_metabolite(substrate.getSpecies())
            print("\t\tAdding %s as substrate to %s" % (substrate.getSpecies(), kwargs['reaction'].getId()))
        return substrates

    def extract_reaction_dblinks(self, **kwargs):
        pass

    def extract_metabolite(self, metabolite_id):
        """

        :param metabolite_id:
        :return:
        """
        if metabolite_id not in self.metabolites:
            metabolite_notes_dict = metacyc_metabolite_notes2dict(
                self.sbml_file.getModel().getListOfSpecies().get(metabolite_id).getNotesString())
            name = self.extract_metabolite_name(metabolite=self.sbml_file.getModel().getListOfSpecies().get(metabolite_id))
            charge = self.extract_metabolite_charge(metabolite_notes_dict=metabolite_notes_dict)
            formula = self.extract_metabolite_formula(metabolite_notes_dict=metabolite_notes_dict)
            inchi = self.extract_metabolite_inchi(metabolite_notes_dict=metabolite_notes_dict)
            db_links = self.extract_metabolite_dblinks(metabolite_notes_dict=metabolite_notes_dict)

            metabolite = databaseExtraction.MetaboliteDict(metabolite_id, name, formula, db_links, charge=charge, inchi=inchi)
            self.metabolites[metabolite_id] = metabolite

            return metabolite
        else:
            return self.metabolites[metabolite_id]

    def extract_reactions(self):
        """

        :return:
        """
        print("Executing MetaCyc SBML Extractor")
        for ec_number in self.enzymes.keys():
            print("Extracting reactions linked to %s" % ec_number)
            for reaction in self.sbml_file.getModel().getListOfReactions():
                if len(re.findall('\\b'+ec_number+'\\b', reaction.getNotesString())) > 0:
                    print('\tExtracting reaction: %s' % reaction.getId())
                    substrates = self.extract_reaction_substrates(reaction=reaction)
                    products = self.extract_reaction_products(reaction=reaction)
                    # products
                        # parent class
                    # reversible
                        # parent class
                    # ec_number
                    # geneids
                    # db links
                    # charge
                    # inchi
                    # stoichiometry
                        # parent class
                    # reaction = databaseExtraction.ReactionDict(reaction.getId())
                    # self.reactions[reaction.getId()] = reaction


def metacyc_metabolite_notes2dict(metabolite_notes_string):
    """

    :param metabolite_notes_string:
    :return:
    """
    metabolite_notes_dict = {}
    for line in metabolite_notes_string.split('\n'):
        if '<p>' in line:
            line = line.replace('<p>', '')
            line = line.replace('</p>', '')
            s = line.split(': ')
            metabolite_notes_dict[s[0].strip()] = s[1]
    return metabolite_notes_dict
