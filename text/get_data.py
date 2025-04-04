#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program generates various files (i.e., CSV and XLSX) in the /data directory for machine 
translation datasets from Hugging Face and language pairs that contains the number of examples. 

- The initial file is generated for comparision with the data refresh to highlight newly added, 
modified, and removed datasets.

- The secondary file is genereated from the initial file for the language pairs present in the
parallel corpora.
"""

import argparse
import os
import re
import sys
import ast
import logging
# import pdb

from huggingface_hub import HfApi
from datasets import load_dataset_builder, disable_progress_bar, get_dataset_config_names
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', \
                    handlers=[logging.StreamHandler(sys.stdout)])
disable_progress_bar()

COLS = ['Author/Dataset', 'Date of Creation', 'Last Modified', 'Dataset Type', \
        'Hugging Face Link', 'Downloads Last Month', '# Likes', '# Languages', \
        'Supported Languages']
COLS2 = ['Author/Dataset', 'Language Pair', '# Train Set', '# Development Set', '# Test Set']

def create_spreadsheet(datasets, init=False) -> pd.DataFrame:
    """
    Returns a spreadsheet containing machine translation datasets from Huggingface.

    *** init is intended to clean up data. This means 'removed' datasets are completely removed
    from the dataset. If selected you must save the newest mt_hf.csv in the logging folder.***

    :param data: huggingface translation datasets 
    :param init: initializes the starting dataframe for comparision; single-use only!
    :return: pandas dataframe
    """
    data = []

    for dataset in datasets:
        if 'language:code' not in dataset.tags and 'modality:audio' not in dataset.tags:
            langs = list({lang[9:] for lang in dataset.tags if "language:" in lang})
            data.append([dataset.id, dataset.created_at.date(), dataset.last_modified.date(), "",
                            f"https://huggingface.co/datasets/{dataset.id}", 
                            dataset.downloads, dataset.likes, len(langs), langs])
    dataframe = pd.DataFrame(data, columns=COLS)

    if init:
        df_tagged = pd.read_csv('data/logging/mt_hf_tagged.csv') # VERIFY DATASETS ARE DROPPED
        dataframe['Dataset Type'] = dataframe['Author/Dataset'].map(df_tagged.set_index(\
                                'Author/Dataset')['Dataset Type'])
        dataframe = dataframe.merge(df_tagged, on='Author/Dataset', how='left', suffixes=('', '_y'))
        dataframe = dataframe.drop(columns=dataframe.columns[dataframe.columns.str.endswith('_y')])
        dataframe.to_csv('data/mt_hf.csv', header=True, index=False)

    return dataframe

def merge_dataframes(old_data, new_data) -> tuple[pd.DataFrame, pd.DataFrame,\
                                                 pd.DataFrame, pd.DataFrame]:
    """Helper function to return different merge types"""
    outer = old_data.merge(new_data, on='Author/Dataset', how='outer',\
                            indicator=True, suffixes=('_old', '_new'))

    left = outer[outer['_merge'] == 'left_only']
    right = outer[outer['_merge'] == 'right_only']
    inner = outer[outer['_merge'] == 'both']
    inner = inner.copy()

    inner['Last Modified_old'] = pd.to_datetime(inner['Last Modified_old'],\
                                                format="%Y-%m-%d")
    inner['Date of Creation_old'] = pd.to_datetime(inner['Date of Creation_old'],\
                                                format="%Y-%m-%d")

    updated = inner[inner['Last Modified_old'] != inner['Last Modified_new']]
    unchanged = inner[inner['Last Modified_old'] == inner['Last Modified_new']]

    suffixes = ('_old', '_merge', '_new')
    left = left.drop(columns = left.columns[left.columns.str.endswith(suffixes[1:])])
    right = right.drop(columns = right.columns[right.columns.str.endswith(suffixes[:2])])
    updated = updated.drop(columns=updated.columns[updated.columns.str.endswith(suffixes[:2])])
    unchanged = unchanged.drop(columns=unchanged.columns[unchanged.columns.str.endswith(\
                                                        suffixes[:2])])

    left.columns = unchanged.columns = updated.columns = right.columns = COLS

    return left, unchanged, updated, right

def update_spreadsheet(file, dataframe) -> pd.DataFrame:
    """
    Returns an updated spreadsheet with highlighted rows for newly added data and modified data.

    :param file: old data
    :param mt_data: updated data
    :return: highlighted/fitted excel file
    """
    old_data = pd.read_csv(file, converters={
                            "Date of Creation": lambda x: pd.to_datetime(x).date(),
                            "Last Modified": lambda x: pd.to_datetime(x).date()
                             })
    new_data = create_spreadsheet(dataframe, init=False)

    new_data['Dataset Type'] = new_data['Author/Dataset'].map(old_data.set_index(
                                        'Author/Dataset')['Dataset Type'])

    left, unchanged, updated, right = merge_dataframes(old_data, new_data)

    for row in left.itertuples():
        left.loc[left['Author/Dataset'] == row[1], 'Dataset Type'] = 'Removed'

    refresh = pd.concat([right, updated, unchanged, left], axis=0)
    refresh.to_csv('data/mt_hf.csv', header=True, index=False)

    for obj, status in [(left, 'Removed'), (updated, 'Updated'),\
                        (unchanged, 'Unchanged'), (right, 'New')]:
        obj.insert(0, 'Status', status)

    refresh_status = pd.concat([right, updated, unchanged, left], axis=0)
    with pd.ExcelWriter('references/refresh.xlsx') as writer: # pylint: disable=abstract-class-instantiated
        refresh_status.style.apply(highlight_status, axis=1).to_excel(
                            writer, engine='openpyxl', index=False, freeze_panes=(1,0))
        worksheet = writer.sheets['Sheet1']
        worksheet.autofit()

    return refresh_status

def highlight_status(row) -> None:
    """
    Returns an .xlsx file that highlights three categories (i.e., new, updated, and removed data).

    :param row: row
    :returns: None
    """
    styles = []
    for val in row:
        if isinstance(val, str) and val.startswith('http'):
            styles.append('color: blue')
        else:
            styles.append('')

    if row['Status'] == 'New':
        return ['background-color: lightgreen'] * len(row)
    if row['Status'] == 'Updated':
        return ['background-color: yellow'] * len(row)
    if row['Status'] == 'Removed':
        return ['background-color: red'] * len(row)

    return styles

def log_missing_data(dataset_name, missing_type='Default') -> None:
    """
    TODO
    """

    if missing_type.startswith(('Default', 'Monitor')):
        with open('references/missing_datasets_v1.txt', 'a', encoding='utf-8') as file:
            file.write(f'{dataset_name}\n') #append or write?
    elif missing_type.startswith('Validate'):
        with open('references/missing_datasets_v2.txt', 'a', encoding='utf-8') as file:
            file.write(f'{dataset_name}\n')

def filter_parallel(dataframe) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Filter dataframe to include parallel datasets."""

    parallel_data = dataframe[dataframe['Dataset Type'].str.contains('Parallel',\
                                                                    case=False, na=False)]
    edge_cases = dataframe[(
                    dataframe['Dataset Type'] == 'Parallel') & (dataframe['# Languages'] != 2)]
    edge = edge_cases['Author/Dataset'].unique()
    parallel_data = parallel_data[~parallel_data['Author/Dataset'].isin(edge)]
    filtered_data = parallel_data[['Author/Dataset', 'Dataset Type', 'Supported Languages']]
    return filtered_data, edge_cases

def fill_datum(ds_datum, ds_info) -> list[str, str, int, int, int]:
    """Helper function for adding train/val/split information."""

    for split in ds_info.splits:
        if split.startswith('tr'):
            ds_datum[2] = ds_info.splits[split].num_examples
        elif split.startswith('val'):
            ds_datum[3] = ds_info.splits[split].num_examples
        else:
            ds_datum[4] = ds_info.splits[split].num_examples

    return ds_datum

def create_pairs(dataframe, update=('Default', False), verbose=True) -> tuple[pd.DataFrame,\
                                                                         pd.DataFrame]:
    """
    Returns a dataframe that contains language pairs for Hugging Face datasets.

    :param mt_df: Hugging Face datasets df
    :param update: A full update iterates through all relevant parallel datasets;
                   A simple update only iterates through parallel datasets that are not
                   part of the existing language_pairs_hf.csv file
    :param verbose: Displays verbose error
    :returns: language pairs df
    """
    filtered_data, edge_cases = filter_parallel(dataframe)

    data = []
    for _, row in filtered_data.iterrows():
        try:
            identifier = row['Author/Dataset']

            if row['Dataset Type'].startswith('Parallel'):
                pair = "-".join(ast.literal_eval(row['Supported Languages']))

                if update[0].startswith('Monitor') and update[1] is not False:
                    if not update[1].loc[update[1]['Author/Dataset'] == identifier,\
                                        'Language Pair'].isin([pair]).empty:
                        logging.info("The dataset %s is already loaded.", identifier)
                        continue

                logging.info("Loading dataset: %s", identifier)
                info = load_dataset_builder(identifier, trust_remote_code=True).info

                datum = [identifier, pair, 0, 0, 0]
                data.append(fill_datum(datum, info))

            elif row['Dataset Type'].startswith('Multilingual'):
                logging.info("Getting configs from %s", identifier)
                configs = get_dataset_config_names(identifier)

                if configs[0].startswith('default'):
                    logging.info("Error loading %s. Default setting", identifier)
                    log_missing_data(row['Author/Dataset'], missing_type=update[0])
                    continue

                pattern = r'[a-z]{2,3}((_|-)\w+)?(-|2)[a-z]{2,3}((_|-)\w+)?'

                if not re.fullmatch(pattern, configs[0]):
                    logging.info("Error loading %s. Not a match!", identifier)
                    log_missing_data(row['Author/Dataset'], missing_type=update[0])
                    continue

                for config in configs:
                    if update[0].startswith('Monitor') and update[1] is not False:
                        if not update[1].loc[update[1]['Author/Dataset'] == identifier,\
                                            'Language Pair'].isin([config]).empty:
                            logging.info("The dataset %s has been loaded with config %s",\
                                                                        identifier, config)
                            continue

                    logging.info("Loading %s with conf: %s ", identifier, config)
                    info = load_dataset_builder(identifier, config, trust_remote_code=True).info

                    datum = [identifier, config, 0, 0, 0]
                    data.append(fill_datum(datum, info))

        except Exception as exc: # pylint: disable=broad-except
            if verbose:
                logging.info("%s", exc)
            else:
                logging.info("Error loading dataset %s", identifier)
            log_missing_data(row['Author/Dataset'], missing_type=update[0])

    pairs_df = pd.DataFrame(data,columns=COLS2)

    if update[0].startswith(('Monitor', 'Validate')):
        pairs_df = pd.concat([pairs_df, update[1]])

    pairs_df.to_csv('data/language_pairs_hf.csv', header=True, index=False)

    return pairs_df, edge_cases

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read translation data from Hugging Face.')
    parser.add_argument('scrape', help='Generate files for mt')
    args = parser.parse_args()

    if args.scrape.startswith(('initialize', 'refresh')):
        api = HfApi()
        translation_data = api.list_datasets(filter='task_categories:translation')
        mt_data = list(translation_data)

        if args.scrape == 'initialize':
            _ = create_spreadsheet(mt_data, init=True)

        elif args.scrape == 'refresh':
            _ = update_spreadsheet('data/mt_hf.csv', mt_data)

    elif args.scrape.startswith(('update:create', 'update:monitor')):
        mt_df = pd.read_csv('data/mt_hf.csv')

        if os.path.exists('references/missing_datasets_v1.txt'):
            os.remove('references/missing_datasets_v1.txt')

        if args.scrape == 'update:create':
            _, _ = create_pairs(mt_df, update=('Default', False), verbose=False)

        elif args.scrape == 'update:monitor':
            lang_pairs = pd.read_csv('data/language_pairs_hf.csv')
            _, _ = create_pairs(mt_df, update=('Monitor', lang_pairs), verbose=False)

    elif args.scrape == 'update:validate':
        mt_df = pd.read_csv('data/mt_hf.csv')

        if os.path.exists('references/missing_datasets_v2.txt'):
            os.remove('references/missing_datasets_v2.txt')

        hf_pairs = pd.read_csv('data/language_pairs_hf.csv')
        ext_pairs = pd.read_csv('data/language_pairs_external.csv')
        complete_pairs = pd.concat([hf_pairs, ext_pairs], axis=0)

        old_datasets = complete_pairs['Author/Dataset'].unique()
        mt_df = mt_df[~mt_df['Author/Dataset'].isin(old_datasets)]

        _, _ = create_pairs(mt_df, update=('Validate', hf_pairs), verbose=False)

#1. Automate 'y' option for remote code ds
#2. two hours for full (create?)
#3. 10 minutes for monitor
