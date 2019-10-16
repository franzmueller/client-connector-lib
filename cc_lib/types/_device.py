"""
   Copyright 2019 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ('Device', 'device')

from .._util import validateInstance, validateSubclass, getSubclass
from ._service import Service
from collections import OrderedDict
from typing import Union


class Device:
    uri = str()
    description = str()
    services = dict()

    def __new__(cls, *args, **kwargs):
        if cls is __class__:
            __err = "instantiation of class '{}' not allowed".format(__class__.__name__)
            raise TypeError(__err)
        __instance = super(__class__, cls).__new__(cls)
        __instance.__id = str()
        __instance.__remote_id = str()
        __instance.__name = str()
        __instance.__tags = OrderedDict()
        return __instance

    @property
    def id(self) -> str:
        return self.__id

    @id.setter
    def id(self, arg: str):
        validateInstance(arg, str)
        if self.__id:
            raise AttributeError
        self.__id = arg

    @property
    def remote_id(self) -> str:
        return self.__remote_id

    @remote_id.setter
    def remote_id(self, arg: str):
        validateInstance(arg, str)
        if self.__remote_id:
            raise AttributeError
        self.__remote_id = arg

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, arg: str) -> None:
        validateInstance(arg, str)
        self.__name = arg

    def getService(self, service: str) -> Service:
        try:
            return self.__class__.services[service]
        except KeyError:
            raise KeyError("service '{}' does not exist".format(service))

    def __str__(self, **kwargs):
        """
        Provide a string representation.
        :param kwargs: User attributes provided from subclass.
        :return: String.
        """
        attributes = [
            ('id', repr(self.id)),
            ('remote_id', repr(self.remote_id)),
            ('name', repr(self.name)),
            ('tags', repr(self.tags)),
            ('services', [key for key in self.__class__.services])
        ]
        if kwargs:
            for arg, value in kwargs.items():
                attributes.append((arg, value))
        return "{}({})".format(type(self).__name__, ", ".join(["=".join([key, str(value)]) for key, value in attributes]))

    @classmethod
    def _validate(cls) -> None:
        for a_name, a_type in _getAttributes():
            attr = getattr(cls, a_name)
            validateInstance(attr, a_type)
            if a_name is "services":
                for key, srv in attr.items():
                    if isinstance(srv, type):
                        validateSubclass(srv, Service)
                    else:
                        validateInstance(srv, Service)
                    validateInstance(key, str)


def device(obj: Union[type, dict]) -> type:
    validateInstance(obj, (type, dict))
    return getSubclass(obj, Device)


def _getAttributes() -> tuple:
    return tuple((name, type(obj)) for name, obj in Device.__dict__.items() if
                 not name.startswith("_") and not isinstance(obj, staticmethod))