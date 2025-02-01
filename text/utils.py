import pandas as pd
import pdb 

def update_pairs(dataset_author, supp_langs, n_rows, dtype='Multiway', save_df=False):
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
        pairs = [tuple((l1, l2)) for l2 in supp_langs for l1 in supp_langs if l1.startswith(('eng', 'en')) and not l2.startswith(('eng','en'))]
    elif dtype == 'Simple Parallel':
        pairs = [tuple(supp_langs)]
    elif dtype == 'Pivot-Based':
        #TODO
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

def other_function():
	pass