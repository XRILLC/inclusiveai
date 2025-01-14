## GENERAL INFORMATION 

*This README.md establishes project level documentation about the data, particulary the "objective" and "approach".*

### OBJECTIVE
Successful machine translation systems often presuppose very large parallel datasets (tens or hundreds of million sentences). Few datasets actually exemplify highly resourced language pairs while most language pairs in the world have limited data, or non-existent data.

There is no comprehensive survey on the available datasets for machine translation and their metadata. The content of the files in this repository include the data available for machine translation datasets and the language pairs, respectively.

### FILE DIRECTORY 

*This section will help users navigate the folders and files that make up the data set.*

```bash
.
├── data/                   # Contains datasets for MT datasets & lang pairs
│   ├── logging/               
│   ├── mt_hf.csv               
│   ├── mt_external.csv
│   ├── language_pairs_hf.csv
│   ├── language_pairs_external.csv
│   └── CODEBOOK.md        
├── get_data.py             # Function for retrieving data 
├── references/             # Files for checking new/missing data
│   ├── refresh.xlsx
│   └── missing_datasets.txt                     
├── Workbook.ipynb               
├── utils.py                
├── README.md               
└── requirements.txt        
```

#### FILE LIST

*A complete list of all of the files/folders in your data set. The file’s name and a short description are included.*

- **data/** 
  - **logging/**, Folder for logged versions of the tagged hf datasets 
  - **mt_hf.csv**, MT datasets from hf (semi-automatic)
  - **mt_external.csv**, MT datasets from external resources (manual)
  - **language_pairs_hf.csv**, data containing language pairs from hf that automatically counts # of rows
  - **language_pairs_external.csv**, data containing language pairs that cannot be extracted automatically
- **references/**
  - **missing_datasets**, Datasets unable to be extracted from hf (e.g., gated or corrupted data)
  - **refresh.xlsx**, User-friendly file for viewing new, updated, and removed datasets from hf
- **get_data.py**
- **Workbook.ipynb**, Workbook for handling or showcasing the datasets
- **utils.py**, Helper program for making tagging tasks easier for manual tagging
- **requirements.txt**

## SOURCES AND METHODS
  
*This section is devoted to the “where” and “how” of the data.*

### DATA SOURCES
MT is data-driven application where we must consider what data sources are already available. Data is arguably the most important factor for translation systems and helps companies whether a dataset needs to be created or currated for future work.

Popular existing resources include:
1.  [Hugging Face](https://huggingface.co/)
2.  [OPUS](https://opus.nlpl.eu/)
3.  Monolingual data
4.  [StatMT](https://statmt.org/)
5.  [Wikipedia](https://www.wikipedia.org/)

Hugging Face is arguably the defacto site for finding parallel datasets in a programmatic fashion and many researchers publish their datasets there. Therefore we will use hf as the main source of parallel datasets and manually add external datasets periodically.

### DATA COLLECTION METHODS 
There are two main data collections we are interested in: machine translation datasets and the language pairs found in these datasets.

The primary data is extracted directly from Hugging Face's API; unfortunately their API does not offer support for finding machine translation datasets exclusively. Meaning a general query is required in hopes of finding the parallel datasets by using the task "Translation" as a proxy. The secondary data is manually tagged according to the format from the hf API. These datasets include any dataset that is not manually uploaded to hf.

Then the language pairs are either inferred from the data or manually tagged when a programmatic method cannot be found. Simple language pairs, when only one pair exists, can be automatically extracted and the number of **rows** in the data can be found. While most examples of parallel data are sentences, certain datasets contain words or various formats that need further preprocessing. That is why we emphasize rows instead of sentences.

**We are in the processing of identifying multilingual language pairs programmatically but have not found a solution** 

### DATA PROCESSING METHODS 
The empirical challenges (as encountered during data collection) are missing languages in the metadata, no consistent indication if a data is parallel, and information on language pairs and their directionality is not always present. 

For that reason, quality assurance procedures are carried out, namely:
1. Identifying which datasets are relevant (i.e., unsupported or parallel).
2. Pull requests on Hugging Face to include missing metadata (e.g., a language that contains an ISO code but isn't generated automatically on hf).
3. We may also be interested in the domain of the dataset, however this is pending further discussion.
   
## Virtual Environment
The data can be generated with a virtual environment. 

```bash
$ git clone inclusiveai
$ cd inclusiveai/text/
$ python3 -m venv .env
$ source .env/bin/activate
$ pip install -r requirements.txt
```

## Get Data
The ```get_data.py``` script generates both a .csv and .xlsx file in ```/data``` for machine translation datasets from Hugging Face. The initial file is generated for comparision with the data refresh to highlight newly added, modified, and removed datasets. 

Initalize the .csv file:

```
python get_data.py initialize    
```

Refresh the data:
```
python get_data.py refresh
```

Retrieve the language pairs:
```
python get_data.py lang-pairs
```
