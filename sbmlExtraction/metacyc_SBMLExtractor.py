from interfaces import sbmlExtraction


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

    def extract_metabolite(self, metabolite_id):
        """

        :param metabolite_id:
        :return:
        """
        pass

    def extract_reactions(self):
        """

        :return:
        """
        print("Executing MetaCyc SBML Extractor")
        for ec_number in self.enzymes.keys():
            print("Extracting reactions linked to %s" % ec_number)

