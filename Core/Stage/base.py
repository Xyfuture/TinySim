from collections import OrderedDict
from abc import ABCMeta,abstractmethod


class StageBase(metaclass=ABCMeta):
    def __init__(self):
        pass


    @abstractmethod
    def recv(self):
        pass

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def ticktock(self):
        pass

    @abstractmethod
    def stall(self):
        pass