from interfaces import databaseExtraction
from sbml import sbml


class SBMLExtraction(databaseExtraction.DatabaseExtraction):
    def __init__(self, **kwargs):
        # check for key errors
        self._reactions = {}
        self._metabolites = {}
        self._assigned_enzymes = self.assigned_enzymes(kwargs['enzymes'])
        self._sbml_file = sbml.load_sbml(kwargs['sbml_file'])

    @property
    def sbml_file(self):
        return self._sbml_file

    def extract_reaction_name(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        return [kwargs['reaction'].getName()]

    def extract_reaction_reversibility(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        return kwargs['reaction'].getReversible()

    def extract_reaction_stoichiometry(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        stoichiometry = {}
        for substrate in kwargs['reaction'].getListOfReactants():
            stoichiometry[substrate.getSpecies()] = substrate.getStoichiometry()
        for product in kwargs['reaction'].getListOfProducts():
            stoichiometry[product.getSpecies()] = product.getStoichiometry()
        return stoichiometry

    def extract_metabolite_formula(self, **kwargs):
        pass

    def extract_metabolite_compartment(self, **kwargs):
        pass

    def extract_metabolite_inchi(self, **kwargs):
        pass

    def extract_reaction_substrates(self, **kwargs):
        pass

    def extract_reaction_products(self, **kwargs):
        pass

    def extract_reactions(self):
        pass

    def database_name(self):
        pass

    def extract_metabolite_name(self, **kwargs):
        pass

    def extract_metabolite_dblinks(self, **kwargs):
        pass

    def extract_metabolite(self, metabolite_id):
        pass

    def extract_reaction_dblinks(self, **kwargs):
        pass

    def extract_metabolite_charge(self, **kwargs):
        pass

    def extract_metabolite_smiles(self, **kwargs):
        pass
