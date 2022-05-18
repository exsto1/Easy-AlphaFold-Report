import pandas as pd
import requests as r
from time import time


def split_list_into_chunks(IDS):
    # number of items in the list after the split
    chunk_size = 50

    result = [IDS[i:i + chunk_size] for i in range(0, len(IDS), chunk_size)]
    return result


def quick_check_func(IDS, database_type):
    Url = "https://rest.uniprot.org/uniprotkb/search?fields=accession%2Creviewed%2Clength%2Cxref_pfam%2Cxref_pdb%2Clineage&format=tsv&query="

    if database_type == "pfam":
        for ID in IDS:
            Url += f"%28xref%3Apfam-{ID}%29%20OR%20"

    elif database_type == "PDB":
        for ID in IDS:
            Url += f"%28xref%3Apdb-{ID}%29%20OR%20"

    elif database_type == "uniprot":
        for ID in IDS:
            Url += f"%28accession%3A{ID}%29%20OR%20"

    Url = Url[:-8]

    Url += "&size=500"

    s = time()
    response = r.get(Url)
    real_time = time() - s
    try:
        res_number = response.headers["x-total-records"]
    except:
        res_number = len(response.content.decode().split("\n")) - 1
    return int(res_number), real_time


def uniprot_quick_check(pfam=None, pdb=None, uniprot=None):
    combined_number = 0
    r_time = 0

    if pfam:
        chunk_pfam = split_list_into_chunks(pfam)
        for i in chunk_pfam:
            number, r_time = quick_check_func(i, 'pfam')
            combined_number += number

    if pdb:
        chunk_pdb = split_list_into_chunks(pdb)
        for i in chunk_pdb:
            number, r_time = quick_check_func(i, 'PDB')
            combined_number += number

    if uniprot:
        chunk_uniprot = split_list_into_chunks(uniprot)
        for i in chunk_uniprot:
            number, r_time = quick_check_func(i, 'uniprot')
            combined_number += number

    return combined_number, r_time


def uniprot_downloader(IDS: str, database_type: str):
    Url = "https://rest.uniprot.org/uniprotkb/search?fields=accession%2Creviewed%2Clength%2Cxref_pfam%2Cxref_pdb%2Clineage&format=tsv&query="

    if database_type == "pfam":
        for ID in IDS:
            Url += f"%28xref%3Apfam-{ID}%29%20OR%20"

    elif database_type == "PDB":
        for ID in IDS:
            Url += f"%28xref%3Apdb-{ID}%29%20OR%20"

    elif database_type == "uniprot":
        for ID in IDS:
            Url += f"%28accession%3A{ID}%29%20OR%20"

    Url = Url[:-8]

    Url += "&size=500"

    response = r.get(Url)
    new_url = ""
    more_pages = True
    try:
        new_url = response.headers["Link"].lstrip("<").split(">")[0]
    except:
        more_pages = False

    tsv_uniprot = response.content.decode()
    tsv_uniprot = [i0.split("\t") for i0 in tsv_uniprot.split("\n") if i0]

    header = tsv_uniprot[0]
    all_data = tsv_uniprot[1:]


    while more_pages:
        response = r.get(new_url)
        if "Link" in response.headers:
            new_url = response.headers["Link"].lstrip("<").split(">")[0]
        else:
            more_pages = False
        tsv_uniprot = response.content.decode()
        tsv_uniprot = [i0.split("\t") for i0 in tsv_uniprot.split("\n")[1:] if i0]
        all_data.extend(tsv_uniprot)

    return all_data, header


def uniprot_check(pfam=None, pdb=None, uniprot=None):
    combined_data = []
    header = None

    if pfam:
        chunk_pfam = split_list_into_chunks(pfam)
        for i in chunk_pfam:
            data, header = uniprot_downloader(i, 'pfam')
            combined_data.extend(data)

    if pdb:
        chunk_pdb = split_list_into_chunks(pdb)
        for i in chunk_pdb:
            data, header = uniprot_downloader(i, 'PDB')
            combined_data.extend(data)

    if uniprot:
        chunk_uniprot = split_list_into_chunks(uniprot)
        for i in chunk_uniprot:
            data, header = uniprot_downloader(i, 'uniprot')
            combined_data.extend(data)

    if not header:
        return False, False

    header.extend(["Genus", "Superkingdom"])
    for i in range(len(combined_data)):
        combined_data[i][3] = [i for i in combined_data[i][3].split(";") if i]
        combined_data[i][5] = [i for i in combined_data[i][5].split(", ") if i]
        try:
            combined_data[i].append([i0.rstrip(" (genus)") for i0 in combined_data[i][5] if "(genus)" in i0][0])
        except:
            combined_data[i].append("")
        try:
            combined_data[i].append([i0.rstrip(" (superkingdom)") for i0 in combined_data[i][5] if "(superkingdom)" in i0][0])
        except:
            combined_data[i].append("")

    pd_data_full = pd.DataFrame(combined_data, columns=header)
    pd_data_full = pd_data_full[['Entry', 'Reviewed', 'Length', 'Pfam', 'PDB', 'Genus', 'Superkingdom']]

    return pd_data_full, True


if __name__ == '__main__':
    pass
