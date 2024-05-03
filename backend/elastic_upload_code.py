# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 16:51:49 2024

@author: rameez
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 11:21:53 2023

@author: aisystem
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


cred=""
chnk_size=1200

save_main_pickle = r""
batches_folder = r""
current_batch = r""

if os.path.exists(save_main_pickle)==False:
    os.makedirs(save_main_pickle)
if os.path.exists(batches_folder)==False:
    os.makedirs(batches_folder)
if os.path.exists(current_batch)==False:
    os.makedirs(current_batch)


embeddings_= HuggingFaceInstructEmbeddings(model_name=r"hkunlp_instructor-xl",model_kwargs={'device':"cpu"})

def load_clean_json(json_folder):
    loader = DirectoryLoader(json_folder,glob='**/*.json',loader_cls=TextLoader,show_progress=True)
    documents=loader.load()
    documents=documents[0:]
    for cnt in tqdm(range(len(documents))):
        temp_dict=json.loads(documents[cnt].page_content)
        documents[cnt].page_content = re.sub(r' +', ' ',temp_dict['judgment'].replace(r"\u00a0"," ").replace("##TS##"," ").replace("##TE##"," ").replace(r"\u"," ").replace(r'\u201d'," ").replace(r'\u201c'," ").replace("\xa0"," ").replace("\n"," ").replace("--"," ").replace(".."," ").replace("--"," ").replace("**"," "))
        documents[cnt].metadata={'source':temp_dict['id']}
        
    print('Document Cleaned\n')
    print("\n----------\n")
    return documents

def text_splitting(documents):
    print("Inside Text Spltting Doc")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chnk_size, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    texts=[t for t in tqdm(texts) if len(t.page_content)>40]
    
    print('Done Splitting\n')
    print("\n----------\n")
    return texts

def setting_ids_meta_saving(texts):
   x_df=pd.DataFrame([[t,t.metadata['source']] for t in texts],columns=['Text','source'])
   
   unique_mat2=x_df['source'].nunique()
   print("Unique cases are:",unique_mat2)
   
   if unique_mat2==1:
       x_df=pd.concat([x_df,pd.DataFrame({'source':'Filler','Text':['Filler']})]).reset_index(drop=True)
   
   x_df['to_sum'] = 1
   x_df['cum_count'] = (x_df.groupby('source').apply(lambda x: x.to_sum.shift(1).cumsum()).fillna(0).reset_index(0, drop=True))
   
   x_df=x_df[x_df['source']!='Filler'].reset_index(drop=True)
   
   x_df['ID'] = x_df['source']+',v_id'+ x_df['cum_count'].astype(int).astype(str)
   
   x_df=x_df.drop(['to_sum','cum_count'],axis=1)
   x_df['size']=str(chnk_size)
   print("Set Up done now\n")
   print("\n----------\n")
   return x_df


def saving_pickle(save_path,x_df):
    current_time=str(datetime.datetime.now()).replace(" ","_").replace(":",'_').replace(".",'_').replace("-",'_')

    save_folder_pickle=save_path
    save_folder_pickle=os.path.join(save_folder_pickle,f"all_1200_{current_time}.pickle")
    
    y={
       'texts':x_df['Text'].to_list(),
       'source':x_df['source'].to_list(),
       'ids':x_df['ID'].to_list(),
       }
    
    with open(save_folder_pickle, 'wb') as handle:
        pickle.dump(y, handle)
    
    print(f'Done saving, transformed data is saved at: \n {save_folder_pickle}')
    print("\n----------\n")



def convert_pickle_batch_save(temp_text,temp_source,temp_ids,i,save_path):
    x={'texts':temp_text,
       'source':temp_source,
       'ids':temp_ids
       }
    
    save_path=os.path.join(save_path,f"{i}batch.pickle")
    
    with open(save_path,'wb') as handle:
        pickle.dump(x,handle)
        

def splitting_data_batches2(seg=10000,load_path="",save_batches_path=""):
    print("Splitting main Pickle File to make Batches")
    load_path+='/*'
    list_of_files = glob.glob(load_path) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    
    with open(latest_file,'rb') as file:
        x_load=pickle.load(file)
    
    cnt=int(len(x_load['texts'])/seg)
    cnt2=len(x_load['texts'])/seg
    trav_x=0
    trav_y=seg
    
    save_path=save_batches_path
    
    if cnt!=0:
        
            
        for i in range(cnt):
            if i!=(cnt-1):
                
                temp_text=x_load['texts'][trav_x:trav_y]
                temp_source=x_load['source'][trav_x:trav_y]
                temp_ids=x_load['ids'][trav_x:trav_y]
                
                my_pic = convert_pickle_batch_save(temp_text,temp_source,temp_ids,i,save_path)
                
            else:
                temp_text=x_load['texts'][trav_x:]
                temp_source=x_load['source'][trav_x:]
                temp_ids=x_load['ids'][trav_x:]
                my_pic = convert_pickle_batch_save(temp_text,temp_source,temp_ids,i,save_path)
                
            
            trav_x+=seg
            trav_y+=seg
    
    else:
    
        temp_text=x_load['texts'][0:]
        temp_source=x_load['source'][0:]
        temp_ids=x_load['ids'][0:]    
        my_pic = convert_pickle_batch_save(temp_text,temp_source,temp_ids,cnt,save_path)

    print("Done, Batches made and placed int the directory:\n",save_path)
    

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
        
        
        db = ElasticVectorSearch.from_documents(texts, embeddings,
                                                elasticsearch_url=f"http://{cred}@localhost:9200",index_name="test",
                                                ids=ids )
        torch.cuda.empty_cache()
        if f_number<(total_batches-1):
            os.remove(save_path)
        
    print("-----------------Done Uploading----------------------")
    
    t2=time.time()
    print(f"Time Taken To Upload the vectors : {(t2-t1)/(60)}min")
    print("\n----------\n")
    return (t2-t1)/(60)




def view_stats():
    print("-----------------------------")
    print(requests.get(f"http://{cred}@localhost:9200").text)
    print("-----------------------------")
    print(requests.get(f"http://{cred}@localhost:9200/_cat/indices").text)
    print("-----------------------------")
    print(requests.get(f"http://{cred}@localhost:9200/_cat/shards").text)
    print("-----------------------------")
    print(requests.get(f"http://{cred}@localhost:9200/_cat/shards/test").text)
    print("-----------------------------")
    print(requests.get(f"http://{cred}@localhost:9200/test/_count").json())
    
def delete_instance():

    #client = Elasticsearch(f"http://{cred}@localhost:9200")
    #client.indices.delete(index='test', ignore=[400, 404])
    

def query(q='None',k='None'):
    pass



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

json_folder = r"" #Folders where individual documents in json format are present{id:unique_name_of_document, judgment_text:"judgment text"}

documents=load_clean_json(json_folder)
texts=text_splitting(documents)

x_df=setting_ids_meta_saving(texts)

saving_pickle(save_main_pickle,x_df)

splitting_data_batches2(seg=50,load_path=save_main_pickle,save_batches_path=batches_folder)

view_stats()

cnt_from=0
t=run_elastic_search(load_path=batches_folder,continue_from=cnt_from,embeddings=embeddings_)

view_stats()















