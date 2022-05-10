import requests as r
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


def split_list_into_chunks(IDS):
    # number of items in the list after the split
    chunk_size = 50

    result = [IDS[i:i + chunk_size] for i in range(0, len(IDS), chunk_size)]
    return result


def uniprot_dowlander(IDS: str, database_type: str):
    Url = "https://rest.uniprot.org/uniprotkb/stream?fields=accession%2Creviewed%2Cid%2Clength%2Cxref_pfam%2Cxref_pdb&format=tsv&query="

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
    response = r.get(Url)
    tsv_uniprot = response.content.decode()

    return "\n".join(tsv_uniprot.split("\n")[1:])


def uniprot_to_file(pfam=None, pdb=None, uniprot=None):
    path = "config/data/uniprot_data.tsv"
    data = "Entry	Reviewed	Entry Name	Length	Pfam	PDB\n"

    heder = len(data)

    if pfam:
        chunk_pfam = split_list_into_chunks(pfam)
        for i in chunk_pfam:
            data += uniprot_dowlander(i, 'pfam')

    if pdb:
        chunk_pdb = split_list_into_chunks(pdb)
        for i in chunk_pdb:
            data += uniprot_dowlander(i, 'PDB')

    if uniprot:
        chunk_uniprot = split_list_into_chunks(uniprot)
        for i in chunk_uniprot:
            data += uniprot_dowlander(i, 'uniprot')

    if heder == len(data):
        return False

    with open(path, "w") as ff:
        ff.write(data)

    return StringIO(data)


if __name__ == '__main__':
    pass