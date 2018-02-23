import collections
import logging
import re

import requests

from interfaces import databaseExtraction

kegg_url = "http://rest.kegg.jp/get/%s"
kegg_reaction_pattern = re.compile("^[R]\d{5}")
kegg_compound_pattern = re.compile("^[CG]\d{5}")


class KeggExtraction(databaseExtraction.DatabaseExtraction):
    """
    Database extraction module to extract reactions and metabolites from KEGG
    The module extends the databaseExtraction interface
    It works by making use of the KEGG REST services
    """

    def metabolite_inchi_key(self, **kwargs):
        pass

    def database_name(self):
        """

        :return:
        """
        return "KEGG"

    def metabolite_compartment(self, **kwargs):
        pass

    def metabolite_inchi(self, **kwargs):
        pass

    def metabolite_charge(self, **kwargs):
        pass

    def metabolite_smiles(self, **kwargs):
        pass

    def metabolite_dblinks(self, **kwargs):
        """

        :return:
        """
        try:
            db_links = {'KEGG': kwargs['metabolite_id']}
            for l in kwargs['compound_kegg_entry']['DBLINKS']:
                db_links[l.split(': ')[0]] = l.split(': ')[1]
        except KeyError:
            db_links = {}
        return db_links

    def metabolite_formula(self, **kwargs):
        """

        :return:
        """
        try:
            formula = kwargs['compound_kegg_entry']['FORMULA'][0]
        except KeyError:
            formula = 'NA'
        return formula

    def metabolite_name(self, **kwargs):
        """

        :return:
        """
        try:
            name = kwargs['compound_kegg_entry']['NAME']
        except KeyError:
            name = [kwargs['metabolite_id']]
        return name

    def reaction_name(self, **kwargs):
        """

        :return:
        """
        try:
            name = kwargs['reaction_kegg_entry']['NAME']
        except KeyError:
            name = [kwargs['reaction_id']]
        return name

    def reaction_dblinks(self, **kwargs):
        """

        :return:
        """
        try:
            db_links = {'KEGG': kwargs['reaction_id']}
            for l in kwargs['reaction_kegg_entry']['DBLINKS']:
                db_links[l.split(': ')[0]] = l.split(': ')[1]
        except KeyError:
            db_links = {}
        return db_links

    def reaction_reversibility(self, **kwargs):
        """

        :return:
        """
        try:
            reversible = '<=>' in kwargs['reaction_kegg_entry']['EQUATION'][0]
        except KeyError:
            reversible = False
        return reversible

    def extract_metabolite(self, metabolite_id):
        """

        :param metabolite_id:
        :return:
        """
        if metabolite_id not in self.metabolites:
            logging.info("\t\tCalling KEGG REST service: %s" % metabolite_id)
            compound_kegg_entry = get_entry(rest2dict(requests.get(kegg_url % metabolite_id)))

            name = self.metabolite_name(compound_kegg_entry=compound_kegg_entry, metabolite_id=metabolite_id)
            formula = self.metabolite_formula(compound_kegg_entry=compound_kegg_entry)
            db_links = self.metabolite_dblinks(compound_kegg_entry=compound_kegg_entry, metabolite_id=metabolite_id)

            metabolite = databaseExtraction.MetaboliteDict(metabolite_id, name, formula, db_links)
            self.metabolites[metabolite_id] = metabolite

            return metabolite
        else:
            logging.info("\t\tCompound %s already extracted from KEGG" % metabolite_id)
            return self.metabolites[metabolite_id]

    def get_reactions(self):
        """

        :return:
        """
        logging.info("Executing KEGG Extractor")
        for ec_number in self.enzymes.keys():
            logging.info("Calling KEGG REST service: %s" % ec_number)
            ec_kegg_entry = get_entry(rest2dict(requests.get(kegg_url % ec_number)))
            kegg_reaction_ids = []
            try:
                for e in ec_kegg_entry['ALL_REAC']:
                    for r in e.split(' '):
                        kegg_reaction_ids.extend(re.findall(kegg_reaction_pattern, r))
            except KeyError:
                pass
            for r in kegg_reaction_ids:
                if r == 'R07620':
                    print()
                if r not in self.reactions:
                    logging.info("\tCalling KEGG REST service: %s" % r)
                    reaction_kegg_entry = get_entry(rest2dict(requests.get(kegg_url % r)))

                    name = self.reaction_name(reaction_id=r, reaction_kegg_entry=reaction_kegg_entry)
                    reversible = self.reaction_reversibility(reaction_kegg_entry=reaction_kegg_entry)
                    db_links = self.reaction_dblinks(reaction_kegg_entry=reaction_kegg_entry, reaction_id=r)

                    substrates = self.reaction_substrates(reaction_kegg_entry=reaction_kegg_entry,
                                                          reaction_id=r)
                    products = self.reaction_products(reaction_kegg_entry=reaction_kegg_entry, reaction_id=r)
                    stoichiometry = self.reaction_stoichiometry(substrates=substrates, products=products, reaction_kegg_entry=reaction_kegg_entry)

                    reaction = databaseExtraction.ReactionDict(r, name, substrates, products, reversible, ec_number,
                                                               self.enzymes[ec_number], db_links, stoichiometry)
                    self.reactions[r] = reaction

                else:
                    logging.info("\tReaction %s already extracted from KEGG .... appending E.C. number and Gene IDs" % r)
                    reaction = self.reactions[r]
                    reaction.append_enzyme(ec_number)
                    reaction.append_gene(self.enzymes[ec_number])

    def reaction_substrates(self, **kwargs):
        """

        :return:
        """
        reaction_substrate_ids = []
        for kegg_compound_id in kwargs['reaction_kegg_entry']['EQUATION'][0].split('<=>')[0].split(' '):
            reaction_substrate_ids.extend(re.findall(kegg_compound_pattern, kegg_compound_id))
        substrates = {}
        for substrate in reaction_substrate_ids:
            substrates[substrate] = self.extract_metabolite(substrate)
            logging.info("\t\t\tAdding %s as substrate to %s" % (substrate, kwargs['reaction_id']))
        return substrates

    def reaction_products(self, **kwargs):
        """

        :return:
        """
        reaction_product_ids = []
        for kegg_compound_id in kwargs['reaction_kegg_entry']['EQUATION'][0].split('<=>')[1].split(' '):
            reaction_product_ids.extend(re.findall(kegg_compound_pattern, kegg_compound_id))
        products = {}
        for product in reaction_product_ids:
            products[product] = self.extract_metabolite(product)
            logging.info("\t\t\tAdding %s as product to %s" % (product, kwargs['reaction_id']))
        return products

    def reaction_stoichiometry(self, **kwargs):
        stoichiometry = {}
        equation = kwargs['reaction_kegg_entry']['EQUATION'][0].replace(" ", "")
        for substrate in kwargs['substrates']:
            index = equation.index(substrate)
            if not index == 0:
                if equation[index - 1].isdigit():
                    stoichiometry[substrate] = int(equation[index - 1])
                else:
                    stoichiometry[substrate] = 1
            else:
                stoichiometry[substrate] = 1

        for product in kwargs['products']:
            index = equation.index(product)
            if not index == 0:
                if equation[index - 1].isdigit():
                    stoichiometry[product] = int(equation[index - 1])
                else:
                    stoichiometry[product] = 1
            else:
                stoichiometry[product] = 1

        return stoichiometry


def rest2dict(request):
    """
    Transforms a KEGG get REST request into an OrderedDict
    :param request:
    :return:
    """
    k_list = request.text.split('\n')
    res = collections.OrderedDict()
    for v in k_list:
        if '\t' in v:
            new_v = v.split('\t', 1)
            res[new_v[0]] = new_v[1]
        else:
            res[v] = ""
    return res


def get_entry(r):
    e = {}
    temp = []
    for line in r:
        if line.startswith(" "):
            temp.append(line[12:])
        else:
            temp = []
            field = line.split(" ")[0]
            temp.append(line[12:])
            e[field] = temp

    return e
