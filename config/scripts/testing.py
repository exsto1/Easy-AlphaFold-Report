from check_alphafold import *
from verify_input import *
from batch_uniprot import *


def test_main():
    def test_alphafold():
        print("1. Test Alphafold")
        try:
            res = alphafold_verify(["B0BNG7", "B5R6I4", "XXXXXX"],
                                   file="../data/alpha_fold_data.txt")
        except:
            print("TECH ERROR - check dependencies and folder architecture.")
            return False
        expected = ['B0BNG7', 'B5R6I4']
        if res == expected:
            return True
        else:
            print("ERROR: Alphafold check failed. Is the data file missing? Check /config/data/AlphaFold_metadata.txt file.")
            return False

    def test_pfam():
        print("2. Test Pfam Clans")
        res = input_parse(["CL0057", "PF01402", "PAN domain"], filepath0="../data/Pfam-A.clans.tsv")
        expected = (['pf01340', 'pf01402', 'pf02697', 'pf03693', 'pf03869', 'pf04221', 'pf05509', 'pf05534', 'pf05713', 'pf07181', 'pf07328', 'pf07362', 'pf07704', 'pf07764', 'pf07878', 'pf08681', 'pf08870', 'pf08972', 'pf09274', 'pf09386', 'pf09957', 'pf10723', 'pf10784', 'pf10802', 'pf11020', 'pf11423', 'pf11903', 'pf12441', 'pf12651', 'pf13467', 'pf14384', 'pf15919', 'pf15970', 'pf16762', 'pf16777', 'pf17206', 'pf17414', 'pf17723', 'pf18064', 'pf19514', 'pf19807', 'pf19839', 'pf19891', 'pf00024', 'pf14295'], [], [])
        if res == expected:
            return True
        else:
            print("ERROR: Pfam check failed. Is the data file missing? Check /config/data/Pfam-A.clans.tsv file.")
            return False

    def test_uniprot():
        print("3. Test Uniprot")
        res, _ = uniprot_check(uniprot=["B8E3L7"])
        if len(res) == 1 and res["Entry"][0] == "B8E3L7":
            return True
        else:
            print("ERROR: Uniprot check failed. Do you have an internet connection? If so, Uniprot servers might be down. Try again later.")
            return False


    max_score = 3
    score = 0
    score += test_alphafold()
    score += test_pfam()
    score += test_uniprot()

    if score == max_score:
        print("Test completed! No errors detected.")


if __name__ == '__main__':
    test_main()
