import collections
import re
import requests
from interfaces import databaseExtraction

kegg_url = "http://rest.kegg.jp/get/%s"
kegg_reaction_pattern = re.compile("^[R]\d{5}")
kegg_compound_pattern = re.compile("^[C]\d{5}")


class KeggExtraction(databaseExtraction.DatabaseExtraction):
    """
    Database extraction module to extract reactions and metabolites from KEGG
    The module extends the databaseExtraction interface
    It works by making use of the KEGG REST services
    """
    def database_name(self):
        return "KEGG"

    def extract_metabolite(self, metabolite_id):
        """

        :param metabolite_id:
        :return:
        """
        if metabolite_id not in self.metabolites:
            print("\t\tCalling KEGG REST service: %s" % metabolite_id)
            compound_kegg_entry = get_entry(rest2dict(requests.get(kegg_url % metabolite_id)))

            name = extract_metabolite_name(compound_kegg_entry, metabolite_id)
            formula = extract_metabolite_formula(compound_kegg_entry)
            db_links = extract_metabolite_dblinks(compound_kegg_entry)

            metabolite = databaseExtraction.MetaboliteDict(metabolite_id, name, formula, db_links)
            self.metabolites[metabolite_id] = metabolite

            return metabolite
        else:
            print("\t\tCompound %s already extracted from KEGG" % metabolite_id)
            return self.metabolites[metabolite_id]

    @property
    def extract_reactions(self):
        """

        :return:
        """
        print("Executing KEGG Extractor")
        for ec_number in self.enzymes.keys():
            print("Calling KEGG REST service: %s" % ec_number)
            ec_kegg_entry = get_entry(rest2dict(requests.get(kegg_url % ec_number)))
            kegg_reaction_ids = []
            for e in ec_kegg_entry['ALL_REAC']:
                for r in e.split(' '):
                    kegg_reaction_ids.extend(re.findall(kegg_reaction_pattern, r))
            for r in kegg_reaction_ids:
                if r not in self.reactions:
                    print("\tCalling KEGG REST service: %s" % r)
                    reaction_kegg_entry = get_entry(rest2dict(requests.get(kegg_url % r)))

                    name = extract_reaction_name(r, reaction_kegg_entry)
                    reversible = extract_reaction_reversibility(reaction_kegg_entry)
                    pathway = extract_reaction_pathway(reaction_kegg_entry)
                    db_links = extract_reaction_dblinks(reaction_kegg_entry)

                    substrates = self.extract_reaction_substrates(reaction_kegg_entry, r)
                    products = self.extract_reaction_products(reaction_kegg_entry, r)

                    reaction = databaseExtraction.ReactionDict(r, name, substrates, products, reversible, ec_number,
                                                               pathway, self.enzymes[ec_number], db_links)
                    self.reactions[r] = reaction

                else:
                    print("\tReaction %s already extracted from KEGG .... appending E.C. number and Gene IDs" % r)
                    reaction = self.reactions[r]
                    reaction.append_enzyme(ec_number)
                    reaction.append_gene(self.enzymes[ec_number])

    def extract_reaction_substrates(self, reaction_kegg_entry, reaction_id):
        """

        :param reaction_id:
        :param reaction_kegg_entry:
        :return:
        """
        reaction_substrate_ids = []
        for kegg_compound_id in reaction_kegg_entry['EQUATION'][0].split('<=>')[0].split(' '):
            reaction_substrate_ids.extend(re.findall(kegg_compound_pattern, kegg_compound_id))
        substrates = {}
        for substrate in reaction_substrate_ids:
            substrates[substrate] = self.extract_metabolite(substrate)
            print("\t\t\tAdding %s as substrate to %s" % (substrate, reaction_id))
        return substrates

    def extract_reaction_products(self, reaction_kegg_entry, reaction_id):
        """

        :param reaction_id:
        :return:
        :param reaction_kegg_entry:
        :return:
        """
        reaction_product_ids = []
        for kegg_compound_id in reaction_kegg_entry['EQUATION'][0].split('<=>')[1].split(' '):
            reaction_product_ids.extend(re.findall(kegg_compound_pattern, kegg_compound_id))
        products = {}
        for product in reaction_product_ids:
            products[product] = self.extract_metabolite(product)
            print("\t\t\tAdding %s as substrate to %s" % (product, reaction_id))
        return products


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


def extract_metabolite_dblinks(compound_kegg_entry):
    """

    :param compound_kegg_entry:
    :return:
    """
    try:
        db_links = {}
        for l in compound_kegg_entry['DBLINKS']:
            db_links[l.split(': ')[0]] = l.split(': ')[1]
    except KeyError:
        db_links = {}
    return db_links


def extract_metabolite_formula(compound_kegg_entry):
    """

    :param compound_kegg_entry:
    :return:
    """
    try:
        formula = compound_kegg_entry['FORMULA']
    except KeyError:
        formula = ['NA']
    return formula


def extract_metabolite_name(compound_kegg_entry, metabolite_id):
    """

    :param compound_kegg_entry:
    :param metabolite_id:
    :return:
    """
    try:
        name = compound_kegg_entry['NAME']
    except KeyError:
        name = metabolite_id
    return name


def extract_reaction_name(r, reaction_kegg_entry):
    """

    :param r:
    :param reaction_kegg_entry:
    :return:
    """
    try:
        name = reaction_kegg_entry['NAME']
    except KeyError:
        name = [r]
    return name


def extract_reaction_dblinks(reaction_kegg_entry):
    """

    :param reaction_kegg_entry:
    :return:
    """
    try:
        db_links = {}
        for l in reaction_kegg_entry['DBLINKS']:
            db_links[l.split(': ')[0]] = l.split(': ')[1]
    except KeyError:
        db_links = {}
    return db_links


def extract_reaction_pathway(reaction_kegg_entry):
    """

    :param reaction_kegg_entry:
    :return:
    """
    try:
        pathway = reaction_kegg_entry['PATHWAY']
    except KeyError:
        pathway = []
    return pathway


def extract_reaction_reversibility(reaction_kegg_entry):
    """

    :param reaction_kegg_entry:
    :return:
    """
    try:
        reversible = '<=>' in reaction_kegg_entry['EQUATION'][0]
    except KeyError:
        reversible = False
    return reversible
