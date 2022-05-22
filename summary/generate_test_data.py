


import numpy as np
import pandas as pd

import random
random.seed(222)


'''
def generate_input_report():
	#columns = ["ID", "was_entry_found", "Database", "how_many_structures", "how_many_predictions"]

	ids = []
	was_entry_found =[]
	db = []
	how_many_structures =[]
	how_many_predictions = []

	valid = [True]*10 +[False]*3
	databases = ["Uniprot", "PDB", "Pfam"]
	hm_structures = [1,1,1,1,1,1,1,1,1,1,110,100,120,130,140,50,1200,5000, 800]
	hm_predictions = [1,1,1,1,2,5]

	input_size = 15
	for i in range(input_size):
		ids.append(f"id_{i}")
		was_entry_found.append(random.choice(valid))
		db.append( None if was_entry_found[i]==False else random.choice(databases) )
		how_many_structures.append( 0 if was_entry_found[i]==False else random.choice(hm_structures))
		how_many_predictions.append(min(random.choice(hm_predictions), how_many_structures[i]))

	list_of_tuples = list(zip(ids, was_entry_found, db, how_many_structures, how_many_predictions))
	df = pd.DataFrame(list_of_tuples, columns = ["ID", "was_entry_found", "Database", "how_many_structures", "how_many_predictions"])

	return df.fillna(value=np.nan)
'''


def generate_general_data():
	#[not_found_num, Pfam_ids_num, PDB_inds_num, Uniprot_ids_num, total_structures_found, alphafold_structures_num]
	not_found = random.choice([0,0,0,0,0,0,0,0,0,1,2,3])
	pfam = random.choice([0,1,5,17,10,20,50,100])
	pdb = random.choice([0,1,5,15,17, 20, 40, 50])
	uniprot = random.choice([1,3,14, 18, 20, 40, 100, 200])
	total = random.choice([10, 50, 130, 400, 700, 1500])
	alphafold = int(round((total / random.choice([1.5, 2,3,4])), 0))

	return [not_found, pfam, pdb, uniprot, total, alphafold]



def generate_pLDDT_data():

	lengths = [1000, 999, 800, 900, 850]
	entries_num=10

	plddt=[]
	ids=[]
	for i in range(entries_num):
		ids.append(f"id_{i}")
		plddt.append(np.random.uniform(30, 100, random.sample(lengths,1)))

	plddt_data = {
	    "IDs" :ids,
	    "pLDDT":plddt,
	}
	plddt_data = pd.DataFrame(plddt_data)

	return plddt_data







'''
plddt_data = generate_pLDDT_data()


from statistics import mean
plddt_data.insert(loc=2, column="mean_plddt", value = list(map( mean, plddt_data["pLDDT"])))

print(plddt_data)
print(plddt_data["mean_plddt"].max())
'''

'''
input_report = generate_input_report()
print(input_report)

print(input_report["was_entry_found"].sum())
'''

#print(generate_general_data())
#not_found, pfam, pdb, uniprot, total, alphafold = generate_general_data()
#print(not_found)
#print(pfam)


