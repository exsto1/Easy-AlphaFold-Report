# Easy-AlphaFold-Report
# WIP

## Members
Maciej Sikora, Małgorzata Sudoł, Maria Bochenek, Kamil Pawlicki 

## Folder architecture with descriptions
```
Easy-AlphaFold-Report    
 ├─ open_autogui.py (main function)    
 ├─ README.md    
 └─ config     
     ├─ data
     │   ├─ AlphaFold_metadata.txt
     │   ├─ Pfam-A-clans.tsv
     │   └─ temp
     │       ├─ README.md
     │       └─ ... (temp files from Alphafold)
     │
     ├─ other
     │   └─ Pfam.version
     │
     └─ scripts
         ├─ check_alphafold.py
         ├─ gather_data_from_alphafold.py
         ├─ testing.py (basic tests for error collection)
         ├─ verify_input.py
         └─ version_control.py
```

## Project features
- Flexible input providing (direct input, files).
- Convenient usage via GUI.
- Various data type recognition and parsing (Pfam families, clans, PDB, Uniprot).
- Automatic database updates.
- ID verification.
- Data collection from multiple databases (PDB, PFAM, Uniprot, AlphaFold).
- Optional data download from AlphaFold (.cif files)
- Presenting results and statistics in the intuitive and interactive html.













----------------

## Project main goal
Repository for easy access and summary to Alphafold dataset.

Project is targetted at users with biological focus.


## Input
Identificator or list of IDs in Pfam / Uniprot / PDB format.
Input can be provided directly as a flag or as a text file.

### Flags:

| Flag |  Description |
|------|--------------|
| -i   | Input (IDs or path to file)|
| -o   | Output |
| -h   | Help |
| -d   | Download |
| ?    | TBA |

## Output
Summary in html/pdf format with downloaded data from AlphaFold (if needed).

If only Pfam IDs are provided, summaries can be split into respective families.



