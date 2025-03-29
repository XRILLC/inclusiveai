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
		assert False, f"The mt_hf.csv file contains null values.\n" \
					  f"{read_data[0].isnull().sum()}"
	if null_2.any():
		assert False, f"The mt_external.csv file contains null values.\n" \
					  f"{read_data[1].isnull().sum()}"

def test_supported_languages(read_data): # consistency
	empty_hf = read_data[0][read_data[0]['Supported Languages'] == '[]']

	if len(empty_hf) > 0:
		assert False, f"The mt_hf.csv file contains {len(empty_hf)} instances of empty supported languages."

def test_parallel(read_data): # consistency
	edge_naught = read_data[0][(read_data[0]['Dataset Type'] == 'Parallel') & (read_data[0]['# Languages'] != 2)]
	
	if len(edge_naught) > 0:
		assert False, f"The mt_hf.csv file contains {len(edge_naught)} instances of inconsistency" \
					  f"A simple parallel dataset should contain two languages, no more and no less."

def test_multilingual(read_data): # consistency
	edge_one = read_data[0][(read_data[0]['Dataset Type'] == 'Multilingual Parallel') & (read_data[0]['# Languages'] <= 2)]
	edge_one = edge_one[~edge_one['Supported Languages'].isin(("['Multilingual']", "['multilingual']"))]

	if len(edge_one) > 0:
		assert False, f"The mt_hf.csv file contains {len(edge_one)} instances of inconsistency. " \
					  f"A multilingual dataset should contain more than two languages, not less."

