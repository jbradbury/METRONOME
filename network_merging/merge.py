import glob
import os
import re

import requests

from interfaces import databaseExtraction
from sbml import sbml
from tools import notes2dict

metanetx_reaction_pattern = re.compile("(MNXM[0-9]+)")


class NetworkMerger(databaseExtraction.DatabaseExtraction):
    # need to pass the assigned enzymes
    def __init__(self, **kwargs):
        super(NetworkMerger, self).__init__(**kwargs)
        self._path = kwargs['path']
        self._metanetx_dict = MetaNetXDict()
        self._merged_reactions = self.merge_reactions()
        self.get_reactions()

    def database_name(self):
        pass

    def metabolite_charge(self, **kwargs):
        pass

    def reaction_substrates(self, **kwargs):
        reaction_substrate_ids = re.findall(metanetx_reaction_pattern,
                                            self.metanetx_dict.reactions[kwargs['reaction_id']]['EQUATION'].split('=')[
                                                0])
        substrates = {}
        for substrate_id in reaction_substrate_ids:
            substrates[substrate_id] = self.extract_metabolite(substrate_id)

        return substrates

    def reaction_products(self, **kwargs):
        reaction_product_ids = re.findall(metanetx_reaction_pattern, self.metanetx_dict.reactions[kwargs['reaction_id']]['EQUATION'].split('=')[1])
        products = {}
        for product_id in reaction_product_ids:
            products[product_id] = self.extract_metabolite(product_id)

        return products

    def extract_metabolite(self, metabolite_id):
        if metabolite_id not in self.metabolites:
            m = self.metanetx_dict.metabolites[metabolite_id]
            name = [m['DESCRIPTION']]
            formula = m['FORMULA']
            db_links = self.metabolite_dblinks(metabolite_id=metabolite_id)
            charge = m['CHARGE']
            inchi = m['INCHI']
            inchikey = m['INCHIKEY']
            smiles = m['SMILES']
            metabolite = databaseExtraction.MetaboliteDict(metabolite_id, name, formula, db_links, charge=charge, inchi=inchi,
                                                           inchikey=inchikey, smiles=smiles)
            self.metabolites[metabolite_id] = metabolite

            return metabolite
        else:
            return self.metabolites[metabolite_id]

    def metabolite_compartment(self, **kwargs):
        pass

    def reaction_reversibility(self, **kwargs):
        pass

    def reaction_name(self, **kwargs):
        pass

    def metabolite_formula(self, **kwargs):
        pass

    def metabolite_smiles(self, **kwargs):
        pass

    def metabolite_name(self, **kwargs):
        pass

    def reaction_dblinks(self, **kwargs):
        db_links = {}
        for reaction_xref in self.metanetx_dict.reactions_xref:
            if self.metanetx_dict.reactions_xref[reaction_xref]['MNXR'] == kwargs['reaction_id']:
                db = self.metanetx_dict.reactions_xref[reaction_xref]['DB'].split(':')[0].upper()
                db_links[db] = reaction_xref
        return db_links

    def metabolite_dblinks(self, **kwargs):
        db_links = {}
        for metabolite_xref in self.metanetx_dict.metabolites_xref:
            if self.metanetx_dict.metabolites_xref[metabolite_xref]['MNXR'] == kwargs['metabolite_id']:
                db = self.metanetx_dict.metabolites_xref[metabolite_xref]['DB'].split(':')[0].upper()
                db_links[db] = metabolite_xref
        return db_links

    def metabolite_inchi(self, **kwargs):
        pass

    def metabolite_inchi_key(self, **kwargs):
        pass

    def reaction_stoichiometry(self, **kwargs):
        stoichiometry = {}
        
        return stoichiometry

    def get_reactions(self):
        for reaction_id in self.merged_reactions:
            name = ['']
            substrates = self.reaction_substrates(reaction_id=reaction_id)
            products = self.reaction_substrates(reaction_id=reaction_id)
            reversible = True
            db_links = self.reaction_dblinks(reaction_id=reaction_id)
            stoichiometry = self.reaction_stoichiometry(substrates=substrates, products=products, reaction_id = reaction_id)

            # enzymes/gene ids

            r = databaseExtraction.ReactionDict(reaction_id, name, substrates, products, reversible, ec_number, genes, db_links, stoichiometry)
            print()

    @property
    def path(self):
        return self._path

    @property
    def metanetx_dict(self):
        return self._metanetx_dict

    @property
    def merged_reactions(self):
        return self._merged_reactions

    def merge_reactions(self):
        mnxrids = []
        no_mnxrids = []

        os.chdir(self.path)
        for file in [f for f_ in [glob.glob(e) for e in ('*.xml', '*.sbml')] for f in f_]:
            sbml_file = sbml.load_sbml(file)
            _mnxrids = []
            _no_mnxrids = []
            for reaction in sbml_file.getModel().getListOfReactions():
                reaction_notes = notes2dict(reaction.getNotesString())
                del reaction_notes['ENZYME']
                del reaction_notes['GENE_ASSOCIATION']
                added = False
                for key in reaction_notes.keys():
                    if reaction_notes[key] in self.metanetx_dict.reactions_xref:
                        _mnxrids.append(self.metanetx_dict.reactions_xref[reaction_notes[key]]['MNXR'])
                        added = True
                        break
                try:
                    if reaction.getId() in self.metanetx_dict.reactions_xref:
                        _mnxrids.append(self.metanetx_dict.reactions_xref[reaction.getId()]['MNXR'])
                        added = True
                except KeyError:
                    pass

                if not added:
                    _no_mnxrids.append(file + ': ' + reaction.getId())

            _mnxrids = set(_mnxrids)
            print(file + ":\n\t%d unique reaction MetaNetX ids\n\t%d reactions with no MetaNetX id" % (
                len(_mnxrids), len(_no_mnxrids)))
            mnxrids.extend(_mnxrids)
            no_mnxrids.extend(_no_mnxrids)

        return set(mnxrids)


reac_xref_url = 'https://www.metanetx.org/cgi-bin/mnxget/mnxref/reac_xref.tsv'
reac_prop_url = 'https://www.metanetx.org/cgi-bin/mnxget/mnxref/reac_prop.tsv'
chem_xref_url = 'https://www.metanetx.org/cgi-bin/mnxget/mnxref/chem_xref.tsv'
chem_prop_url = 'https://www.metanetx.org/cgi-bin/mnxget/mnxref/chem_prop.tsv'


class MetaNetXDict:
    def __init__(self):
        self.store = dict()
        self._reactions_xref = self.load_xref(reac_xref_url)
        self._reactions = self.load_reactions(reac_prop_url)
        self._metabolites_xref = self.load_xref(chem_xref_url)
        self._metabolites = self.load_metabolites(chem_prop_url)

    @property
    def reactions_xref(self):
        return self._reactions_xref

    @property
    def reactions(self):
        return self._reactions

    @property
    def metabolites_xref(self):
        return self._metabolites_xref

    @property
    def metabolites(self):
        return self._metabolites

    @staticmethod
    def load_xref(url):
        print('Loading XRefs from %s' % url)
        response = requests.get(url)
        xref = {}
        try:
            for line in response.text.split('\n'):
                if not line[0] == '#' and 'deprecated' not in line and ':' in line:
                    line = line.split('\t')
                    xref[line[0].split(':')[1]] = {'MNXR': line[1], 'DB': line[0]}
        except IndexError:
            pass
        return xref

    @staticmethod
    def load_reactions(url):
        print('Loading Reactions from %s' % url)
        response = requests.get(url)
        reactions = {}
        try:
            for line in response.text.split('\n'):
                if not line[0] == '#':
                    line = line.split('\t')
                    reactions[line[0]] = {'EQUATION': line[1], 'DESCRIPTION': line[2], 'BALANCE': line[3],
                                          'EC': line[4],
                                          'SOURCE': line[5]}
        except IndexError:
            pass
        return reactions

    @staticmethod
    def load_metabolites(url):
        print('Loading Metabolites from %s' % url)
        response = requests.get(url)
        metabolites = {}
        try:
            for line in response.text.split('\n'):
                if not line[0] == '#':
                    line = line.split('\t')
                    metabolites[line[0]] = {'DESCRIPTION': line[1], 'FORMULA': line[2], 'CHARGE': line[3],
                                            'MASS': line[4],
                                            'INCHI': line[5], 'SMILES': line[6], 'SOURCE': line[7], 'INCHIKEY': line[8]}
        except IndexError:
            pass
        return metabolites
