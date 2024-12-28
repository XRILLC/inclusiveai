from huggingface_hub import HfApi
import pandas as pd
import argparse
import pdb

COLS = ['Author/Dataset', 'Date of Creation', 'Last Modified', 'Hugging Face Link',
		'# Downloads', '# Likes', '# Languages', 'Supported Languages']

def create_spreadsheet(datasets, init=False):
	"""
	Returns a spreadsheet containing machine translation datasets
	from Huggingface.

	:param data: huggingface translation datasets 
	:param init: initializes the starting dataframe for comparision; intended
				as one-term use.
	:return: pandas dataframe
	"""
	data = []

	for dataset in datasets:
		langs = [lang[9:] for lang in dataset.tags if "language:" in lang]

		data.append([dataset.id, dataset.created_at.date(), dataset.last_modified.date(),
						f"https://huggingface.co/datasets/{dataset.id}", 
						dataset.downloads, dataset.likes, len(langs), langs])
	df = pd.DataFrame(data, columns=COLS)

	if init:
		df.to_csv('data/mt_hf.csv', header=True, index=False)

	return df

def update_spreadsheet(file, mt_data):
	"""
	Returns an updated spreadsheet with highlighted rows for newly added data
	and modified data.

	:param file: old data
	:param mt_data: updated data
	:return: highlighted/fit excel file
	"""
	old_data = pd.read_csv(file)
	new_data = create_spreadsheet(mt_data, init=False)

	outer = old_data.merge(new_data, on='Author/Dataset', how='outer', indicator=True, suffixes=('_old', '_new')) 
	left = outer[outer['_merge'] == 'left_only'] 
	right = outer[outer['_merge'] == 'right_only'] 
	inner = outer[outer['_merge'] == 'both']
	inner = inner.copy()

	inner['Last Modified_old'] = pd.to_datetime(inner['Last Modified_old']).dt.date
	inner['Date of Creation_old'] = pd.to_datetime(inner['Date of Creation_old']).dt.date
	
	updated = inner[inner['Last Modified_old'] != inner['Last Modified_new']] 
	unchanged = inner[inner['Last Modified_old'] == inner['Last Modified_new']] 

	suffixes = ('_old', '_merge', '_new')
	left = left.drop(columns = left.columns[left.columns.str.endswith(suffixes[1:])])
	right = right.drop(columns = right.columns[right.columns.str.endswith(suffixes[:2])])
	updated = updated.drop(columns=updated.columns[updated.columns.str.endswith(suffixes[:2])])	
	unchanged = unchanged.drop(columns=unchanged.columns[unchanged.columns.str.endswith(suffixes[:2])])

	left.columns = unchanged.columns = updated.columns = right.columns = COLS

	refresh = pd.concat([right, updated, unchanged, left], axis=0) 
	refresh.to_csv('data/mt_hf.csv', header=True, index=False)

	for obj, status in [(left, 'Removed'), (updated, 'Updated'), (unchanged, 'Unchanged'), (right, 'New')]:
		obj.insert(0, 'Status', status)
	
	refresh_status = pd.concat([right, updated, unchanged, left], axis=0) 
	with pd.ExcelWriter('data/refresh.xlsx') as writer:
		refresh_status.style.apply(highlight_status, axis=1).to_excel(writer, engine='openpyxl', index=False, freeze_panes=(1,0))
		worksheet = writer.sheets['Sheet1']
		worksheet.autofit()

	return refresh_status

def highlight_status(row):
	"""
	Returns an .xlsx file that highlights three categories: newly added data, updated data, and
	removed data. 

	:param row: row
	:returns None: background color 
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

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Read machine translation data from Hugging Face.')
	parser.add_argument('scrape', help='Generate file for mt')
	args = parser.parse_args()

	api = HfApi()
	data = api.list_datasets(filter='task_categories:translation')
	mt_data = [dataset for dataset in data]

	if args.scrape == 'initialize':
		df = create_spreadsheet(mt_data, init=True)

	elif args.scrape == 'refresh':
		_ = update_spreadsheet('data/mt_hf.csv', mt_data)

