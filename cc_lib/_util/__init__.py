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


__all__ = (
    'Singleton',
    'validateInstance',
    'validateSubclass',
    'getMangledAttr',
    'setMangledAttr',
    'calcNthTerm',
    'calcDuration'
)


from typing import Any, Union, Tuple
from math import ceil, log10


class Singleton(type):
    """
    Subclass this class for singleton behavior.
    """
    _instances = dict()
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def validateInstance(obj: object, cls: Union[type, Tuple[type, ...]]) -> None:
    """
    Raise TypeError if given object is not an instance of given class.
    Also works with instances of sub classes derived from the given class.
    :param obj: Object to be validated.
    :param cls: Class to check against.
    :return: None.
    """
    if not isinstance(obj, cls):
        err = "instance of {} required but got {}".format(cls, type(obj))
        raise TypeError(err)


def validateSubclass(cls: type, parent_cls: Union[type, Tuple[type, ...]]) -> None:
    """
    Raise TypeError if given class is not sub class of given class.
    :param cls: Class to be validated.
    :param parent_cls: Class to check against.
    :return: None.
    """
    if not issubclass(cls, parent_cls):
        err = "{} not subclass of {}".format(cls, parent_cls)
        raise TypeError(err)


def getMangledAttr(obj: object, attr: str) -> Any:
    """
    Read mangled attribute.
    :param obj: Object with mangled attributes.
    :param attr: Name of mangled attribute.
    :return: value of mangled attribute.
    """
    return getattr(obj, '_{}__{}'.format(obj.__class__.__name__, attr))


def setMangledAttr(obj: object, attr: str, arg: Any) -> None:
    """
    Write to mangled attribute.
    :param obj: Object with mangled attributes.
    :param attr: Name of mangled attribute.
    :param arg: value to be written.
    """
    setattr(obj, '_{}__{}'.format(obj.__class__.__name__, attr), arg)


def calcNthTerm(a_1: Union[float, int], r: Union[float, int], n: Union[float, int]) -> Union[float, int]:
    """
    Calculates the nth term of a geometric progression (an = a1 * r^(n-1)).
    :param a_1: First term.
    :param r: Common ratio.
    :param n: Number of desired term.
    :return: Float or integer.
    """
    return a_1 * r ** (n - 1)


def calcDuration(min_duration: int, max_duration: int, retry_num: int, factor: Union[float, int]) -> int:
    """
    Calculate a value to be used as sleep duration based on a geometric progression.
    Won't return values above max_duration.
    :param min_duration: Minimum value to be returned.
    :param max_duration: Maximum value to be returned.
    :param retry_num: Number iterated by a loop calling the method.
    :param factor: Speed at which the maximum value will be reached.
    :return: Integer.
    """
    base_value = calcNthTerm(min_duration, factor, retry_num)
    magnitude = int(log10(ceil(base_value)))+1
    duration = ceil(base_value / 10 ** (magnitude - 1)) * 10 ** (magnitude - 1)
    if duration <= max_duration:
        return duration
    return max_duration