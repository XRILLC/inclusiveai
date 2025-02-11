from huggingface_hub import HfApi
from datasets import load_dataset_builder, disable_progress_bar, get_dataset_config_names
from datasets import logging as datasets_logging
import pandas as pd
import argparse
import os
import re
import sys
import ast
import logging
import pdb

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
disable_progress_bar()

COLS = ['Author/Dataset', 'Date of Creation', 'Last Modified', 'Dataset Type', 'Hugging Face Link', 
		'Downloads Last Month', '# Likes', '# Languages', 'Supported Languages']
COLS2 = ['Author/Dataset', 'Language Pair', '# Train Set', '# Development Set', '# Test Set']

def create_spreadsheet(datasets, init=False):
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
			langs = list(set([lang[9:] for lang in dataset.tags if "language:" in lang])) 
			data.append([dataset.id, dataset.created_at.date(), dataset.last_modified.date(), "",
							f"https://huggingface.co/datasets/{dataset.id}", 
							dataset.downloads, dataset.likes, len(langs), langs])
	df = pd.DataFrame(data, columns=COLS)

	if init: 
		df_tagged = pd.read_csv('data/logging/mt_hf_tagged.csv') # VERIFY DATASETS ARE DROPPED
		df['Dataset Type'] = df['Author/Dataset'].map(df_tagged.set_index('Author/Dataset')['Dataset Type'])
		df = df.merge(df_tagged, on='Author/Dataset', how='left', suffixes=('', '_y'))
		df = df.drop(columns=df.columns[df.columns.str.endswith('_y')])
		df.to_csv('data/mt_hf.csv', header=True, index=False)

	return df

def update_spreadsheet(file, mt_data):
	"""
	Returns an updated spreadsheet with highlighted rows for newly added data and modified data.

	:param file: old data
	:param mt_data: updated data
	:return: highlighted/fitted excel file
	"""
	old_data = pd.read_csv(file)

	new_data = create_spreadsheet(mt_data, init=False)
	new_data['Dataset Type'] = new_data['Author/Dataset'].map(old_data.set_index('Author/Dataset')['Dataset Type'])

	outer = old_data.merge(new_data, on='Author/Dataset', how='outer', indicator=True, suffixes=('_old', '_new')) 
	left = outer[outer['_merge'] == 'left_only'] 
	right = outer[outer['_merge'] == 'right_only'] 
	inner = outer[outer['_merge'] == 'both']
	inner = inner.copy()

	inner['Last Modified_old'] = pd.to_datetime(inner['Last Modified_old'], format="mixed") 
	inner['Date of Creation_old'] = pd.to_datetime(inner['Date of Creation_old'], format="mixed") 
	
	updated = inner[inner['Last Modified_old'] != inner['Last Modified_new']] 
	unchanged = inner[inner['Last Modified_old'] == inner['Last Modified_new']] 

	suffixes = ('_old', '_merge', '_new')
	left = left.drop(columns = left.columns[left.columns.str.endswith(suffixes[1:])])
	right = right.drop(columns = right.columns[right.columns.str.endswith(suffixes[:2])])
	updated = updated.drop(columns=updated.columns[updated.columns.str.endswith(suffixes[:2])])	
	unchanged = unchanged.drop(columns=unchanged.columns[unchanged.columns.str.endswith(suffixes[:2])])

	left.columns = unchanged.columns = updated.columns = right.columns = COLS 

	for row in left.itertuples():
		left.loc[left['Author/Dataset'] == row[1], 'Dataset Type'] = 'Removed'

	refresh = pd.concat([right, updated, unchanged, left], axis=0) 
	refresh.to_csv('data/mt_hf.csv', header=True, index=False)

	for obj, status in [(left, 'Removed'), (updated, 'Updated'), (unchanged, 'Unchanged'), (right, 'New')]:
		obj.insert(0, 'Status', status)
	
	refresh_status = pd.concat([right, updated, unchanged, left], axis=0) 
	with pd.ExcelWriter('references/refresh.xlsx') as writer:
		refresh_status.style.apply(highlight_status, axis=1).to_excel(writer, engine='openpyxl', index=False, freeze_panes=(1,0))
		worksheet = writer.sheets['Sheet1']
		worksheet.autofit()

	return refresh_status

def highlight_status(row):
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
	elif row['Status'] == 'Updated':
		return ['background-color: yellow'] * len(row)
	elif row['Status'] == 'Removed':
		return ['background-color: red'] * len(row)
	else:
		return styles

def log_missing_data(dataset_name, missing_type='Default'): 
	"""
	TODO
	"""
	if missing_type.startswith(('Default', 'Monitor')):		
		with open('references/missing_datasets_v1.txt', 'a') as f:
			f.write(f'{dataset_name}\n')
	elif missing_type.startswith('Validate'):
		with open('references/missing_datasets_v2.txt', 'a') as f:
			f.write(f'{dataset_name}\n')

def create_pairs(mt_df, update=('Default', False), verbose=True):
	"""
	Returns a dataframe that contains language pairs for Hugging Face datasets.

	:param mt_df: Hugging Face datasets df
	:param update: A full update iterates through all relevant parallel datasets;
				   A simple update only iterates through parallel datasets that are not
				   part of the existing language_pairs_hf.csv file
	:param verbose: Displays verbose error
	:returns: language pairs df
	"""
	parallel_data = mt_df[mt_df['Dataset Type'].str.contains('Parallel', case=False, na=False)]
	edge_cases = mt_df[(mt_df['Dataset Type'] == 'Parallel') & (mt_df['# Languages'] != 2)]
	edge = edge_cases['Author/Dataset'].unique()
	parallel_data = parallel_data[~parallel_data['Author/Dataset'].isin(edge)]
	mt_data = parallel_data[['Author/Dataset', 'Dataset Type', 'Supported Languages']]

	data = []
	for _, row in mt_data.iterrows(): 
		try:
			ID = row['Author/Dataset'] 

			if row['Dataset Type'].startswith('Parallel'):
				langs = ast.literal_eval(row['Supported Languages'])
				pair = "-".join(langs)

				if update[0].startswith('Monitor') and update[1] is not False:
					if not update[1].loc[update[1]['Author/Dataset'] == ID, 'Language Pair'].isin([pair]).empty:
						logging.info(f"The dataset {ID} is already loaded.")
						continue

				datum = [ID, pair, 0, 0, 0]
				logging.info(f"Loading dataset: {ID}")

				builder = load_dataset_builder(ID, trust_remote_code=True) 
				info = builder.info

				for split in info.splits:
					if split.startswith('tr'):
						datum[2] = info.splits[split].num_examples
					elif split.startswith('val'):
						datum[3] = info.splits[split].num_examples
					else:
						datum[4] = info.splits[split].num_examples
				data.append(datum)
            
			elif row['Dataset Type'].startswith('Multilingual'): 
				configs = get_dataset_config_names(ID)
				if configs[0].startswith('default'):
					continue

				pattern = r'[a-z]{2,3}((_|-)\w+)?(-|2)[a-z]{2,3}((_|-)\w+)?'

				if not re.fullmatch(pattern, configs[0]): 
					logging.info(f"Error loading dataset {ID}. Not a match!")
					log_missing_data(row['Author/Dataset'], missing_type=update[0]) 
					continue

				for config in configs: 
					if update[0].startswith('Monitor') and update[1] is not False:
						if not update[1].loc[update[1]['Author/Dataset'] == ID, 'Language Pair'].isin([config]).empty:
							logging.info(f"The dataset {ID} is already loaded with config {config}.")
							continue

					datum = [ID, config, 0, 0, 0]

					logging.info(f"Loading dataset: {ID} with config: {config}")
					builder = load_dataset_builder(ID, config, trust_remote_code=True)
					info = builder.info

					for split in info.splits:
						if split.startswith('tr'):
							datum[2] = info.splits[split].num_examples
						elif split.startswith('val'):
							datum[3] = info.splits[split].num_examples
						else:
							datum[4] = info.splits[split].num_examples
					data.append(datum)

		except Exception as e: 
			if verbose:
				logging.info(f"{e}")
			else:
				logging.info(f"Error loading dataset {ID}")
			log_missing_data(row['Author/Dataset'], missing_type=update[0])

		except KeyboardInterrupt:
			print('Caught KeyboardInterrupt, exiting...')
			exit()

	df = pd.DataFrame(data,columns=COLS2) 

	if update[0].startswith(('Monitor', 'Validate')): 
		df = pd.concat([df, update[1]])

	df.to_csv('data/language_pairs_hf.csv', header=True, index=False)

	return df, edge_cases 

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Read translation data from Hugging Face.')
	parser.add_argument('scrape', help='Generate files for mt')
	args = parser.parse_args()

	if args.scrape.startswith(('initialize', 'refresh')):
		api = HfApi()
		data = api.list_datasets(filter='task_categories:translation')
		mt_data = [dataset for dataset in data]

		if args.scrape == 'initialize':
			df = create_spreadsheet(mt_data, init=True)

		elif args.scrape == 'refresh':
			_ = update_spreadsheet('data/mt_hf.csv', mt_data)

	elif args.scrape.startswith(('update:create', 'update:monitor')): 
		mt_df = pd.read_csv('data/mt_hf.csv') 

		if os.path.exists('references/missing_datasets_v1.txt'):
			os.remove('references/missing_datasets_v1.txt')

		if args.scrape == 'update:create':
			_, edge_cases = create_pairs(mt_df, update=('Default', False), verbose=False)

		elif args.scrape == 'update:monitor':
			pairs_df = pd.read_csv('data/language_pairs_hf.csv')
			_, edge_cases = create_pairs(mt_df, update=('Monitor', pairs_df), verbose=False)

	elif args.scrape == 'update:validate': 
	# pending!!! this behaves such that you verify what's missing & do a final validation
		mt_df = pd.read_csv('data/mt_hf.csv')

		if os.path.exists('references/missing_datasets_v2.txt'): 
			os.remove('references/missing_datasets_v2.txt')		

		pairs_df = pd.read_csv('data/language_pairs_hf.csv')
		ext_pairs = pd.read_csv('data/language_pairs_external.csv')
		pairs_df_2 = pd.concat([pairs_df, ext_pairs], axis=0)

		old_datasets = pairs_df_2['Author/Dataset'].unique() 
		mt_df = mt_df[~mt_df['Author/Dataset'].isin(old_datasets)]

		_, edge_cases = create_pairs(mt_df, update=('Validate', pairs_df), verbose=False)

#TODO
#1. Automate 'y' option for remote code ds
#2. two hours for full
#3. 10 minutes for monitor
#4. batch processing
#5. check initialization
#6. Refresh -> Pytest -> Tagging -> (?) Monitor -> Validate
#7. RTmV
