import numpy as np
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import requests as req
import pandas as pd
import time
# import requests as re
import json
import ast
from datetime import date,datetime,timedelta
from dash_iconify import DashIconify
from dash.exceptions import PreventUpdate
from dash import Dash,dcc, html, Input, Output, callback,dash_table, no_update,register_page,State,ctx,ALL, MATCH,clientside_callback
import dash

register_page(
    __name__,
    name='Login',
    top_nav=True,
    path='/'
)



mainpage1 = dmc.Grid(
    dmc.Col(
        dbc.Card([
            dbc.Col([
                dbc.Row([
                    dmc.TextInput(
                        label="Username",
                        id='email',
                        # style={"width": 300,'padding':'0px'},
                        size='lg',
                        placeholder="Your Username",
                        icon=DashIconify(icon="ic:round-alternate-email"),
                    ),
                ],align="center",justify="center"),
                dmc.Space(h=18),
                dbc.Row([
                    dmc.PasswordInput(
                        label="Password",
                        id='pass',
                        # style={"width": 300,'padding':'0px'},
                        size='lg',
                        placeholder="Your password",
                        icon=DashIconify(icon="bi:shield-lock"),
                    )
                ],align="center",justify="center"),
                dbc.Row([
                    dmc.Button(
                    "Login",
                    id = 'login',
                    disabled=False,
                    leftIcon=DashIconify(icon="carbon:login"),
                    size='md',
                    radius='md',
                    style={'background-color':'#2A9296','border-color': 'white'},
                ),
                ],align="center",justify="center",style={'padding':'20px 12px 0px 12px',}),
                dmc.Space(h=9),
                dbc.Row([
                    dmc.Button(
                    "Sign Up",
                    id = 'signup',
                    disabled=True,
                    leftIcon=DashIconify(icon="oui:ml-create-single-metric-job"),
                    size='md',
                    radius='md',
                    style={'background-color':'#2A9296','border-color': 'white'},
                ),
                ],align="center",justify="center",style={'padding':'0px 12px'}),
                
            ],style={"padding":"18px 10px"})
        ]),
        xl=3,
        lg=4,
        md=6,
        sm=8,
        xs=10
    ),
    justify="center",
    align="center",
    gutter="xl",
    style={
        'height':"94vh"
    }
)


alertLogin = dmc.Alert(
    "Something happened! You made a mistake and there is no going back, your data was lost forever!",
    title="Simple Alert!",
    id='loginAlert',
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

def layout():
    return html.Div(
        dbc.Container([
            # navbar,
            mainpage1,
            alertLogin
        ],style = {'padding':'0px 40px',"height": "94vh"},fluid=True)
        )


clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return true
    }
    """,
    Output("login", "loading"),
    Input("login", "n_clicks"),
    prevent_initial_call=True,
)   
@callback(
    Output('url','pathname',allow_duplicate=True),
    Output("loginAlert","title"),
    Output('loginAlert',"children"),
    Output('loginAlert',"hide"),
    Output('email','error'),
    Output('pass','error'),
    Output('loggedin','data'),
    Output("login", "loading",allow_duplicate=True),
    Input('login','n_clicks'),
    State('email','value'),
    State('pass','value'),
    State("loginAlert","hide"),
    prevent_initial_call=True
)
def redir(but,st,pas,aler):
    if but is not None:

        if st is None or st == "" or pas is None or pas =='':
        
            ret = [no_update,"","",aler]
            if st is None or st == "":
                ret+=["Please enter a valid user"]
            else:
                ret+=[False]
                
            if pas is None or pas == "":
                ret+=["Please enter a valid password"]
            else:
                ret+=[False]
                
            print(ret)
            ret+=[no_update,False]
            return ret
        elif (st is not None or st != "") and (pas is not None or pas != ""):
            # print('imhere')
            resp=json.loads(
                req.post(
                    "https://legalanalysis.ai-iscp.com/validate_user",
                    
                    json = {
                        "user_name":st,
                        "user_password":pas
                    }).text)
            print(resp)
            if resp['response']=='error':
                return no_update,"Server Error","An internal error occured please try again later",not(aler),False,False,no_update,False
            elif resp['user']=='yes' and resp['password']=='yes':
                return '/query',"","",aler,False,False,st,False
            elif resp['user']=='no' and resp['password']=='no':
                return no_update,"","",aler,"Please enter a valid user","Please enter a valid password",no_update,False
            elif resp['user']=='yes' and resp['password']=='no':
                return no_update,"","",aler,False,"Please enter a valid password",no_update,False
            elif resp['user']=='no' and resp['password']=='yes':
                return no_update,"","",aler,"Please enter a valid email",False,no_update,False
            else:
                return no_update,"Unkown Error","Please try again later",not(aler),False,False,no_update,False
        
    else:
        return no_update,"","",aler,False,False,no_update,False