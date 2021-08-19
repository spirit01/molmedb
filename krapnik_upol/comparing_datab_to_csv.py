#!/usr/bin/env python3
import csv
import threading

import MySQLdb
# from Bio.SubsMat.MatrixInfo import structure
from pubchempy import *
import configparser


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
    FORMATS = {logging.DEBUG: logging._STYLES['{'][0]("DEBUG; {message}"),
               logging.ERROR: logging._STYLES['{'][0]("ERROR; {message}"),
               logging.INFO: logging._STYLES['{'][0]("{message}"),
               'DEFAULT': logging._STYLES['{'][0](" {message}")}

    def format(self, record):
        # Ugly. Should be better
        self._style = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)


# load Final_merge_dat and returns sets of tuples(name,smile)
def load_document_csv():
    name_smile_csv = []
    with open('Final_merge_dat.csv') as juraskova_csv_file:
        juraskova_csv_file = csv.reader(juraskova_csv_file, delimiter="|")

        for line in juraskova_csv_file:
            if line[0].strip() == 'DrugBank':
                name_smile_csv.append((line[1], line[2]))
                name_smile_csv.append((line[3], line[4]))

    return sorted(set(name_smile_csv))


# unify name and smile with PubChem, can be identified by prefixes ERROR
def unify_structures_pubchem(name, smile):
    if name == '' or smile == '':
        logging.info(f'WARNING: {name} ; {name}; {smile} \n')
    else:
        for compound in get_compounds(name, 'name'):
            print(f'{name} and {compound.cid}')
            for structure in get_compounds(compound.cid, 'cid'):
                # make file with similar and different items
                if name is not None or structure.iupac_name != None:
                    logging.info(f'ERROR; {name} ; {structure.iupac_name}; {structure.canonical_smiles} \n')
                    return False
                else:
                    return structure.iupac_name, structure.iupac_name


def compare_csv_to_molmedb(name1, smile, db):
    mycursor = db.cursor()
    sql = 'SELECT name,smiles FROM substances WHERE name=%s AND smiles=%s'
    if mycursor.execute(sql, [name1, smile]) == 1:
        logging.info(f'MATCH; {name1}; {smile}')
        return True
    else:
        return False


def make_final_file_for_calculation(name1, smile, db):
    mycursor = db.cursor()
    sql = 'SELECT name,smiles FROM substances WHERE name=%s AND smiles=%s'
    if mycursor.execute(sql, [name1, smile]) == 1:
        logging.info(f'MATCH; {name1}; {smile}')
    else:
        logging.info(f'ERROR; {name1} ; {structure.iupac_name}; {structure.canonical_smiles} \n')


# noinspection PyArgumentList
def strucutres(db):
    name_smile_csv = load_document_csv()
    for name1, smile in sorted(name_smile_csv):
        if not compare_csv_to_molmedb(name1, smile, db):
            if unify_structures_pubchem(name1, smile):
                make_final_file_for_calculation(unify_structures_pubchem(name1, smile), db)


def main():
    # remove logging file if it's already exist
    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['MolMeDB']['user']
    password = config['MolMeDB']['password']
    host = config['MolMeDB']['host']
    database = config['MolMeDB']['database']

    db = MySQLdb.connect(user = user, password = password, host = host, database = database)

    hdlr = logging.FileHandler(
        f'results_name_smile.log')
    hdlr.setFormatter(SpecialFormatter())
    logging.root.addHandler(hdlr)
    logging.root.setLevel(logging.INFO)
    logging.root.setLevel(logging.DEBUG)
    logpipe = LogPipe(logging.DEBUG)
    logpipe_err = LogPipe(logging.DEBUG)
    # structure_to_unify are not in MolMeDB
    # send structrue to PubChem
    strucutres(db)
    logpipe.close()
    logpipe_err.close()
    db.close()


if __name__ == '__main__':
    main()
