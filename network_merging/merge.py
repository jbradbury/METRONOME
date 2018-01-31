import glob
import os
import requests
from sbml import sbml


def merge_networks(path):
    metanetx_dict = MetaNetXDict()
    mnxrids = []
    no_mnxrids = []

    os.chdir(path)
    for file in [f for f_ in [glob.glob(e) for e in ('*.xml', '*.sbml')] for f in f_]:
        sbml_file = sbml.load_sbml(file)
        _mnxrids = []
        _no_mnxrids = []
        for reaction in sbml_file.getModel().getListOfReactions():
            if reaction.getId() in metanetx_dict.reactions_xref:
                _mnxrids.append(metanetx_dict.reactions_xref[reaction.getId()])
            else:
                _no_mnxrids.append(file + ': ' + reaction.getId())
        _mnxrids = set(_mnxrids)
        print(file + ":\n\t%d unique reaction MetaNetX ids\n\t%d reactions with no MetaNetX id" % (len(_mnxrids), len(_no_mnxrids)))
        mnxrids.append(_mnxrids)
        no_mnxrids.append(_no_mnxrids)

    mnxrids = set(mnxrids)



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

    @staticmethod
    def load_xref(url):
        print('Loading XRefs from %s' % url)
        response = requests.get(url)
        xref = {}
        try:
            for line in response.text.split('\n'):
                if not line[0] == '#' and 'deprecated' not in line and ':' in line:
                    line = line.split('\t')
                    xref[line[0].split(':')[1]] = line[1]
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
                    reactions[line[0]] = {'EQUATION': line[1], 'DESCRIPTION': line[2], 'BALANCE': line[3], 'EC': line[4],
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
                    metabolites[line[0]] = {'DESCRIPTION': line[1], 'FORMULA': line[2], 'CHARGE': line[3], 'MASS': line[4],
                                            'INCHI': line[5], 'SMILES': line[6], 'SOURCE': line[7], 'INCHIKEY': line[8]}
        except IndexError:
            pass
        return metabolites
