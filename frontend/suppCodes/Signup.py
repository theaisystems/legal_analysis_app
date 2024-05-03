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
from dash import Dash,dcc, html, Input, Output, callback,dash_table, no_update,register_page,State,ctx,ALL, MATCH
import re

register_page(
    __name__,
    name='Signup',
    top_nav=True,
    path='/su'
)

mainpage = dbc.Card([
    dmc.Grid([
        dmc.Col(
            dmc.TextInput(
                label="Username",
                id='Suser',
                style={'padding':'0px'},
                size='md',
                placeholder="Enter Your Username Here",
                icon=DashIconify(icon="ic:outline-alternate-email"),
                required=True,
                debounce=2000
            ),span=4
        ),
        dmc.Col(
            dmc.TextInput(
                label="Email",
                id='Semail',
                style={'padding':'0px'},
                size='md',
                placeholder="Enter Your email Here",
                icon=DashIconify(icon="ic:outline-email"),
                required=True,
                debounce=2000
            ),span=8
        ),
        dmc.Col(
            dmc.TextInput(
                label="Contact No.",
                id='Spno',
                style={'padding':'0px'},
                size='md',
                placeholder="+92 333 1234567",
                icon=DashIconify(icon="ic:outline-phone-iphone"),
                required=True,
                debounce=2000
            ),span=6
        ),
        dmc.Col(
            dmc.TextInput(
                label="Occupation",
                id='Soccu',
                style={'padding':'0px'},
                size='md',
                placeholder="Enter Your Occupation Here",
                icon=DashIconify(icon="ic:outline-work-outline"),
                debounce=2000
            ),span=6
        ),
        dmc.Col(
            dmc.PasswordInput(
                label="Password",
                id='Spass1',
                style={'padding':'0px'},
                size='md',
                placeholder="Set your password",
                icon=DashIconify(icon="bi:shield-lock"),
                required=True,
                debounce=2000
            ),span=6
        ),
        dmc.Col(
            dmc.PasswordInput(
                label="Re-enter Password",
                id='Spass2',
                style={'padding':'0px'},
                size='md',
                placeholder="Re-enter your password",
                icon=DashIconify(icon="bi:shield-lock"),
                required=True,
                debounce=2000
            ),span=6
        ),
    ],grow=True,gutter='md')
],style={'padding':'15px'})


signupAlert = dmc.Alert(
    "Something happened! You made a mistake and there is no going back, your data was lost forever!",
    title="Simple Alert!",
    id='signupAlert',
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
            mainpage,
            signupAlert
        ],style = {'padding':'40px 40px',"height": "100vh"},fluid=True)
        )


@callback(
    Output('Suser',"error"),
    Output('Semail',"error"),
    Output('Spno',"error"),
    Output('Spass1','error'),
    Output('Spass2','error'),
    Input('Suser','value'),
    Input('Semail','value'),
    Input('Spno','value'),
    Input('Spass1','value'),
    Input('Spass2','value'),
    prevent_initial_call=True  
)
def checkfields(user,email,pno,pas,repass):
    print(ctx.triggered_id)
    
    if ctx.triggered_id == 'Suser':
        # print(user)
        testlist = [x for x in ["/","!","-","*","+"] if x in user]
        if len(testlist)>0:
            return f"User cannot contain the characters : {str(testlist)[1:-1]}",no_update,no_update,no_update,no_update
            print(testlist)
        resp = json.loads(
            req.post(
                "http://192.168.1.10:1271/validate_info",
                json = {
                    "field":'user_name',
                    "val":user,
                }
            ).text
        )
        if resp['response']=='no':
            return f"This Username is already taken",no_update,no_update,no_update,no_update
        else: return False,no_update,no_update,no_update,no_update
    
    if ctx.triggered_id == 'Spno':
        pattern =r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
        if re.fullmatch(pattern, pno) is None:
            return no_update,no_update,"Please Enter a valid Phone number",no_update,no_update

        resp = json.loads(
            req.post(
                "http://192.168.1.10:1271/validate_info",
                json = {
                    "field":'phone_no',
                    "val":pno,
                }
            ).text
        )
        if resp['response']=='no':
            return no_update,no_update,"An account with this Number already exists",no_update,no_update
        else:
            return no_update,no_update,False,no_update,no_update
        
    if ctx.triggered_id == 'Semail':
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        if re.fullmatch(regex, email) is None:
            return no_update,f"Please Enter a valid email",no_update,no_update,no_update

        resp = json.loads(
            req.post(
                "http://192.168.1.10:1271/validate_info",
                json = {
                    "field":'email',
                    "val":email,
                }
            ).text
        )
        if resp['response']=='no':
            return no_update,"An account with this email already exists",no_update,no_update,no_update
        else:
            return no_update,False,no_update,no_update,no_update
    
    if ctx.triggered_id == 'Spass2':
        
        if repass !=pas:
            return no_update,no_update,no_update,no_update,"Passwords do not match"
        else: return no_update,no_update,no_update,no_update,False
    
    return no_update,no_update,no_update,no_update,no_update
        
    
# @callback(
#     Input('Suser',"error"),
#     Input('Semail',"error"),
#     Input('Spno',"error"),
#     Input('Spass1','error'),
#     Input('Spass2','error'),
# )
# @callback(
#     Output('url','pathname'),
#     Output("loginAlert","title"),
#     Output('loginAlert',"children"),
#     Output('loginAlert',"hide"),
#     Output('email','error'),
#     Output('pass','error'),
#     Input('login','n_clicks'),
#     State('email','value'),
#     State('pass','value'),
#     State("loginAlert","hide"),
#     prevent_initial_call=True
# )
# def redir(but,st,pas,aler):

#     return ()
