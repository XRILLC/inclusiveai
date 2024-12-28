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
