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

__all__ = ('getLogger', )

from ..configuration.configuration import user_dir, cc_conf
from logging.handlers import TimedRotatingFileHandler
from threading import RLock
from os import makedirs
from os.path import exists as path_exists
import logging


lock = RLock()


logging_levels = {
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'debug': logging.DEBUG
}

formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s: [%(name)s] %(message)s', datefmt='%m.%d.%Y %I:%M:%S %p')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

lib_logger = logging.getLogger('cc_lib')
lib_logger.propagate = False
lib_logger.addHandler(stream_handler)

usr_logger = logging.getLogger('user')
usr_logger.propagate = False
usr_logger.addHandler(stream_handler)


def initLogging():
    lib_logger.setLevel(logging_levels[cc_conf.logger.level])
    if cc_conf.logger.rotating_log:
        lock.acquire()
        lib_logger.removeHandler(stream_handler)
        usr_logger.removeHandler(stream_handler)
        logs_path = '{}/logs'.format(user_dir)
        if not path_exists(logs_path):
            makedirs(logs_path)
        file_path = '{}/connector.log'.format(logs_path)
        log_handler = TimedRotatingFileHandler(
            file_path,
            when="midnight",
            backupCount=cc_conf.logger.rotating_log_backup_count
        )
        log_handler.setFormatter(formatter)
        lib_logger.addHandler(log_handler)
        usr_logger.addHandler(log_handler)
        lock.release()


def _getLibHandler():
    lock.acquire()
    log_handler = lib_logger.handlers[0]
    lock.release()
    return log_handler


def _getLibLogger(name: str) -> logging.Logger:
    return lib_logger.getChild(name)


def getLogger(name: str) -> logging.Logger:
    return usr_logger.getChild(name)
