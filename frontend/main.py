from dash.exceptions import PreventUpdate
from dash import Dash,dcc, html, Input, Output, callback,dash_table, no_update,register_page,State,ctx, clientside_callback, ALL,MATCH,exceptions
import dash
import requests as req
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import openai
from textwrap import dedent
import config

app  = Dash(
    __name__,
    use_pages=True,
    pages_folder="suppCodes",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.ZEPHYR,dbc.icons.BOOTSTRAP],
    update_title=None,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)
server = app.server
app.title = "RAG"


navbar1 =    dbc.Navbar(
        [
                dbc.Col([
                        dmc.Space(w=20),
                        html.Img(src=app.get_asset_url('miniLogoBg.png'),style={'height' : '6vh'}),
                        dmc.Space(w=15),
                        html.H3("Legal Assistant",style={"margin":'0px',"display":"flex","flex-direction":"column","justify-content":"center",'color':'white'}),
                ],style={'display':'flex'},sm=10,md=10,lg=10),
                dbc.Col(
                    [
                    html.A(html.P("AI Systems",style={'margin':'0px','color':"white"}),href="https://theaisystems.com/",target="_blank")
                ]   ,id='avatar'
                    ,style={
                        'display': 'flex',
                        'flex-direction': 'row',
                        'justify-content': 'center'
                    },
                    xs=2,sm=2,md=2,lg=2
                ),
        ],
        color = '#2A9296',
        style={
            'height':"6vh",
            'padding':'0px'
        }
    )

app.layout =dmc.NotificationsProvider(
    [
        # navbar,
        navbar1,
        dash.page_container,
        dcc.Location(id='url', refresh=True),
        dcc.Store(id='loggedin',storage_type='session'),
        dcc.Store(id='screen',storage_type='session'),
    ]
)
app.clientside_callback(
    """
    function(href) {
        console.log(window.innerWidth);
        var w = window.innerWidth;
        var h = window.innerHeight;
        console.log(h);
        return JSON.stringify({'height': h, 'width': w});
    }
    """,
    Output('screen', 'data'),
    Input('url', 'href')
)

@callback(
    Output('avatar','children'),
    Input("url","pathname"),
    State('loggedin','data')
)
def ava(ur,user):
    # print(ur)
    if ur=='/query':
        return  dmc.Menu(
        [
            dmc.MenuTarget( 
                dmc.Avatar(
                    # f"{user[0]}",
                    radius="xl",
                    style={
                        'height':'5vh',
                        'width':'5vh',
                    }
                ),
            ),
            dmc.MenuDropdown(
                [
                    dmc.MenuLabel(f"Hello, {user}"),
                    dmc.MenuItem("Logout", icon=DashIconify(icon="ic:twotone-logout"),id='logout'),
                    dmc.MenuItem("Contact Us", icon=DashIconify(icon="ic:twotone-email"),href='mailto:info@theaisystems.com'),
                    dmc.MenuDivider(),
                    dmc.MenuItem(
                        "AI Systems",
                        href="https://theaisystems.com/",
                        target="_blank",
                        icon=DashIconify(icon="radix-icons:external-link"),
                        color="Green"
                    ),
                ],
            ),
        ],
        trigger="click",
    )
    else:
        return no_update
    # return no_update


if __name__ == '__main__':
    app.run_server(debug=False,port=config.port,host = "0.0.0.0") 
    
