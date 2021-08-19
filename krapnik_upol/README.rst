Script 'comparing_datab_juraskova' check both databases and compare the same result.

Structure in juraskova's file AND molmed are evaluated as solved and are written to results.log, separated with ; They are DONE.
 The rest of structures is unselected and there are written iupac name and iupac smile. These structures are for further processing. Function  'unify_structures_juraskova(name_smile_juraskova.difference(name_smile_databse))'
compare Juraskova's structures and structures from MolMeDB and these strucutre are send to PubChem to unify name and smile. Comparing process with MolMeDB is repeating.


File all_countless_structures_from_juraskova
Structures which are NOT in MolMeDB are written to all_countless_structures_from_juraskova.log and these structures will be handed over


Input: SMILE's file and mol2 file. 
SMILE -> mol2 could be converted by openbabel
(it is possible to use script: convert_smile_2_mol2
