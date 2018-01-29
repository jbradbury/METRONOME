import abc

from interfaces import databaseExtraction
from interfaces.enzymeAssignment import AssignedEnzymeDict
from sbml import sbml


class SBMLExtraction(databaseExtraction.DatabaseExtraction):
    def __init__(self, **kwargs):
        # check for key errors
        self._reactions = {}
        self._metabolites = {}
        self._assigned_enzymes = self.assigned_enzymes(kwargs['enzymes'])
        self._sbml_file = sbml.load_sbml(kwargs['sbml_path'])

