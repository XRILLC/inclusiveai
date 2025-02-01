## GENERAL INFORMATION
This README.md establishes file level documentation about the data, particulary the "datasets" and "language pairs".

### DATA DICTIONARY
The data consists of two splits for datasets and pairs. Each split contains automated and manually tagged data. 

- Datasets
  - ```mt_hf.csv```
  - ```mt_external.csv```
- Language pairs
  - ```language_pairs_hf.csv```
  - ```language_pairs_external.csv```

### VARIABLES
The data dictionary for each split is below. Each split contains possible amendments that can enrich the data/presentation.

#### DATASET 
| **Variable**            | **Definition**                                                                                  |
|--------------------------|-----------------------------------------------------------------------------------------------|
| `Author/Dataset`         | The creator of the dataset and/or the dataset name.                                           |
| `Date of Creation`       | The date when the dataset was first created.                                                  |
| `Last Modified`          | The most recent date when the dataset was updated.                                            |
| `Dataset Type`           | The purpose or format of the dataset (e.g., parallel, multilingual parallel, unsupported).   |
| `Hugging Face Link`      | A URL linking to the dataset's page on the Hugging Face platform.                             |
| `Downloads Last Month`   | The number of times the dataset was downloaded in the past month.                             |
| `# Likes`                | The number of likes or upvotes the dataset has received on Hugging Face.                      |
| `# Languages`            | The total number of languages included in the dataset.                                        |
| `Supported Languages`    | A list of specific languages available in the dataset in ISO 639-1 and ISO 639-3 format.                                        |

> The ```Dataset Type``` is missing information that requires tagging. We may consider the inclusion of domain metadata information; however that assumes more tagging is needed for each refresh update.

#### LANGUAGE PAIRS 
| **Variable**         | **Definition**                                                                      |
|-----------------------|-------------------------------------------------------------------------------------|
| `Author/Dataset`      | The creator of the dataset and/or the dataset name.                                |
| `Language Pair`       | The source and target languages for the dataset (e.g., English-French).            |
| `# Train Set`         | The number of examples available in the training set of the dataset.               |
| `# Development Set`   | The number of examples available in the development/validation set of the dataset. |
| `# Test Set`          | The number of examples available in the test set of the dataset.                   |

> The # train, development, and test set refers to the rows in each data split. Most frequently these are sentences but occasionally are words or a source sentence in one row only with the translation following.
