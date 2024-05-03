# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 16:48:18 2024

@author: aisystems
"""


import torch
import pandas as pd
import numpy as np
import datetime
import pickle
import json
from langchain import ElasticVectorSearch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.document_loaders.json_loader import JSONLoader
from tqdm import tqdm
import re
import os
import glob
import requests
from elasticsearch import Elasticsearch
import time
from langchain.embeddings import HuggingFaceInstructEmbeddings
from datetime import datetime

cred=""
chnk_size=1200

save_main_pickle = r""
batches_folder = r""
current_batch = r""
log_file=r""



if os.path.exists(save_main_pickle)==False:
    os.makedirs(save_main_pickle)
if os.path.exists(batches_folder)==False:
    os.makedirs(batches_folder)
if os.path.exists(current_batch)==False:
    os.makedirs(current_batch)


embeddings_= HuggingFaceInstructEmbeddings(model_name=r"hkunlp_instructor-xl",model_kwargs={'device':"cuda"})


def delete_files_in_directory(directory_path):
   try:
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")


def run_elastic_search(load_path,continue_from="",embeddings=""):
    print("Continuing from Point: ",continue_from)
    delete_files_in_directory(current_batch)
    load_path+='/*'
    list_of_files = glob.glob(load_path) # * means all if need specific format then *.csv
    list_of_files.sort(key=lambda i:int(i.split(r'batches')[-1].replace("\\","").split('.pickle')[0].split('batch')[0]),reverse=False)
    #print(list_of_files)
    total_batches=len(list_of_files)
    #
    t1=time.time()
    print("------------------Uploading----------------------")
  
    for file in tqdm(list_of_files[continue_from:]):
        print(f"Currently Working on file {file.split(r'batches')[-1][1:]}")
        print("")
        with open(file, 'rb') as handle:
             x_load= pickle.load(handle)
             
        f_number=int(file.split(r'batches')[-1].replace("\\","").split('.pickle')[0].split('batch')[0])
        file_name= file.split('\\')[-1]
        
        save_path=os.path.join(current_batch,f"{file_name}")
        with open(save_path,'wb') as handle:
            pickle.dump(x_load,handle)
        
        print("File Placed")
        texts=x_load['texts']
        ids=x_load['ids']
        
        current_dateTime = datetime.now()
        
        db = ElasticVectorSearch.from_documents(texts, embeddings,
                                                elasticsearch_url=f"http://{cred}@localhost:9200",index_name="test",
                                                ids=ids )
        current_dateTime2=datetime.now()
        
        with open(log_file, "a") as f:
            f.write(f"The batch is {file.split(r'batches')[-1][1:]} and time taken {current_dateTime} <---> {current_dateTime2} \n\n")
            f.close()
        
        
        torch.cuda.empty_cache()
        if f_number<(total_batches-1):
            os.remove(save_path)
        
    print("-----------------Done Uploading----------------------")
    
    t2=time.time()
    print(f"Time Taken To Upload the vectors : {(t2-t1)/(60)}min")
    print("\n----------\n")
    return (t2-t1)/(60)

continue_value=0
t=run_elastic_search(load_path=batches_folder,
                     continue_from=continue_value,
                     embeddings=embeddings_
                     )