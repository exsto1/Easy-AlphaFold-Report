from urllib import request
import requests
from tqdm import tqdm
import pandas as pd


def get_new_database_alpha():
    url = "http://ftp.ebi.ac.uk/pub/databases/alphafold/accession_ids.txt"
    # request.urlretrieve(url, "alpha_fold_new.txt")

    r = requests.get(url, stream=True)

    with open("../data/alpha_fold_metadata.txt", 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)


def prepare_file(file="../../config/data/alpha_fold_metadata.txt"):
    with open(file) as file_h:
        file = file_h.readlines()
        file = [i.split(",")[0] for i in file]

    file.sort()

    with open("../../config/data/alpha_fold_data.txt", "w") as out:
        out.write("\n".join(file))


def alphafold_verify(UNI_IDs, file="config/data/alpha_fold_data.txt"):
    with open(file) as file_h:
        file = file_h.readlines()
    file = [i.rstrip() for i in file]

    UNI_IDs.sort()
    UNI_IDs = [i for i in UNI_IDs if i]
    found_IDS = []

    prefix = 3
    data_file = {}
    for i in range(len(UNI_IDs)):
        if UNI_IDs[i][0:prefix] not in data_file:
            data_file[UNI_IDs[i][0:prefix]] = [UNI_IDs[i]]
        else:
            data_file[UNI_IDs[i][0:prefix]].append(UNI_IDs[i])

    data_ref = {}
    for i in range(len(file)):
        if file[i][0:prefix] not in data_ref:
            data_ref[file[i][0:prefix]] = [file[i]]
        else:
            data_ref[file[i][0:prefix]].append(file[i])

    for i in data_file:
        for i1 in range(len(data_file[i])):
            if i in data_ref:
                if data_file[i][i1] in data_ref[i]:
                    found_IDS.append(data_file[i][i1])

    return found_IDS


if __name__ == '__main__':

    # res = alphafold_verify(["B0BNG7", "B5R6I4", "XXXXXX"])
    # test_list = pd.read_csv("../data/temp/uniprot_data.tsv", sep="\t")["Entry"]
    # res = alphafold_verify(test_list, file="../../config/data/alpha_fold_data.txt")
    # get_new_database_alpha()
    # prepare_file()
    pass
