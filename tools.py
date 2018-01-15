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


def load_classes(path, instance, argument):
    classes = []

    for file in os.listdir(os.path.dirname(__file__) + '/' + path):
        if file.endswith(".py"):
            file_module = importlib.import_module(path + '.' + file.split('.')[0])
            class_members = inspect.getmembers(file_module, inspect.isclass)

            for class_member in class_members:
                the_class = getattr(file_module, class_member[0])
                the_instance = the_class(argument)
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
