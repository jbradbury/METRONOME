import importlib
import inspect
import os


def load_classes(path, instance, **kwargs):
    """
    Method for loading all classes of a given instance from a given path (directory).
    Classes in the files in the directory that have a .py extension are loaded using the load_class method
    :param path: The directory to load classes from
    :param instance: The instance of the classes to be loaded (can be parent class instance)
    :param kwargs: Optional arguments for the target classes __init__ method
    :return: A list of instantiated classes
    """
    classes = []

    for file in os.listdir(os.path.dirname(__file__) + '/' + path):
        if file.endswith(".py"):
            classes.append(load_class(path + '.' + file.split('.')[0], instance, **kwargs))

    return classes


def load_class(path, instance, **kwargs):
    """
    Method for loading a class of a given instance from a path
    :param path: The path of the class to be loaded
    :param instance: The instance of the class to be loaded (can be parent class instance)
    :param kwargs: Optional arguments for the target classes __init__ method
    :return: An instantiated class
    """
    file_module = importlib.import_module(path)
    class_members = inspect.getmembers(file_module, inspect.isclass)

    for class_member in class_members:
        the_class = getattr(file_module, class_member[0])
        the_instance = the_class(**kwargs)
        if isinstance(the_instance, instance):
            return the_instance


def notes2dict(notes_string):
    """
    Turns a SBML notes string into a dictionary
    Each item in the notes string that is inside a <p> tag is added to the dictionary
    The keys are the left side of a colon, the value is the right side
    E.G.: KEGG: C00001 = {KEGG = C00001}
    :param notes_string: The SBML notes string
    :return: a dict <p> tagged items in the SBML notes string
    """
    notes_dict = {}
    for line in notes_string.split('\n'):
        if '<p>' in line:
            line = line.replace('<p>', '')
            line = line.replace('</p>', '')
            s = line.split(': ')
            notes_dict[s[0].strip()] = s[1]
    return notes_dict