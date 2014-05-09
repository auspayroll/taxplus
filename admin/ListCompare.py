from django.db import models

class ListCompare:
    """
    In this class, all the functions are static.
    All these functions are commonly used across all the apps
    """
    
    @staticmethod
    def getExtraItems(old_list,new_list):
        """
        Compare two lists, and get old_list - new_list
        """
        result = []
        if len(old_list) == 0:
            return result
        elif len(new_list) == 0:
            return old_list
        for element in old_list:
            if element not in new_list:
                result.append(element)
        return result
    
    @staticmethod
    def getLessItems(old_list,new_list):
        """
        Compare two lists, and get new_list - old_list
        """
        result = []
        if len(old_list) == 0:
            return new_list
        elif len(new_list) == 0:
            return result
        else:
            for element in new_list:
                if element not in old_list:
                    result.append(element)
            return result