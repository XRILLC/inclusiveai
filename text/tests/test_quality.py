# Data quality tests
import pandas as pd 
import pytest
import itertools

import pdb

@pytest.fixture
def read_data():
	mt_path = ["data/mt_hf.csv", "data/mt_external.csv"]
	pairs_path = ["data/language_pairs_hf.csv", "data/language_pairs_external.csv"]

	dataframes = []
	for path in itertools.chain(mt_path, pairs_path):
		df = pd.read_csv(path)
		dataframes.append(df)

	return dataframes

def test_uniqueness_mt(read_data): # uniqueness
	ids_hf = read_data[0]['Author/Dataset']
	ids_ext = read_data[1]['Author/Dataset']

	if len(ids_hf) != len(ids_hf.unique()):
		assert False, f"The mt_hf.csv file contains duplicates. " \
					  f"Please verify the file contains only one instance of each author/dataset."

	if len(ids_ext) != len(ids_ext.unique()):
		assert False, f"The mt_external.csv file contains duplicates. " \
					  f"Please verify the file contains only one instance of each author/dataset."

def test_null(read_data): # completenesss
	null_1 = read_data[0].isnull().any()
	null_2 = read_data[1].isnull().any()

	if null_1.any():
		assert False, f"The mt_ht.csv file contains null values.\n" \
					  f"{read_data[0].isnull().sum()}"
	if null_2.any():
		assert False, f"The mt_external.csv file contains null values.\n" \
					  f"{read_data[1].isnull().sum()}"


def test_supported_languages(read_data): # consistency
	#TODO
	pass

def test_uniqueness_pairs(read_data): #directionality might matter here; pending! might not need.
	#TODO
	pass



