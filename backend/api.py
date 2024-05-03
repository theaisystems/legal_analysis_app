# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 11:25:17 2024

@author: aisystems
"""



import pandas as pd
import datetime as dt
import os
import numpy as np
from flask import Flask, jsonify, request ,make_response
import json
import time
from langchain import ElasticVectorSearch
from langchain.embeddings import HuggingFaceInstructEmbeddings
from elasticsearch import Elasticsearch
import requests as req
import pickle
import os
from elasticsearch import helpers


from pymongo import MongoClient
import re


print("Setting up th MongoDB")

url = '' #enter your mongo URL

# Database Name
db_name = 'all-legal-master'
client = MongoClient(url)
db_mongo = client[db_name]
collection = db_mongo['cases']
logs_collection = db_mongo['legalapp_userlogs']


print("loading the legal user data")
user_collection=db_mongo['legal_users']
df_user = pd.DataFrame(list(user_collection.find({})))

def main_mongo():
    query={}        
    results = collection.find(query, {'judgment':0,'respondant':0,'tagged_statues':0,
                                      'statutesId':0, 'advocate_appeallant': 0,
                                      'advocate_respondant':0,"_id":0})
    data = []
    for res in results:
        data.append(res)
    
    data=pd.DataFrame(data)
    df=data.copy().drop_duplicates(subset=['id',])

    return df



def get_judges_mongo():
    pass

def get_book_mongo():
    pass


books_dict=dict(zip(['PLD', 'PLC', 'PCRLJ', 'SCMR', 'CLC', 'PLJ', 'PTD', 'MLD', 'PTCL',
       'KLR', 'PCTLR', 'YLR', 'CLR', 'CLD', 'NLR', 'PSC CRI', 'PLC(CS)',
       'PHC', 'PSC', 'PSC CIV', 'Comp. C', 'LHC', 'SHC', 'IHC', 'SCP',
       'SCR','M L D','C L C','Y L R','P L D'],['PLD', 'PLC', 'PCRLJ', 'SCMR', 'CLC', 'PLJ', 'PTD', 'MLD', 'PTCL',
              'KLR', 'PCTLR', 'YLR', 'CLR', 'CLD', 'NLR', 'PSC CRI', 'PLC(CS)',
              'PHC', 'PSC', 'PSC CIV', 'Comp. C', 'LHC', 'SHC', 'IHC', 'SCP',
              'SCR','MLD','CLC','YLR','PLD']))
                                       

def get_books(x):
    try:
        mybooks=x.split(",")
    
        if len(mybooks)>0:
            ans=[]
            for bk in mybooks:
                book_to_match=[i for i in list(books_dict.keys()) if i in bk]
                if book_to_match:
                   temp=books_dict[book_to_match[0]]
                   if temp not in ans:
                       ans.append(temp)
            
            return ",".join(ans)
    except:
        return 'N/A'



print("Loading Meta File")


df=main_mongo()
    
cols=['id','court','judgment_date','citation','judges','result','book','title','case_year','appeal']

not_include=[]

df=df[~(df['id'].isin(not_include))].reset_index(drop=True)

df_test=df[df['id']=='6347f4b1944b94c694f630fe_289893']

df=df[cols]



df['book2']=df['citation'].apply(lambda x:get_books(x))

df_check=df.fillna('N/A')[['id','book2']]

df_check=pd.concat([df_check,df_check['book2'].str.split(",",expand=True)],axis=1)
df_check=pd.melt(df_check,id_vars=['id'],value_vars=df_check.columns[2:]).dropna().drop_duplicates(subset=['id','value']).reset_index(drop=True)
df_check=df_check[['id','value']].rename({'value':'book_all'},axis=1)
df_check['book_all']=df_check['book_all'].apply(lambda x : x.strip())



#df_judges=pd.read_excel(os.path.join("/home/aisystem/Work/SHC/Langchain ElasticSearch",'rent-law_cases_updated.xlsx'),sheet_name='Sheet2')

df_judges=df[['id','judges']]
df_judges=df_judges.fillna("N/A")
df_judges=pd.concat([df_judges,df_judges['judges'].str.split(",",expand=True)],axis=1)
df_judges=pd.melt(df_judges,id_vars=['id'],value_vars=df_judges.columns[2:]).dropna().drop_duplicates(subset=['id','value']).reset_index(drop=True)
df_judges=df_judges[['id','value']].rename({'value':'judges'},axis=1)
df_judges['judges']=df_judges['judges'].apply(lambda x : x.strip())
df_judges=df_judges.drop_duplicates(subset=['id','judges']).reset_index(drop=True)



df_main=df_judges.merge(df_check,how='left',on='id')
df_main['book_all']=df_main['book_all'].replace('','N/A')
df_main=df_main.drop_duplicates()
#df_test=df_main[df_main['id']=='6347f4b1944b94c694f630fe_289893']



df['Date2']=pd.to_datetime(df['judgment_date'],format='mixed',dayfirst=True,errors='coerce')
df['Date2']=df['Date2'].dt.strftime("%Y-%m-%d")
df=df.round(decimals=0)
df=df.fillna('N/A')
df['Date']=pd.to_datetime(df['judgment_date'],format='mixed',dayfirst=True,errors='coerce')


judges_all = list(df_main['judges'].unique())
book_all = list(df_main['book_all'].unique())

court_all = list(df['court'].unique())

case_all=list(df['id'].unique())
law_all=['Civil Procedure',
 'Company Law',
 'Corporate Law',
 'Civil Law',
 'Civil Procedure',
 'Constitutional Law',
 'Contract Law',
 'Evidence',
 'India',
 'Civil Law',
 'Civil Procedure',
 'Evidence',
 'Land Law',
 'Land Revenue']


print("Done With Mongo Setup")

cred=""

print("Loading the embedding Model")

embeddings = HuggingFaceInstructEmbeddings(model_name=r"E:\Cleaned_All\Instruct_embed\hkunlp_instructor-xl",model_kwargs={'device':"cpu"})


db= ElasticVectorSearch(
            elasticsearch_url=f"http://{cred}@localhost:9200",
            index_name="test",
            embedding=embeddings
        )

es = Elasticsearch(f"http://{cred}@localhost:9200")

print("Initialized the Vector Store")

def get_cases(search_query):
    pattern = re.compile(search_query, re.IGNORECASE)  # Case-insensitive matching for 'Rent'

    query = { "judgment":{ "$regex":pattern}}

    data = list(collection.find(query, {'_id': 0, 'id':1}))

    cases_mongo=[i['id'] for i in data]
    
    return cases_mongo

def get_cases_txt_ids(search_query,sortby=0):
    """ sortby=0 default (by date)
        sortby=1 (by word_count) """
    search_query=search_query.strip()
    search_query=f" {search_query} "
    pattern = re.compile(search_query, re.IGNORECASE)  # Case-insensitive matching for 'Rent'

    query = { "judgment":{ "$regex":pattern}}

    data = collection.find(query)
    df=pd.DataFrame(data)
    if len(df)>0:
        if sortby==0:
            df=df[['id','judgment','judgment_date']]
            
            
            df['date']=pd.to_datetime(df['judgment_date'],format='mixed',dayfirst=True,errors="coerce")
            df=df.sort_values(by='date',ascending=False).reset_index(drop=True)
            
            cases_mongo=list(df['id'].unique())
            
            return cases_mongo,df
        if sortby==1:
            
            df=df[['id','judgment']]
            
            
            df['Word Count']=df['judgement'].apply(lambda x:x.count(search_query))
            df=df.sort_values(by='Word Count',ascending=False).reset_index(drop=True)
            
            cases_mongo=list(df['id'].unique())
            
            return cases_mongo,df
            
    return [],pd.DataFrame()



def get_mongo_cases2(ids=[]):
    # ids=['6347f34b5544b14314cdefc8_177376',
    #  '6347f3375544b14314cd2790_223271',
    #  '6347f59485a8e8efab6d3df7_348413']
    d=collection.find({'id':{"$in":ids}},{})
    
    x=pd.DataFrame(d)
    x=x[['id','judgment','judgment_date']]
    x['date']=pd.to_datetime(x['judgment_date'],format='mixed',dayfirst=True)
    x=x.sort_values(by='date').reset_index(drop=True)
    
    return {x['id'].values[i]:[" ".join(x['judgment'].values[i].split(" ")[0:200])] for i in range(len(x))}




def get_display_case(ids=[]):
    d=collection.find({'id':{"$in":ids}},{})
    data=[]
    for y in d:
        data.append(y)
    return data[0]



def cl_text(txt):
    txt= re.sub(r' +', ' ',txt.replace(r"\u00a0"," ").replace("##TS##"," ").replace("##TE##"," ").replace(r"\u"," ").replace(r'\u201d'," ").replace(r'\u201c'," ").replace("\xa0"," ").replace("\n"," ").replace("--"," ").replace(".."," ").replace("--"," ").replace("**"," "))
    return txt


def trans_listdict(x=[]):
    my_dict={}
    score_dict={}
    vector_ids={}
    for i in x:
        if i[1] not in my_dict:
            my_dict[i[1]]=[i[0]]
            score_dict[i[1]]=[i[2]]
            vector_ids[i[1]]=[i[3]]
        
        else:
            my_dict[i[1]].append(i[0])
            score_dict[i[1]].append(i[2])
            vector_ids[i[1]].append(i[3])
                
    return my_dict,score_dict,vector_ids



def retreive_docs(db,search_query,filt=None,case_count=20,vect_count=40):
    """ This is the function to get the docs from the vectorstore """
    
    if case_count>100:
        case_count=100
    
    if len(search_query)>0:
        #docs=None
        if filter:
            docs = db.similarity_search_with_score(search_query,k=vect_count,filter=filt)
        else:
            docs =  db.similarity_search_with_score(search_query,k=vect_count)
        # if docs==None:
        #     return {'case':None}
        unique_cases=[]
        cnt=0
        ans_results=[]        
        for d in docs:
            print(d[0].metadata['source'], "->", d[1])
            if d[1]<=1.72:
                break
            ans_results.append([d[0].page_content,d[0].metadata['source'],d[1],d[2]])            # making changes adding d[0]
            if d[0].metadata['source'] not in unique_cases:
                unique_cases.append(d[0].metadata['source'])
                cnt+=1
            if cnt==case_count:
                break
        
        return trans_listdict(x=ans_results)
    else:
        raise "Using the Function incorrectly, look for the function parameters"
        


app = Flask(__name__)



@app.route("/")
def test_api():
    #y=retreive_docs(db,search_query="tenant defaulted")
    y={"Hellow":'Hellow'}
    
    return json.dumps(y)

@app.route("/placefilts",methods=['POST','GET'])
def place_meta():
    if request.args['Meta']=='book':
        ls=list(book_all)
    
    if request.args['Meta']=='judges':
        ls=list(judges_all)
        
    if request.args['Meta']=='court':
        ls=list(court_all)
    
    if request.args['Meta']=='law':
        ls=list(law_all)
    return json.dumps(ls)


@app.route("/updatefilts",methods=['POST','GET'])
def update_filts():
    getdata=request.json['filter']
    
    book=getdata['book'] or None
    if (book==[]) or (book is None):
        book=book_all
    #print("The books are:",book)    
    judges=getdata['judges'] or None
    
    if (judges==[]) or (judges is None):
        judges=judges_all
    #print("The judges are:",judges)
    
    court=getdata['court'] or None
    
    if court==[] or (court is None):
        court=court_all
    #print("The court are:",court)
    
    law=getdata['law'] or None
    if law==[] or (law is None):

        print("True Law not found")
    
        law=law_all

    cases_from_main = list(df_main[(df_main['book_all'].isin(book)) & (df_main['judges'].isin(judges))]['id'].unique())
    print(f"The length of cases are {len(cases_from_main)} now by setting the filts from main is")
    
    temp = df[((df['court'].isin(court)) & (df['id'].isin(cases_from_main)))]
    
    cases_from_filt = list(temp['id'].unique())
    
    print(f"The length of cases are {len(cases_from_filt)} now by setting the filts:")
    #print(judges)
    
    book=list(df_main[df_main['id'].isin(cases_from_filt)]['book_all'].unique())
    judges=list(df_main[df_main['id'].isin(cases_from_filt)]['judges'].unique())
    court=list(temp['court'].unique())
    
    print("The length of judges are: ",len(judges))
    print(book)
    print(court)

    filt_dict={'court':court,
               'book':book,
               'judges':judges,
               'law':law}
               
    
    return json.dumps(filt_dict)
    

@app.route("/t3",methods=['GET','POST'])
def test_api3():
    
    
     flag=False
     xquery=request.json['SearchQuery']
     print(f"The query is:\n {xquery}")
     court=request.json['court'] or None
     judge=request.json['judges'] or None
     book=request.json['book'] or None
     flag=request.json['flag']
     ws=request.json['ws']
     
     fcase=request.json['fcase'] or None
     
     min_date=request.json['startDate']
     max_date=request.json['endDate']
     
     word_cases=get_cases(search_query=ws) if ws!=None else None
     
     
     if word_cases==None:
         word_cases=list(df_main['id'].unique())
     if court==None:
         court=court_all
     if judge==None:
         judge=judges_all
     if book==None:
         book=book_all
     
     if fcase==None:
        fcase=case_all         
         
     
     
     print("The cases are ---------------------------------------------------------")
     
     
     
     
     cases_from_main=list(df_main[((df_main['judges'].isin(judge)) & (df_main['book_all'].isin(book)))]['id'].unique())
     
     cases_list=list(df[((df['court'].isin(court)) & (df['id'].isin(cases_from_main))  & (df['Date']>=min_date) & (df['Date']<=max_date))]['id'].unique())
     
     
     #cases_list=[cs for cs in cases_list if cs in word_cases]
     cases_list=list(set(cases_list) & set(word_cases))
     cases_list=list(set(cases_list) & set(fcase))
     print(f"These are the cases count {len(cases_list)}")
     
     if len(cases_list)>0:
         if flag==False:
             try:
                 y,score_dict,vector_ids=retreive_docs(db,search_query=xquery,filt=None)
                 if (len(y)==0) or (y is None):
                     return json.dumps({'data':"E0"})
             except:
                 return json.dumps({'data':"E0"})
                 
                 
             cases_list2=list(y.keys())
             
             score_dict={key:max(value) for key,value in score_dict.items()}
             
             
             
         else:
             
             mongo_cases,df_mongo_ans=get_cases_txt_ids(search_query=xquery)
             if len(mongo_cases)==0:
                 return json.dumps({'data':"E0"})
                 
             
             print(f'The mongo cases on the query are: {xquery} \n {len(mongo_cases)}')
             #cases_list2=[i for i in mongo_cases if i in cases_list][0:10]
             cases_list2=list(set(mongo_cases) & set(cases_list))[0:10]
             if len(cases_list2)==0:
                 return json.dumps({'data':"E1"})
                 
            
             df_mongo_ans=df_mongo_ans[df_mongo_ans['id'].isin(cases_list2)]
             cnt=len(df_mongo_ans)
             
             y = {df_mongo_ans['id'].values[i]:[" ".join(df_mongo_ans['judgment'].values[i].split(" ")[0:200])] for i in range(cnt)}
             
            
             
             score_dict={df_mongo_ans['id'].values[i]:df_mongo_ans['judgment'].values[i].count(xquery) for i in range(cnt)}
             
         
             vector_ids={i:[f"{i},{xquery}"] for i in cases_list2} or None
             
             print("The cases are from mongo")
             print(y)
         
            
         
         df2=df[df['id'].isin(cases_list2)].drop_duplicates(subset=['id']).reset_index(drop=True)
         
         x_main=dict(zip(df2['id'].values,
                    df2[['court','Date2','result','book','title','case_year','judges','citation','appeal']].values.tolist()))      
          
         
         date_dict=dict(zip(df2['id'].values,
                    df2['Date2'].values.tolist()))      
          
         
         return json.dumps({'data':y,'scores':score_dict,'vector_ids':vector_ids,'date':date_dict,'lookup':x_main})
     else:
         return json.dumps({'data':"E1"})
     
     
@app.route("/t4_describe",methods=["GET",'POST'])
def test_api4():
    
    if request.json['flag']==False:
        vector_ids=request.json['vector_ids']
       
        case_id=vector_ids[0].split(',')[0]
        hits = helpers.scan(
            es,
            query={"query":{ "ids":{ "values": vector_ids } } },
            #scroll='1m',
            index='test'
        )
            
        source = [hit['_source'] for hit in hits]
        vectors_text = [s['text'] for s in source]
        
        main_case=get_display_case(ids=[case_id])
        
        result_dict={main_case['id']:[cl_text(main_case['judgment']),vectors_text]}
        
        return json.dumps({'data':result_dict})
    
    else:
        
        vector_ids = request.json['vector_ids']
        case_id = vector_ids[0].split(',')[0]
        exact_query = vector_ids[0].split(',')[1]
        main_case = get_display_case(ids=[case_id])
        
        print("The mongo cases is: ,", main_case['id'])
        
        print("The mongo exact query is is: ,", exact_query)
        
        result_dict={main_case['id']:[cl_text(main_case['judgment']),[exact_query]]}
        
        return json.dumps({'data':result_dict})             


@app.route("/validate_info",methods=['POST','GET'])
def validate_info():
    
    df_user = pd.DataFrame(list(user_collection.find({})))
    x_field=request.json['field']
    x_val=request.json['val']
    
    all_val = df_user[x_field].unique().tolist()
    
    print(f"column name : {x_field}")
    print(f"val: {x_val}")
    print(all_val)
    if x_val in all_val:
        return json.dumps({'response':'no'})
    
    else:
        return json.dumps({'response':'yes'})
    
    return json.dumps("error")


@app.route("/validate_user",methods=['POST','GET'])
def validate_user():
    
    df_user = pd.DataFrame(list(user_collection.find({})))
    
    user_name=request.json['user_name']
    user_password=request.json['user_password']
    
    all_creditentials=df_user[['user_name','user_password']].apply(tuple,axis=1).to_list()
    
    
    print(f"The user is {user_name} and {user_password}" )
    
    if (user_name,user_password) in all_creditentials:
        return json.dumps({"response":"yes",'user':'yes','password':'yes','id':user_name})
    
    
    if (user_name not in list(df_user['user_name'].unique())) and (user_password not in (list(df_user['user_password'].unique()))):
        return json.dumps({'response':'no','user':'no','password':'no'})
    
    if (user_name in list(df_user['user_name'].unique())) and (user_password not in (list(df_user['user_password'].unique()))):
        return json.dumps({'response':'no','user':'yes','password':'no'})
    
    
    if (user_name not in list(df_user['user_name'].unique())) and (user_password in (list(df_user['user_password'].unique()))):
        return json.dumps({'response':'no','user':'no','password':'yes'})
    
    
    return json.dumps({'response':'error'})


@app.route("/user_track",methods=['POST','GET'])
def user_track():
    
    print(list(request.json.keys()))
    
    keys = list(request.json.keys())
    
    user= request.json['user'] if "user" in keys else None
    
    date = request.json['date'] if "date" in keys else None
    
    user_input = request.json['user_input'] if "user_input" in keys else None
    
    user_hit_endpoint = request.json['api_hit'] if "api_hit" in keys else None
    
    context = request.json['context'] if "context" in keys else None
    
    response_output = request.json['output'] if "usoutputer" in keys else None
    
    
    mongo_upload_dict={
                    'date':date,
                    'user':user,
                    'user_hitendpoint':user_hit_endpoint,
                    'user_input':user_input,
                    'context':context,
                    'response_output':response_output
                        }
    
    try:
        logs_collection.insert_one(mongo_upload_dict)
        print("Successfully place data")
        return json.dumps({'response':'yes'})
    
    except:
        
        return json.dumps({'response':'no'})
        


    


  

if __name__ == "__main__":
    app.run(debug=True,port = 1270)


