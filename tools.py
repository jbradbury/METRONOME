import importlib
import inspect
import os


def load_classes(path, instance):
    classes = []

    for file in os.listdir(os.path.dirname(__file__) + '/' + path):
        if file.endswith(".py"):
            file_module = importlib.import_module(path + '.' + file.split('.')[0])
            class_members = inspect.getmembers(file_module, inspect.isclass)

            for class_member in class_members:
                the_class = getattr(file_module, class_member[0])
                the_instance = the_class()
                if isinstance(the_instance, instance):
                    classes.append(the_instance)

    return classes


def load_classes(path, instance, **kwargs):
    classes = []

    for file in os.listdir(os.path.dirname(__file__) + '/' + path):
        if file.endswith(".py"):
            file_module = importlib.import_module(path + '.' + file.split('.')[0])
            class_members = inspect.getmembers(file_module, inspect.isclass)

            for class_member in class_members:
                the_class = getattr(file_module, class_member[0])
                the_instance = the_class(**kwargs)
                if isinstance(the_instance, instance):
                    classes.append(the_instance)

    return classes


def load_class(path, instance):
    file_module = importlib.import_module(path)
    class_members = inspect.getmembers(file_module, inspect.isclass)

    for class_member in class_members:
        the_class = getattr(file_module, class_member[0])
        the_instance = the_class()
        if isinstance(the_instance, instance):
            return the_instance


def notes2dict(notes_string):
    """

    :param notes_string:
    :return:
    """
    notes_dict = {}
    for line in notes_string.split('\n'):
        if '<p>' in line:
            line = line.replace('<p>', '')
            line = line.replace('</p>', '')
            s = line.split(': ')
            notes_dict[s[0].strip()] = s[1]
    return notes_dict