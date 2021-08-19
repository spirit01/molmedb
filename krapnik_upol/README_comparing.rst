.. -*- coding: utf-8 -*-

===========================================
MolMeDBB
===========================================

:Copyright: This document has been placed in the public domain.

.. contents::
.. sectnum::

<<<<<<< HEAD

Manual for data processing script.
=======
Script loads data from MolMeDB
>>>>>>>
 :MolMeDB: http://molmedb.upol.cz/stats
<<<<<<< HEAD

The following sections briefly describe the data processing script
and and concrete steps required to run the data processing script and get the results.

Arguments
==========

 --reactions: file with list of reactant + product in format: name(R); SMILE(R); name(P); SMILE(P)
 --output: directory for saving results, required
 -functionalgroupSMART: find all reactants with this functional group(in SMARTS format)
 + their product + comparison
 -functionalgroupSMILE: find all reactants with this functional group(in SMILES format)
 + their product + comparison

Details
=======
list of functional groups: functional groups are in SMILES format. You can check the entire list
of functional groups and add groups if necessary.
 
Input
=====
There are many possible input.
 - 1) files with all reactants + products (name(R); SMILE(R); name(P); SMILE(P))
 - 2) Concreted functional group in SMILES/SMARTS format. Script finds all reactants with this
 functional group + all their product
 - 3) ?

Output
======
Output is csv file. Each items are separated with ";"