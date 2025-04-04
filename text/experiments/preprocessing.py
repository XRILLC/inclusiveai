#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script aids in the preprocessing step for the pre-training data.

- Used preprocessing techniques from section 3.1 Pre-Training Data from:
https://aclanthology.org/2024.lrec-main.1283.pdf
"""
from typing import NoReturn
from dataclasses import dataclass

import ftfy
import pandas as pd
import torch
from transformers import MarianMTModel, MarianTokenizer
from datasets import load_dataset, Dataset, DatasetDict

OPEN_DATA = ['Tatoeba', 'OpenSubtitles', 'KDE4', 'wikimedia', 'GNOME']

class IdiomataDataCleaning:
    """
    Idiomata data cleaning pipeline for parallel corpora extracted from OPUS.
    """

    def __init__(self, scored_txt, source, target, save_path):
        self.dataset = scored_txt
        self.source = source
        self.target = target
        self.save_path = save_path

    def filter_by_langid(self) -> NoReturn:
        """
        Filter dataset if the identified language isn't correct.
        """
        with open(self.dataset, "r", encoding="utf-8") as file:
            target_lines = file.readlines()

        target_langid = pd.DataFrame([text.rsplit('\t', maxsplit=1) for text in target_lines], columns=['target', 'langid'])
        target_langid['orig_index'] = target_langid.index

        indices = target_langid[~target_langid['langid'].str.startswith(self.target)].index
        target_filtered = target_langid.drop(indices).drop(columns='langid').dropna()

        target_filtered.to_csv(self.save_path, sep='\t', header=False,\
                               index=False, encoding='utf-8-sig')

    def to_opus(self, bitext_path) -> NoReturn:
        """
        Convert .csv file (bitext) to opus, or moses, format.
        """
        src_path = bitext_path[:-4] + f".{self.source[:3].lower()}"
        tgt_path = bitext_path[:-4] + f".{self.target[:3].lower()}"
        bitext = pd.read_csv(bitext_path)

        source = bitext[self.source]
        target = bitext[self.target]

        source.to_csv(src_path, sep="\t", header=False, index=False, encoding='utf-8')
        target.to_csv(tgt_path, sep="\t", header=False, index=False, encoding='utf-8')

    def to_bitext(self, source_path, target_path) -> NoReturn:
        """
        Convert .txt file to a bitext.
        """
        latter = source_path.split('/', 3)[-1]
        former = source_path.replace(latter, '')
        file_path = former + 'bitext.csv'

        with open(source_path, 'r', encoding='utf-8') as file:
            source_lines = file.readlines()

        src = pd.DataFrame([t.strip().split('\t') for t in source_lines], columns=[self.source])
        src['orig_index'] = src.index

        tgt = pd.read_csv(target_path, sep='\t', names=[self.target, 'orig_index'])

        bitext = pd.merge(src, tgt, on='orig_index', how='inner')
        bitext = bitext.drop(columns=['orig_index'])

        bitext.to_csv(file_path, header=True, index=False, encoding='utf-8-sig')

    def _ftfy(self, example):
        """
        Helper function for fixing encoding. **PENDING**
        """
        for language in [self.source, self.target]:
            text = ftfy.fix_text(example[language])
            example[language] = text

        return example

    def fix_encoding(self, bitext_path) -> NoReturn:
        """
        Fix broken encoding with ftfy library. **PENDING**
        """
        bitext = pd.read_csv(bitext_path)
        bitext = bitext.drop(columns=['orig_index'])

        bitext_enc = bitext.apply(self._ftfy, axis=1)
        bitext_enc.to_csv(bitext_path, header=True, index=False)

    def filter_by_alignment(self):
        """
        TODO: LABSE embeddings for alignment.
        """
        return

    def filter_by_wordlength(self):
        """
        TODO: Filter datasets by predefined min/max.
        """
        return

    def filter_by_alignmentlength(self):
        """
        TODO: ???
        """
        return

@dataclass
class Pair:
    """
    Class for storing source and target language.
    """
    def __init__(self, source, target):
        self.source = source
        self.target = target

@dataclass
class Translator:
    """
    Class for storing machine translation information.
    """
    def __init__(self, model_name, task_prefix):
        self.model_name = model_name
        self.task_prefix = task_prefix

class BackTranslation:
    """
    Backtranslation for a monolingual corpus. **May need to extrapolate to Colab**

    TODO: include LABSE alignment 
    """
    def __init__(self, translator, corpus, pair):
        self.translator = MarianMTModel.from_pretrained(translator.model_name)
        self.tokenizer = MarianTokenizer.from_pretrained(translator.model_name)
        self.task_prefix = translator.task_prefix
        self.source = pair.source
        self.target = pair.target
        self.dataset = load_dataset(path='csv', data_files=corpus, encoding='utf-8',
                                    delimiter='\t', column_names=[self.target, 'idx'],
                                    split='train')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.translator.to(self.device)

    def translate(self, batch):
        """
        Helper function to translate text.
        """
        inputs = list(batch[self.target])
        inputs = [self.task_prefix + x for x in inputs]

        encoded = self.tokenizer(
            inputs,
            max_length=self.tokenizer.model_max_length,
            truncation=True,
            padding=True,
            return_tensors='pt',
            )

        input_ids = encoded.input_ids.to(self.device)
        attention_mask = encoded.attention_mask.to(self.device)

        output = self.translator.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            num_beams=1,
            max_length=self.tokenizer.model_max_length,
            )

        decoded = self.tokenizer.batch_decode(
            output,
            skip_special_tokens=True
            )

        targets = list(batch[self.target])

        return {
            self.source: decoded,
            self.target: targets,
        }

    def word_dropout(self, probability=0.1):
        """
        TODO: Transform the source sentences with noise: word dropout.
        """
        #the probablity relates to the sentence, or the word? likely the word.
        # for each sentence, word dropout is applied.
        # 1. use a tokenizer to get words
        # 2. implement some sort of prob
        # pdb.set_trace()
        # self.datasets
        return

    def word_replacement(self):
        """
        TODO: Replace words with synset.
        """
        return

    def word_swap(self):
        """
        TODO: swap words based on probability.
        """
        return 

    def translate_monolingual(self, save_path) -> None:
        """
        Use helper function to map translations to dataset object.
        """
        results = self.dataset.map(
            self.translate,
            batched=True,
            batch_size=125,
            )

        results.to_pandas()
        results.to_csv(save_path, header=True, index=False)

def huggingface_push(bitexts_list, bitext_dict) -> None:
    """
    Push dataset to Hugging Face hub.
    """
    datasets = []

    for path in bitexts_list:
        bitext = Dataset.from_pandas(pd.read_csv(path))
        datasets.append(bitext)

    ddict = DatasetDict(bitext_dict)
    # TODO
    # ddict = DatasetDict({
    #     "OpenSubtitles": opensubtitles,
    #     "Tatoeba": tatoeba,
    #     "KDE4": KDE4,
    #     "wikimedia": wikimedia,
    #     "GNOME": GNOME,
    #     "PILARliterary": PILAR1,
    #     "PILARcrawled": PILAR2
    #     })
    return ddict


def main():
    """
    Main
    """
    bt = BackTranslation()
    bt.word_dropout()
    return

if __name__ == '__main__':
    main()
