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


__all__ = ("RawMessage", )

import typing


class RawMessage:

    __slots__ = ('__topic', '__payload')

    def __init__(self, topic: typing.Union[str, bytes], payload: typing.Union[str, bytes]):
        self.topic = topic
        self.payload = payload

    @property
    def topic(self) -> typing.Union[str, bytes]:
        return self.__topic

    @topic.setter
    def topic(self, arg: typing.Union[str, bytes]):
        # validateInstance(arg, typing.Union[str, bytes])
        self.__topic = arg

    @property
    def payload(self) -> typing.Union[str, bytes]:
        return self.__payload

    @payload.setter
    def payload(self, arg: typing.Union[str, bytes]):
        # validateInstance(arg, typing.Union[str, bytes])
        self.__payload = arg

    def __iter__(self):
        items = (('topic', self.topic), ('payload', self.payload))
        for item in items:
            yield item

    def __repr__(self):
        """
        Provide a string representation.
        :return: String.
        """
        attributes = [
            ('topic', self.topic),
            ('payload', self.payload)
        ]
        return "{}({})".format(__class__.__name__, ", ".join(["=".join([key, str(value)]) for key, value in attributes]))
