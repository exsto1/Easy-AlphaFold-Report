from check_alphafold import *


def test_main():
    def test_alphafold():
        print("1. Test alphafold")
        res = alphafold_verify(["B0BNG7", "B5R6I4", "XXXXXX"])
        expected = ['B0BNG7', 'B5R6I4']
        if res == expected:
            return True
        else:
            print("ERROR: Alphafold check failed. Is the data file missing? Check /config/data/AlphaFold_metadata.txt file.")
            return False


    max_score = 1
    score = 0
    score += test_alphafold()

    if score == max_score:
        print("Test completed! No errors detected.")


if __name__ == '__main__':
    test_main()
