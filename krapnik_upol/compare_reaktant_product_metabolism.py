#!/usr/bin/env python3
# script to compare two metabolites

#Vstup:
#   terminal: reaktant nebo reaktanty oddělené ;
#   soubor:   reaktant nebo reaktanty oddělené ; , každý řádek odpovídá jednomu reaktantu

#Vystup:
#   terminal: reaktant se všemi produkty, odděleno ;
#   soubor  : kazda reakce uvedena na svem radku, pro vsechny reaktanty jsou nalezeny vsechny produkty

from __future__ import print_function

import csv
import logging
import sys
import os
from argparse import ArgumentParser
from time import localtime, strftime
from convert_smile_2_mol2 import get_functional_group
import configparser

import MySQLdb

# TODO add a list of functional group

all_functionalgroup_list = ["C(=O)O", "(C=O)", "C=N2"]


# get name or smile of reactant its enzym
def get_argument():
    parser = ArgumentParser()

    parser.add_argument("--reactions", help="choose file with reactants and products. Format: reaction; product",
                        metavar="DIR", dest="reactions")

    parser.add_argument("--output", help="choose directory to save output",
                        metavar="DIR", dest="output", required=True)

    parser.add_argument("-functionalgroupSMART", metavar='FSMR',
                        dest="fc_SMARTS",
                        help="Function group in SMART format")

    parser.add_argument("-functionalgroupSMILE", metavar='FSML',
                        dest="fc_SMILES",
                        help="Functional group in SMILE format")

    return parser.parse_args()

class SpecialFormatter(logging.Formatter):
    FORMATS = {logging.DEBUG: logging._STYLES['{'][0]("DEBUG: {message}"),
               logging.ERROR: logging._STYLES['{'][0]("{module} : {lineno}: {message}"),
               logging.INFO: logging._STYLES['{'][0]("{message}"),
               'DEFAULT': logging._STYLES['{'][0](" {message}")}

    def format(self, record):
        # Ugly. Should be better
        self._style = self.FORMATS.get(record.levelno, self.FORMATS['DEFAULT'])
        return logging.Formatter.format(self, record)


class Structure():
    def __init__(self, logP = 0, SMILE = " ", type = None):
        # TODO add more properties?
        self.logP = logP
        self.SMILE = SMILE
        self.SMART = " "
        self.type = type
        self.functioanl_group = []
        functioanl_group = get_functional_group(self.SMILE)

class Reaction():
    def __init__(self, reactant, product):
        # v reaktantech potřebuji mít pole struktur, a z reakce potřebuji vracet porovnani pro každou reakci
        # chci tam mít pole? nebo pouze jeden reaktant + produkt a potom mít reakce v poli dále?
        # reaktant bude jenom jeden a k nemu bude pole produktu
        self.reactant = [reactant]
        self.product = [product]
        self.delta_logP = 0;

    # TODO add more properties?
    #pro každou reakci vracím fyziklně-chemické vlastnosti
    def compare_phys_chem_properties(reactant, product):
        delta_logP = Structure.logP(product) - Structure.logP(reactant)

    def to_string(self):
        string = f'{reactant}; {product}; {reactant.logP}; {product.logP}; {delta_logP}'
        pass


def check_name_with_molmedb(reactant, db):
    mycursor = db.cursor()
    sql = 'SELECT reactant FROM substances'
    if mycursor.execute(sql, [reactant]) == 1:
        return True
    else:
        print('Wrong name or structure is NOT in MolMeDB')
        sys.exit()


def check_product_with_molmedb(product, db):
    mycursor = db.cursor()
    sql = 'SELECT product FROM substances'
    if mycursor.execute(sql, [product]) == 1:
        return True
    else:
        print('Wrong name or enzyme is NOT in MolMeDB')
        sys.exit()


def find_logP(db):
    mycursor = db.cursor()
    logP = 'SELECT LogP FROM substances'
    return logP


def find_SMILE(db):
    mycursor = db.cursor()
    SMILES = 'SELECT SMILES FROM substances'
    return SMILES


# read csv file with pair reactant-product, input is product
# @return: four elements
def find_product_meetabolism(args):
    name_smile_csv = []
    with open('Final_merge_dat.csv') as juraskova_csv_file:
        juraskova_csv_file = csv.reader(juraskova_csv_file, delimiter="|")

        for line in juraskova_csv_file:
            if line[0].strip() == 'DrugBank' and line[1] == args.reactant:
                # name_smile_csv = reactant, reactant smile, product, product smile
                return name_smile_csv.append((line[1], line[2], line[4], line[4]))


def make_final_csv_file():
    pass


def colect_data(input):
    structures = []
    reactions = []

    with open(input) as file:
        for line in file:
            check_name_with_molmedb(line.split(";")[0], db)
            check_product_with_molmedb(line.split(";")[1], db)
            logP = find_logP(db)
            SMILES = find_SMILE(db)
            structures.append(Structure(logP, SMILES, line.split(";")[0]))
            Reaction(Structure(logP, SMILES, line.split(";")[0]), Structure(logP, SMILES, line.split(";")[1]))
            reactions.append(Reaction(line.split(";")[0], line.split(";")[1]))
    logging.info(f'Final sumarization of result \n')
    for reaction in reactions:
        logging.info(f'{Reaction.reactant}; {Reaction.product}; {Reaction.compare_phys_chem_properties()}')


def main():
    args = get_argument()
    try:
        os.mkdir(f'{args.output}')
    except:
        pass

    hdlr = logging.FileHandler(f'{args.output}/result_{strftime("%Y-%m-%d__%H-%M-%S", localtime())}.log')
    hdlr.setFormatter(SpecialFormatter())
    logging.root.addHandler(hdlr)
    logging.root.setLevel(logging.INFO)

    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['MolMeDB']['user']
    password = config['MolMeDB']['password']
    host = config['MolMeDB']['host']
    database = config['MolMeDB']['database']

    db = MySQLdb.connect(user = user, password = password, host = host, database = database)

    if (args.reactions).is_file():
        colect_data(args.reactions)
    else:
        colect_data('Final_merge_dat.csv')

    db.close()


if __name__ == '__main__':
    main()
