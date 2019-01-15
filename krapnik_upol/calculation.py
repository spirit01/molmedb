#!/usr/bin/env python3

import logging
import os
# work with file results.log from comparing_datab_juraskova.
import tempfile
import threading

from comparing_datab_juraskova import load_database


class LogPipe(threading.Thread):

    def __init__(self, level):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.level = level
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe
        """
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything.
        """
        for line in iter(self.pipeReader.readline, ''):
            logging.log(self.level, line.strip('\n'))

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe.
        """
        os.close(self.fdWrite)


class SpecialFormatter(logging.Formatter):
    FORMATS = {logging.DEBUG: logging._STYLES['{'][0]("DEBUG: {message}"),
               logging.ERROR: logging._STYLES['{'][0]("ERROR: {message}"),
               logging.INFO: logging._STYLES['{'][0]("{message}"),
               'DEFAULT': logging._STYLES['{'][0](" {message}")}

    def format(self, record):
        # Ugly. Should be better
        self._style = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)


# make a list of unsearched structures
def list_selected_name():
    with open('results.log') as file:
        selected_name_smile = []
        for line in file:
            if line.startswith('ERROR') and line.split(';')[1] != None:
                selected_name_smile.append((line.split(';')[1], line.split(';')[2]))
    return selected_name_smile


def compare_sselected_name_with_database(list_selected_name):
    additional_name = []
    for unify_name, unify_smile in list_selected_name:
        for name, smile in load_database():
            if unify_name == name or unify_smile.rstrip() == smile:
                additional_name.append((unify_name.rstrip(), unify_smile.rstrip()))

    return set(additional_name)


def isLineEmpty(line):
    return len(line.strip())

    # go through the results.log, extract modified structures and repeats comparing with MolMeDB


def make_final_files(additional_name, countless_name):
    with open('results.log') as file:
        for line in file:
            if not (line.startswith('ERROR') or line.startswith('DEBUG') or line.startswith(
                    '\'Not Found') or isLineEmpty(
                line) == 0):
                # find solved structures
                logging.info(f'COUNTED: {line.strip()}')
    # add structures where was not the exact same name
    for name, smile in additional_name:
        logging.info(f'WARNING: {name};{smile}')

    for name, smile in countless_name:
        logging.info(f'ERROR: {name};{smile}')


def main():
    # list_selected_name contains structures with are DONE but they had wrong name
    # and it was nessesary to unify them with PubChe
    additional_name = compare_sselected_name_with_database(list_selected_name())
    hdlr = logging.FileHandler(
        f'all_countless_structures_from_juraskova.log')
    hdlr.setFormatter(SpecialFormatter())
    logging.root.addHandler(hdlr)
    logging.root.setLevel(logging.INFO)
    logging.root.setLevel(logging.DEBUG)
    tmpdir = tempfile.mkdtemp()
    logpipe = LogPipe(logging.DEBUG)
    logpipe_err = LogPipe(logging.DEBUG)
    make_final_files(additional_name, list_selected_name())
    logpipe.close()
    logpipe_err.close()


if __name__ == '__main__':
    main()
