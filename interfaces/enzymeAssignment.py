# -*- coding: utf-8 -*-

import abc

class EnzymeAssignment(abc.ABC):
    
    @abc.abstractmethod
    def test(self):
        """ Test method
        """
        
    @abc.abstractmethod
    def test2(self):
        """ Test method
        """