from dash.exceptions import PreventUpdate
from dash import Dash,dcc, html, Input, Output, callback,dash_table, no_update,register_page,State,ctx, clientside_callback, ALL,MATCH,exceptions
import ast
import requests as req
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import time
import PyPDF2
import openai
from textwrap import dedent
import re
import json
import config

register_page(
    __name__,
    name='Query',
    top_nav=True,
    path='/query'
)



openai.api_key = config.apiKey

errorLoggerAPI = "https://legalanalysis.ai-iscp.com/t5_error"

def priority(t):
        
    courts_kar = ["KARACHI-HIGH-COURT-SINDH", "Sindh High Court"]
    courts_fd = ["Supreme Court of Pakistan"]
    if t in courts_fd:
        return 1
    elif t in courts_kar:
        return 2
    else:
        return 3 


controls = dbc.InputGroup(
    children=[
        dbc.Input(
            id="user-input",
            placeholder="what would you like to analyse today?",
            type="text",
            autocomplete='off',
            # size="sm",
            style={
                'font-size': '1.5em',
                'border-top-left-radius': '15px',
                'border-bottom-left-radius': '15px'
                }),
        dmc.ActionIcon(
            DashIconify(icon="tabler:send", width=20),
            size="lg",
            variant="filled",
            id="finanal",
            n_clicks=0,
            style={
                'background-color':'#2A9296',
                'border-color': 'white',
                'border-top-right-radius': '15px',
                'border-bottom-right-radius': '15px',
                'height':'44pt',
                'width':'50pt'
                },
        ),
        
    ]
)


items = dbc.ListGroup(

    id='selCon',
    flush=True,
    style={'overflowX': 'auto','padding':'0px'}
),


analysisRow = dbc.Row([
    dbc.Card([
            dbc.Row([
                
                dbc.Col([
                    html.H5('Relevant cases',style={'display': 'flex',    'flex-direction': 'row',    'justify-content': 'center'}),
                    dbc.ListGroup(
                        id='selCon',
                        flush=True,
                        horizontal=False,
                        style={'overflowX': 'auto','padding':'0px','max-height':'95%'}
                    ),                    
                ],xs=12,sm=12,md=12,lg=2,style={'padding-right': '0px', 'padding-bottom': '10px','max-height':'73vh'},id='relCasesCol'),
                dbc.Col(id='divider',children = dmc.Divider(orientation="vertical", style={"height": "95%"}),style={"width":'25px'},xs=12,sm=12,md=12,lg=1),
                
                dbc.Col([
                    dbc.Row([
                        dbc.Col(
                            # "hello",
                            html.H5("Analysis",style={'padding-left':'16px'}),
                            id='Title'
                            
                        ),
                        dbc.Col([
                            dmc.Group([
                                dmc.ActionIcon(
                                    DashIconify(icon="ic:twotone-clear", width=25),
                                    size="md",
                                    variant="filled",
                                    id="clear",
                                    n_clicks=0,
                                    radius = 'lg',
                                    color='violet'
                                    # mb=10,
                                    
                                ),
                                dmc.ActionIcon(
                                    DashIconify(icon="ic:round-question-mark", width=25),
                                    size="md",
                                    variant="filled",
                                    id="action-icon",
                                    n_clicks=0,
                                    radius = 'lg',
                                    color='violet'
                                    # mb=10,
                                    
                                ),
                                html.A(
                                    dmc.ActionIcon(
                                        DashIconify(icon="lucide:mail", width=18),
                                        size="md",
                                        variant="filled",
                                        id="email",
                                        n_clicks=0,
                                        radius = 'lg',
                                        color='violet'
                                        # mb=10,
                                        
                                    ),href='mailto:info@theaisystems.com')
                            ]),
                        ],
                            style={
                                'display': 'flex',
                                'flex-direction': 'row',
                                'justify-content': 'flex-end'
                            }
                        )
                    ]),
                    dbc.Row([
                        dbc.Spinner(
                            dbc.Textarea(id='finAnalysis',readonly = True,draggable =False,style ={'height':'70vh','overflowY': 'auto','padding-left':'0px',"border":'0px',"resize": "none","font-size":"16px"})   
                            #value=aoc,
                        )
                    ])]
                    ,style={'padding-left':'0px','padding-bottom':'15px'}
                )
            ]),
            dbc.Row([
                controls
            ]),
        ],style={'padding':'15px 15px 5px 15px','max-height':'Auto',"overflowY":'auto','margin-bottom':'0px'})
],style={'margin':'10px 20px 0px 20px',})

tick = dmc.ActionIcon(DashIconify(icon="lucide:check", width=16),size="sm",variant="filled",n_clicks=0,radius = 'lg',color='green')
cross = dmc.ActionIcon(DashIconify(icon="entypo:cross", width=16),size="sm",variant="filled",n_clicks=0,radius = 'lg',color='red')

alert = dmc.Alert(
    "Something happened! You made a mistake and there is no going back, your data was lost forever!",
    title="Simple Alert!",
    id='Alert',
    color="red",
    withCloseButton=True,
    hide=True,
    variant='filled',
    style={
        'position':'absolute',
        'right':"10px",
        'top':'7vh'
        }
    
)


casemodal = dmc.Modal(id="modal1", size="75%",style={'height':'95%','overflowY':'auto'}, zIndex=10000,centered=True,overlayBlur=25 ),

def layout():
    return html.Div(
        dbc.Container([

            analysisRow,
            alert,

            dmc.Modal(
                dbc.Row([
                    html.H5("Hi, i am a specialised Framework developed to answer only queries regarding the caselaws present in my knowledge"),
                    dmc.Space(h=15),
                    dbc.Col([
                        tick,
                        dmc.Space(w=6),
                        html.H4("Here are some examples of what I can answer:",style={'margin-bottom':'0px'})
                    ],style={'display':'flex','flex-direction': 'row','align-items': 'center'}),
                    dmc.Space(h=15),
                    html.P("Can someone who is not the legal owner of a property, but has rented it out and seeks eviction through court, succeed in the eviction process if the tenant disputes the tenancy based on the landlord's lack of ownership?"),
                    html.P("Can a landlord commence ejectment proceedings solely based on rent arrears if the tenant is paying the current rent?"),
                    dbc.Col([
                        cross,
                        dmc.Space(w=6),
                        html.H4("Here are some examples of what I can NOT answer:",style={'margin-bottom':'0px'})
                    ],style={'display':'flex','flex-direction': 'row','align-items': 'center'}),
                    dmc.Space(h=15),
                    html.P("what is the climate in the Amazon Rainforest?"),
                    html.P("Which school has the best principal?")
                ]),
                id="info",
                size="75%",
                style={'height':'95%','overflowY':'auto'},
                zIndex=10000,
                centered=True,
                overlayBlur=25 ),
            dmc.Modal(id="modal1", size="75%",style={'height':'95%','overflowY':'auto'}, zIndex=10000,centered=True,overlayBlur=25 ),
            dcc.Store(id='vids',storage_type='session'),
            dcc.Store(id='count',storage_type='session'),
        ],style = {'padding':'0px'},fluid=True)
    )

@callback(
    Output('url','pathname'),
    Input("url",'pathname'),
    State("loggedin","data"),
)
def checkcred(url,data):
    if url=='/query' and data is None:
        return "/"
    else:
        return no_update
    
@callback(
    Output('divider',"children"),
    Output('divider',"style"),
    Output('selCon',"horizontal"),
    Input("url",'pathname'),
    State('screen','data'),

)
def checkscreen(url,screen):
    if url =='/query':
        sc = json.loads(screen)
        # print(sc)
        if sc['width']<992:
            return dmc.Divider(variant="solid",style={'padding-bottom':'10px'}),None,False
        else:
            return no_update,no_update,no_update
    else:
        no_update





@callback(
    Output('url','pathname',allow_duplicate=True),
    Output("loggedin","data",allow_duplicate=True),
    Input("logout",'n_clicks'),
    State("loggedin","data"),
    prevent_initial_call=True
)
def checkcred(but,data):
    if but is not None and data is not None:
        return "/",None
    else:
        return no_update,no_update


@callback(
    Output("vids","data"),
    Output("count","data"),
    Output("finAnalysis","value"),
    Output('selCon',"children"),

    Output("Alert","title"),
    Output('Alert',"children"),
    Output('Alert',"hide"),
    [Input("finanal","n_clicks")],
    [Input('user-input', 'n_submit')],
    [State("user-input","value"),
    State("Alert","hide")],
    prevent_initial_call=True
)
def analysis(click, n_submit, query,ope):
    if click is not None or n_submit > 0:
        # print(query)
        try:
            resp2=json.loads(
                req.post(
                    "https://legalanalysis.ai-iscp.com/t3",
                    json = {
                        "SearchQuery":f"""{query}""",
                        "book":[],
                        "court":[],
                        "judges":[],
                        "flag":0,
                        "law":[],
                        "ws":"",
                        "fcase":[],
                        "startDate":'1900-1-1',
                        "endDate":'2023-12-31',
                    }
                ).text
            )
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            req.post(
                errorLoggerAPI,
                json = {
                    "SearchQuery":f"""{query}""",
                    "Reason":"no response from API server",
                    'TechnicalError':message
                }
            )
            print(f"Error:{query} RRRREASON: No Response from API Server")

            return no_update,no_update, "" ,[],"Server Error", "The server is currently unreachable please try again later.", not ope

        try:
            if resp2['data'] != 'E0':
                resp_fin_list = []
                
                for u, l in resp2['lookup'].items():
                    # print(l)
                    resp_fin = {}
                    
                    resp_fin['id'] = u
                    resp_fin['court'] = l[0]
                    resp_fin['data'] = resp2['data'][u]
                    if l[-2] == 'N/A':
                        resp_fin['cite'] = l[4] + " (" + l[-1] + ")"
                    else:
                        resp_fin['cite'] = l[4] + " (" + l[-2] + ")"
                    resp_fin['date'] = l[1]
                    resp_fin['score'] = resp2['scores'][u]
                    resp_fin_list.append(resp_fin)
                        
                new = pd.DataFrame(resp_fin_list)
                new['date'] = pd.to_datetime(new['date'], format='%Y-%m-%d',errors='coerce')            
                new['priority'] = new['court'].apply(lambda x: priority(x))

                new = new.sort_values(by=['priority','date'],ascending=[True,False])
                new_final = new.head(5)
                new_final['cite'] = new_final['cite'].apply(lambda x:x.replace('\n',''))

                
                text = f"given the query:  {query} answer the query using the context below with name of case and court that I will provide. if you cant find the answer in the context then apologise and ask for more infomration or say i dont know. do not make things up and try to look only at the explicit meaning."

                text2 = ""

                for _, row in new_final.iterrows():
                    for r in row['data']:
                        t = "In " + row['cite'] +"of" + row['court'] + " the relevant text is " + r + "\n\n"
                        text2 += t

                text4 =f"""{text}
                
                {text2}
                
                if you believe the answer is in the context above then give me a detailed analysis of how the above context supports the answer to the query given and include all citation with case names where possible and do not change the citation only write the citation name as given to you for example if the citation given is "(MUHAMMAD) ALI TAUQIR VS RAFIQ AHMAD (1999 CLC 795)" then write the citation as "(MUHAMMAD) ALI TAUQIR VS RAFIQ AHMAD (1999 CLC 795)".

                """
                try:
                    completion = openai.ChatCompletion.create( 
                        model="gpt-3.5-turbo-1106", 
                        temperature=0.0, 

                        messages=[ 

                            {"role": "user", "content": text4}, 

                        ] 
                    ) 
                except:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(e).__name__, e.args)
                    req.post(
                        errorLoggerAPI,
                        json = {
                            "SearchQuery":f"""{query}""",
                            "Reason":"OpenAi Error",
                            'TechnicalError':message
                        }
                    )
                    return no_update,no_update, "" ,[],"Server Overload", "Our Servers are currently Overloaded, please try again later.", not ope

                    
                ans = completion.choices[0].message.content

                relCases = new_final[new_final.index.isin([i for i in new_final.index if new_final.loc[i,'cite'][:20] in ans])].reset_index(drop=True)
                
                metaRel = {}
                for x in range(0,len(relCases)):
                    metaRel[relCases.at[x,'id']] = {'cite':relCases.at[x,'cite'],'vids':resp2['vector_ids'].get(relCases.at[x,'id'])}
                
                return metaRel, 0, ans, [dbc.ListGroupItem(f"{relCases['cite'][x].capitalize()}",id={"type": "list-group-item", "index": relCases['id'][x]},action = True) for x in relCases.index],"", "",  ope

            else:
                text= f"""
                    I'm sorry, but i could not find an answer to your question '{query}' as i am a specialised Framework developed to answer only queries regarding the caselaws present in my knowledge. Please try changing or clarifying your query or click on the info icon for more information.
                """
                return no_update,no_update,  text ,[],"", "",  ope

            
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            req.post(
                errorLoggerAPI,
                json = {
                    "SearchQuery":f"""{query}""",
                    "Reason":"Error in frontend Callback",
                    'TechnicalError':message
                }
            )
            return no_update,no_update, "" ,[],"Response Error", "There was an error crafting your response please try changing your query.", not ope



@callback(
    Output("vids","data",allow_duplicate=True),
    Output("count","data",allow_duplicate=True),
    Output("finAnalysis","value",allow_duplicate=True),
    Output('user-input', 'value'),
    Output('selCon',"children",allow_duplicate=True),
    [Input("clear","n_clicks")],
    prevent_initial_call=True
)
def analysis(but):
    if but is not None:
        return {},None,"","",[]
    else:
        return no_update,no_update,no_update,no_update,no_update

@callback(
    Output("modal1","opened"),
    Output('modal1',"children"),
    Output('modal1',"title"),
    Output("count","data",allow_duplicate=True),
    Input({'type': 'list-group-item', 'index': ALL}, 'n_clicks'),
    State("modal1","opened"),
    State("vids","data"),
    State("count","data"),
    prevent_initial_call=True
)
def moda(rlc,op,Wmeta,countclicks):

    

    if len(rlc)>0:
        if countclicks==1:
            id = ctx.triggered_id['index']

            ind = Wmeta.get(id)['vids']
            id = id.replace("%20"," ")
            data = json.loads(req.post("https://legalanalysis.ai-iscp.com/t4_describe",json = {"vector_ids":ind,'flag':0}).text)
            hl = data['data'][id][1]
            

            
            sequences = dmc.Highlight(
                f"""{data['data'][id][0]}""", 
                highlight=hl
                )  
            
            return not(op),sequences,Wmeta.get(id)['cite'],no_update
        elif countclicks==0:

            return op,{},[],countclicks+1
    else:
        no_update
@callback(
    Output("info","opened"),
    Input("action-icon","n_clicks"),
    State("info","opened"),
    prevent_initial_call=True
)
def helpmodal(cli,op):
    return not op

