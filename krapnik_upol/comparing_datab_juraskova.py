#!/usr/bin/env python3
import csv
import tempfile
import threading

from pubchempy import *


# TODO udelat obecne porovnani, ne jenom s Juraskovou.
# TODO# Obecne porovnani libovolneho csv souboru v pozadovanem formatu s databazi


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


# load Final_merge_dat and returns sets of tuples(name,smile)
def load_document_juraskova():
    name_smile_juraskova = []
    with open('Final_merge_dat.csv') as juraskova_csv_file:
        juraskova_csv_file = csv.reader(juraskova_csv_file, delimiter="|")

        for line in juraskova_csv_file:
            if line[0].strip() == 'DrugBank':
                name_smile_juraskova.append((line[1], line[2]))
                name_smile_juraskova.append((line[3], line[4]))

    return set(sorted(name_smile_juraskova))

#unify name and smile with PubChem, can be identified by prefixes ERROR
def unify_structures_juraskova(unselected_structure):
    for name, smile in sorted(unselected_structure):
        for compound in get_compounds(name, 'name'):
            # print(f'{name} and {compound.cid}')
            for structure in get_compounds(compound.cid, 'cid'):
                # make file with similar and different items
                if name != None or structure.iupac_name != None:
                    logging.info(
                        f'ERROR: {name.strip()} ; {structure.iupac_name}; {structure.canonical_smiles.strip()} \n')
                else:
                    logging.info(f'ERROR: {name} ; {structure.iupac_name}; {structure.canonical_smiles.strip()} \n')
             


# TODO nezarazene struktury prohnat pres pubchem a znovu porovnat s databzi, az potom posilat na vypocet.
#  Chce to dodelat nejake chytre vyhledavani a vyresit navratovy kod z pubchemu.


# load database from Jurecek and return sets of tuples(name, smile)
def load_database():
    name_smile_database = []
    with open('smiles_upravene_bez_chyby.csv') as smiles_database:
        smiles_database = csv.reader(smiles_database, delimiter=";")

        for line in smiles_database:
            name_smile_database.append((line[1], line[2]))
    return set(sorted(name_smile_database))


# compare to name AND smiles, both must by the same. Result writes to results.log to the first part.
def compare_juraskova_and_database_both(name_smile_databse, name_smile_juraskova):
    final_smile_name = []
    for (name_j, smile_j) in name_smile_juraskova:
        for (name_d, smile_d) in name_smile_databse:
            if name_j == name_d and smile_j == smile_d:
                final_smile_name.append((name_d, smile_d))
                logging.info(f'{name_d}; {smile_d}')
            else:
                pass
                # unify_structures_juraskova(set((name_j, smile_j)))
    # Structures which DON'T have a form in databases are unified with PubChem.ncbi.nlm.nih.gov
    unify_structures_juraskova(name_smile_juraskova.difference(name_smile_databse))


def main():
    # remove logging file if it's already exist
    #results.log contains solved structures and unsolved structures are send to PubChem
    hdlr = logging.FileHandler(
        f'results.log')
    hdlr.setFormatter(SpecialFormatter())
    logging.root.addHandler(hdlr)
    logging.root.setLevel(logging.INFO)
    logging.root.setLevel(logging.DEBUG)
    tmpdir = tempfile.mkdtemp()
    logpipe = LogPipe(logging.DEBUG)
    logpipe_err = LogPipe(logging.DEBUG)

    name_smile_juraskova = load_document_juraskova()
    name_smile_database = load_database()
    compare_juraskova_and_database_both(name_smile_juraskova, name_smile_database)

    logpipe.close()
    logpipe_err.close()


if __name__ == '__main__':
    main()
