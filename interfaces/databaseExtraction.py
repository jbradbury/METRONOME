import abc
import collections
import sys

from interfaces.enzymeAssignment import AssignedEnzymeDict


class DatabaseExtraction(abc.ABC):
    def __init__(self, assigned_enzymes):
        self._reactions = {}
        self._metabolites = {}
        self._assigned_enzymes = self.assigned_enzymes(assigned_enzymes)

    @property
    def reactions(self):
        """

        :return:
        """
        return self._reactions

    @property
    def metabolites(self):
        """

        :return:
        """
        return self._metabolites

    @property
    def enzymes(self):
        """

        :return:
        """
        return self._assigned_enzymes

    @abc.abstractmethod
    def database_name(self):
        """
        Database name. This is used by the SBML module
        :return:
        """
        pass

    @abc.abstractmethod
    def extract_reactions(self):
        """
        Extract reactions based on provided list of assigned enzymes
        :return:
        """
        pass

    @abc.abstractmethod
    def extract_metabolite(self, metabolite_id):
        """
        :param metabolite_id:
        :return:
        """
        pass

    @staticmethod
    def assigned_enzymes(assigned_enzymes):
        """
        Check that assigned_enzymes is instance of enzymeAssignment.AssignedEnzymeDict
        :param assigned_enzymes:
        :return:
        """
        try:
            assert bool(assigned_enzymes) and isinstance(assigned_enzymes, AssignedEnzymeDict)
            return assigned_enzymes
        except AssertionError:
            print('Assigned enzymes must be an instance of enzymeAssignment.AssignedEnzymeDict')
            sys.exit()


class ReactionDict(collections.MutableMapping):
    """
    An object designed to store reactions.
    Reaction id is the key
    Values include:
        - Name
        - Substrate/product metabolites (w/ stoiciometry)
        - reversibility
        - Enzyme number(s)
        - Pathway
        - Gene associations
        - Database references
    """

    def __init__(self, reaction_id, name, substrates, products, reversible, ec_number, pathway, gene_ids, db_links,
                 stoichiometry):
        self.store = dict()
        self.__setitem__('ID', self.reaction_id(reaction_id))
        self.__setitem__('NAME', self.name(name))
        self.__setitem__('SUBSTRATES', self.metabolites_check(substrates))
        self.__setitem__('PRODUCTS', self.metabolites_check(products))
        self.__setitem__('REVERSIBLE', self.reversible(reversible))
        self.__setitem__('ENZYME', self.enzymes([ec_number]))
        self.__setitem__('PATHWAY', self.pathway(pathway))
        self.__setitem__('GENE_ASSOCIATION', self.gene_ids(gene_ids))
        self.__setitem__('DB_LINKS', self.db_links(db_links))
        self.__setitem__('STOICHIOMETRY', self.stoichiometry(stoichiometry))

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def append_enzyme(self, ec_number):
        self.__getitem__('ENZYME').append(ec_number)

    def append_gene(self, gene_id):
        self.__getitem__('GENE_ASSOCIATION').extend(gene_id)

    @property
    def __len__(self):
        return len(self.store)

    @staticmethod
    def reaction_id(reaction_id):
        """

        :param reaction_id:
        :return:
        """
        try:
            assert bool(reaction_id) and isinstance(reaction_id, str)
            return reaction_id
        except AssertionError:
            print("Reaction ID must be of type str")
            sys.exit()

    @staticmethod
    def name(name):
        """

        :param name:
        :return:
        """
        try:
            assert bool(name) and isinstance(name, list) and all(isinstance(n, str) for n in name)
            return name
        except AssertionError:
            print('Reaction Name must be of type list, which can only contain strings')
            sys.exit()

    @staticmethod
    def metabolites_check(metabolites):
        """
        check that substrate is instance of MetaboliteDict
        :param metabolites:
        :return:
        """
        try:
            assert bool(metabolites) and isinstance(metabolites, dict) and all(
                isinstance(metabolite, MetaboliteDict) for metabolite in metabolites.values())
            return metabolites
        except AssertionError:
            print('Substrates and products must be all be an instance of MetaboliteDict')
            sys.exit()

    @staticmethod
    def reversible(reversible):
        """

        :param reversible:
        :return:
        """
        try:
            assert bool(reversible) and isinstance(reversible, bool)
            return reversible
        except AssertionError:
            print('Reaction reversibility must be of type bool')
            sys.exit()

    @staticmethod
    def enzymes(enzymes):
        """

        :param enzymes:
        :return:
        """
        try:
            assert bool(enzymes) and isinstance(enzymes, list) and all(isinstance(e, str) for e in enzymes)
            return enzymes
        except AssertionError:
            print('Reaction Enzymes must be of type list, which can only contain strings')
            sys.exit()

    @staticmethod
    def pathway(pathway):
        """

        :param pathway:
        :return:
        """
        try:
            isinstance(pathway, list) and all(isinstance(p, str) for p in pathway)
            return pathway
        except AssertionError:
            print('Reaction Pathway must be of type list, which can only contain strings')
            sys.exit()

    @staticmethod
    def gene_ids(gene_ids):
        """

        :param name:
        :return:
        """
        try:
            assert bool(gene_ids) and isinstance(gene_ids, list) and all(isinstance(i, str) for i in gene_ids)
            return gene_ids
        except AssertionError:
            print('Reaction Gene IDs must be of type list, which can only contain strings')
            sys.exit()

    @staticmethod
    def db_links(db_links):
        """
        Reaction Database links must be of type dict, all keys and values must be strings
        :return:
        """
        try:
            isinstance(db_links, dict) and all(
                isinstance(key, str) for key in db_links.keys()) and all(
                isinstance(value, str) for value in db_links.values())
            return db_links
        except AssertionError:
            print('Reaction database links must be of type dict. All keys and values in the dict must be strings')
            sys.exit()

    @staticmethod
    def stoichiometry(stoichiometry):
        """

        :param stoichiometry:
        :return:
        """
        try:
            isinstance(stoichiometry, dict) and all(
                isinstance(key, str) for key in stoichiometry.keys()) and all(
                isinstance(value, int) for value in stoichiometry.values())
            return stoichiometry
        except AssertionError:
            print('Reaction stoichiometry should be a dict, with string keys and int values')
            sys.exit()


class MetaboliteDict(collections.MutableMapping):
    """
    A dictionary designed to store metabolites.
    Metabolite id is the key
    Values include:
        - Name
        - Compartment
        - Charge
        - Formula
        - Inchi
        - Smiles
        - Database references
    """

    def __init__(self, metabolite_id, name, formula, db_links, compartment="Intracellular", charge='NA', inchi='NA',
                 smiles='NA'):
        self.store = dict()
        self.__setitem__('ID', self.metabolite_id(metabolite_id))
        self.__setitem__('NAME', self.name(name))
        self.__setitem__('CHARGE', self.charge(charge))
        self.__setitem__('FORMULA', self.formula(formula))
        self.__setitem__('INCHI', self.inchi(inchi))
        self.__setitem__('SMILES', self.smiles(smiles))
        self.__setitem__('DB_LINKS', self.db_links(db_links))
        self.__setitem__('COMPARTMENT', self.compartment(compartment))

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    @property
    def __len__(self):
        return len(self.store)

    @staticmethod
    def metabolite_id(metabolite_id):
        """

        :param metabolite_id:
        :return:
        """
        try:
            assert bool(metabolite_id) and isinstance(metabolite_id, str)
            return metabolite_id
        except AssertionError:
            print("Metabolite ID must be of type str")
            sys.exit()

    @staticmethod
    def name(name):
        """

        :param name:
        :return:
        """
        try:
            assert bool(name) and isinstance(name, list) and all(isinstance(n, str) for n in name)
            return name
        except AssertionError:
            print('Metabolite Name must be of type list, which can only contain strings')
            sys.exit()

    @staticmethod
    def charge(charge):
        """

        :param charge:
        :return:
        """
        try:
            isinstance(charge, str)
            return charge
        except AssertionError:
            print("Metabolite Charge must be of type str")
            sys.exit()

    @staticmethod
    def inchi(inchi):
        """

        :param inchi:
        :return:
        """
        try:
            isinstance(inchi, str)
            return inchi
        except AssertionError:
            print("Metabolite Inchi must be of type str")
            sys.exit()

    @staticmethod
    def smiles(smiles):
        """

        :param smiles:
        :return:
        """
        try:
            isinstance(smiles, str)
            return smiles
        except AssertionError:
            print("Metabolite Smiles must be of type str")
            sys.exit()

    @staticmethod
    def formula(formula):
        """

        :param formula:
        :return:
        """
        try:
            isinstance(formula, str)
            return formula
        except AssertionError:
            print('Metabolite Formula must be of type list, which can only contain strings')
            sys.exit()

    @staticmethod
    def db_links(db_links):
        """
        Metabolite Database links must be of type dict, all keys and values must be strings
        :return:
        """
        try:
            isinstance(db_links, dict) and all(
                isinstance(key, str) for key in db_links.keys()) and all(
                isinstance(value, str) for value in db_links.values())
            return db_links
        except AssertionError:
            print('Metabolite database links must be of type dict. All keys and values in the dict must be strings')
            sys.exit()

    @staticmethod
    def compartment(compartment):
        """

        :param compartment:
        :return:
        """
        try:
            assert bool(compartment) and isinstance(compartment, str)
            return compartment
        except AssertionError:
            print("Metabolite Compartment must be of type str")
            sys.exit()
