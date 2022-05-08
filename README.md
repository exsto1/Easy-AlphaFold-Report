# Easy-AlphaFold-Report

## Members
Maciej Sikora, Małgorzata Sudoł, Maria Bochenek, Kamil Pawlicki 

## Project main goal
Easy-AlphaFold-Report is a package with the aim of processing
data between databases easier and faster for the user.

User can provide input in multiple formats - Pfam families, clans, Uniprot or PDB.
Additionally, for even easier access for less tech-savy users,
main script enables use of convenient GUI for more click-oriented experience.

As a result user can expect interactive and easy to read report with a summary
of provided dataset with a focus on AlphaFold database features.
To help with the analysis, basic statistics are also calculated for a quick overview.

Instead of clicking through multiple sites, finding connections between databases,
this package will do the work for you and if you still want to verify the results, or grab more data
links on the report can send you to the respective websites.

Optionally during the summary process, user can also choose to keep the data
from AlphaFold in the .cif files (cif is a more descriptive alternative for PDB files).

## Project features
- Flexible input providing (direct input, files).
- Convenient usage via GUI.
- Various data type recognition and parsing (Pfam families, clans, PDB, Uniprot).
- Automatic database updates.
- ID verification.
- Data collection from multiple databases (PDB, PFAM, Uniprot, AlphaFold).
- Optional data download from AlphaFold (.cif files)
- Presenting results and statistics in the intuitive and interactive html.

----------------------------------

## Usage

For the basic version with GUI user needs to simply run the main python script:
```
python open_autogui.py
```
This should open interactive window ready to use.

### Input

In the interactive version user can provide ID manually via dedicated box or
using file selector provide path to the file.
File should contain 1 ID per line.

For programatic acess, terminal input is also available and uses the same script as a base - but with manual flags:


### Flags:

| Flag | Type  | Description                          |
|------|-------|--------------------------------------|
| -g   | BOOL  | Open in GUI mode (DEF: True)         |
| -i   | PATH  | Input (path to file - 1 ID per line) |
| -o   | PATH  | Output (path to summary file)        | 
| -d   | BOOL  | Download (DEF: False)                |





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