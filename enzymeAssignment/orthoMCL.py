# -*- coding: utf-8 -*-
import csv
import re
import urllib.request

from xml.etree import ElementTree
from interfaces import enzymeAssignment
from interfaces.enzymeAssignment import ec_pattern


# input_path = 'C:/Users/bradburj/PhD/NBAF/orthoMCL/orthologGroups'


class OrthoMCL(enzymeAssignment.EnzymeAssignment):
    """
    Enzyme Assignment module to assign enzymes based on the output files from OrthoMCL
    It works by making use of the OrthoMCL REST services
    """

    def assign_enzymes(self, input_path):
        with open(input_path) as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if not row[1] == 'NO_GROUP':
                    (protein_id, ec_numbers) = (row[0], self.get_ec_numbers_for_orthoMCL_group(row[1]))
                    print(protein_id, ec_numbers)
                    if not ec_numbers is None:
                        for ec in ec_numbers:
                            if not ec in self.assigned_enzymes.keys():
                                self.assigned_enzymes[ec] = [protein_id]
                            else:
                                self.assigned_enzymes[ec].append(protein_id)

    @staticmethod
    def get_ec_numbers_for_orthoMCL_group(orthoMCL_group):
        """

        :param orthoMCL_group:
        :return:
        """
        url = 'http://www.orthomcl.org/webservices/GroupQuestions/ByNameList.xml?group_names_data=%s&o-fields=ec_numbers' % (
            orthoMCL_group)
        req = urllib.request.urlopen(url)
        rdata = []
        chunk = 'xx'
        while chunk:
            chunk = req.read()
            if chunk:
                rdata.append(chunk)
        tree = ElementTree.fromstring(b''.join(rdata))
        for i, elem in enumerate(tree.getiterator('field')):
            try:
                return re.findall(ec_pattern, elem.text)
            except TypeError:
                return None
