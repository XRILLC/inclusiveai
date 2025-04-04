#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script performs simple functions for extracting information for language pairs. 
It also generates a list for supported languages from Google.

GitHub Issues (Google): 
https://github.com/ssut/py-googletrans/issues/268

Discovering supported languages (Google): 
https://cloud.google.com/translate/docs/basic/discovering-supported-languages
"""
import pandas as pd
import requests
from google.cloud import translate_v2 as translate


def update_pairs(dataset_author, supp_langs, n_rows,\
                dtype='Multiway', save_df=False) -> pd.DataFrame:
    """ 
    Function to update the available language pairs in multilingual datasets.

	:param dataset_author: ID from Hugging Face/external dataset
	:params supp_langs: Languages in dataset
	:params n_rows: Number of rows in df in the form (train, val, test); 
                    - List object (parallel, multilingual)
                    - Dictionary object (English-Centric)
	:params dtype: The type of multilingual dataset (Multiway, English-Centric, Pivot-Based)
	:params save_df: Save modified CSV file 
	:return: dataframe 
    """
    if dtype == 'Multiway':
        pairs = [tuple((l1, l2)) for l2 in supp_langs for l1 in supp_langs if l1 != l2]
    elif dtype == 'English-Centric':
        pairs = [tuple((l1, l2)) for l2 in supp_langs for l1 in supp_langs if \
                l1.startswith(('eng', 'en')) and not l2.startswith(('eng','en'))]
    elif dtype == 'Simple Parallel':
        pairs = [tuple(supp_langs)]
    elif dtype == 'Pivot-Based':
        pass

    df = pd.read_csv('data/language_pairs_external.csv')
    for pair in pairs:
        lpair = "-".join(pair)
        data = {'Author/Dataset': dataset_author, 'Language Pair': lpair}
        if dtype.startswith(('Multiway', 'Simple Parallel')):
            data['# Train set'] = n_rows[0]
            data['# Development set'] = n_rows[1]
            data['# Test set'] = n_rows[2]

        elif dtype.startswith('English-Centric'):
            value = n_rows[pair[1]]
            data['# Train set'] = value[0]
            data['# Development set'] = value[1]
            data['# Test set'] = value[2]

        df.loc[len(df)] = data

    if save_df:
        df.to_csv('data/language_pairs_external.csv', header=True, index=False)
    return df

def list_languages(verbose=False) -> dict:
    """
    Lists all available language via public endpoint. 

    The endpoint may not be stable, however it delivers a more accurate representation 
    of languages from Google compared to the method below.
    """

    endpoint = 'https://translate.googleapis.com/translate_a/l?client=gtx'
    languages = requests.get(endpoint, timeout=10).json()['sl']
    del languages['auto']

    with open('references/models/GoogleTranslate_v1.txt', 'w', encoding='utf-8') as file:
        for language in languages:
            file.write(f"{language} {languages[language]}\n")
            if verbose:
                print("{language} {languages[language]}")

    return languages

def list_languages_google(verbose=False) -> dict:
    """Lists all available languages."""
    translate_client = translate.Client()

    results = translate_client.get_languages()
    languages = {}

    with open('references/models/GoogleTranslate_v2.txt', 'w', encoding='utf-8') as file:
        for language in results:
            iso_code, name = language['language'], language['name']
            languages.update({iso_code: name})
            file.write(f"{iso_code} {name}\n")
            if verbose:
                print("{name} ({language})".format(**language))

    return languages

def create_conversion_dict() -> dict:
    """Creates a dictionary to convert from ISO 639-3 to 639-1."""
    conversion_table = pd.read_table('references/iso-639-3.txt', sep='\t')
    cols = ['Id', 'Part1']
    conversion_table = conversion_table[cols]
    conversion_table = conversion_table.dropna()
    iso_mappings = dict(zip(conversion_table['Id'], conversion_table['Part1']))

    return iso_mappings


if __name__ == '__main__':
    supported_Glanguages = list_languages()
    # supported_Glanguages = list_languages_google()
