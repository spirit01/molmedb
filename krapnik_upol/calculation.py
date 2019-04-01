# Run calculation in upol
# !/usr/bin/env python3
import MySQLdb


def check_method_in_MolMeDB(db):
    mycursor = db.cursor()
    sql = 'SELECT substances.name, methods.name FROM substances RIGHT OUTER JOIN energy ON ' \
          'substances.idSubstance = energy.idSubstance INNER JOIN methods ON ' \
          'energy.idMethod = methods.idMethod'
    print(mycursor.execute(sql))


def send_to_calculation():
    name_iupac_cansmile = []
    with open('results_name_smile.log') as file:
        for line in file:
            if line.startswith('ERROR'):
                name_iupac_cansmile.append((line.split(';')[2], line.split(';')[3].rstrip()))
    return name_iupac_cansmile


def check_match_structures():
    pass
    # TODO for MATCH structures check methods


def make_list_for_calculation():
    name_smile = send_to_calculation()
    with open('list_name_canonic_smile_for_calculation', 'w+') as file:
        for name, smile in name_smile:
            file.write(f'{smile} {name} \n')


def main():
    db = MySQLdb.connect(user='petra', password='petra',
                         host='localhost',
                         database='molmedb')
    make_list_for_calculation()


if __name__ == '__main__':
    main()
