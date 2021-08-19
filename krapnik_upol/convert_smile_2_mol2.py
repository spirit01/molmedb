#!/usr/bin/env python3

# Conver list of SMILE from databse to file and to mol2.

# -*- coding: utf-8 -*-
import logging
import sys
import os
import subprocess
from argparse import ArgumentParser
import MySQLdb
import configparser


# get name or smile of reactant its enzym
def get_argument():
    parser = ArgumentParser()

    parser.add_argument("--directory", help="choose directory to save output",
                        metavar="DIR", dest="output", required=True)

    return parser.parse_args()


def get_functional_group(db, directory):
    functional_group = []
    #f = open("tmp.smi", "w+")
    mycursor = db.cursor()
    sql = 'SELECT SMILES FROM substances'
    mycursor.execute(sql)
    result = mycursor.fetchall()

    for smile in result:
        with open(f'{directory}/{smile}.smi') as f:
            f.write(smile)
            call = subprocess.run('babel -smi {smile}.smi', shell=True)

    return functional_group

def main():
    args = get_argument()
    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['MolMeDB']['user']
    password = config['MolMeDB']['password']
    host = config['MolMeDB']['host']
    database = config['MolMeDB']['database']

    db = MySQLdb.connect(user = user, password = password, host = host, database = database)

    get_functional_group(db, args.output)
    db.close()

if __name__ == '__main__':
    main()