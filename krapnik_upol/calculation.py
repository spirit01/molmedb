#!/usr/bin/env python3

#work with file results.log from comparing_datab_juraskova.

def main():
    with open('results_comparing.log') as file:
        for line in file:
            if line.startswith('ERROR'):
                name = line.split(';')[1]
                print(name)

    pass

if __name__ == '__main__':
    main()
