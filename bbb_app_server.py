# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objs as go

import pickle
import predict_price
import recommend_bike

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
app = dash.Dash()
app.css.append_css({"external_url":"https://codepen.io/chriddyp/pen/bWLwgP.css"})
server = app.server

# prepare data
# used for map access
mapbox_access_token = 'pk.eyJ1IjoiampqeHh4IiwiYSI6ImNqcnliNWI0MDB3NmQ0OW5tN3B4Y29ibXUifQ.rhzR_Hhv0MwY9xsWInG07A'

with open('input_dict.pickle', 'rb') as handle:
    input_dict2 = pickle.load(handle)
input_options = input_dict2
input_options.update({'year': [str(i) for i in range(2019, 1979,-1)]})

pick_df = pd.read_pickle('df_pick.pickle')
pick_list = [ str(i)+': ' + pick_df.loc[i].title for i in pick_df.index]

theme_blue = '#2A99D7'

app.layout = html.Div([
#    html.Div(children = [html.Img(src = "https://i.ibb.co/JnqrxnW/bluebike-title.png", alt = "Bike Blue Book",
#                                  style = {'display':'block', 'margin-left': 'auto', 'margin-right':'auto'})],
#            style = {'borderBottom': 'thin lightgrey solid', 
#                'backgroundColor':'#292C32',
#                'padding': '10px 5px'}),
    
    html.Div(children = [html.Img(src = "https://i.ibb.co/b7ZBjhT/bbb-title.png", alt = "Bike Blue Book",
                                  width = '1000', height = '245',
                                  style = {'display':'block', 'margin-left': 'auto', 'margin-right':'auto'})],
            #style = {'borderBottom': 'thin lightgrey solid'}
            ),    
    html.Br(),  
    html.Ul(children = [html.Li(html.Strong('Price Your Bike', style = {'font-size': '150%'}))]),
    dcc.Textarea(id = 'desp',placeholder = 'Please enter your bicycle specs and description here or specify configurations below', rows = "4",cols = "80", 
                  style = {'display': 'block', 'margin-left': 'auto', 'margin-right':'auto', 'height': '76'} ),
    html.Div(className = 'row', children = [
        html.Div([
            html.Label(children = 'manufacturer', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'make',
                options = [{'label': i, 'value': i} for i in input_options['makemanufacturer']],
                value = 'trek'),
            html.Label('bicycle type', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'bikeType',
                options = [{'label': i, 'value': i} for i in input_options['bicycletype']],
                value = 'road'),
            html.Label('brake type', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'brakeType',
                options = [{'label': i, 'value': i} for i in input_options['braketype']],
                value = 'unknown'),
            html.Label('model name', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'modelname',
                options = [{'label': i, 'value': i} for i in input_options['modelnamenumber']],
                value = 'unknown'),
        ], className = 'four columns'),
        
        html.Div([
            html.Label('handlebar type', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'handleType',
                options = [{'label': i, 'value': i} for i in input_options['handlebartype']],
                value = 'drop'),
            html.Label('suspension', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'suspension',
                options = [{'label': i, 'value': i} for i in input_options['suspension']],
                value = 'unknown'),
            html.Label('electric-assist', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'elecAss',
                options = [{'label': i, 'value': i} for i in input_options['electricassist']],
                value = input_options['electricassist'][0]),
            html.Label('frame size', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'framesize',
                options = [{'label': i, 'value': i} for i in input_options['framesize']],
                value = input_options['framesize'][0]),
        ], className = 'four columns'),
        
        html.Div([
            html.Label('wheel size', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'wheelsize',
                options = [{'label': i, 'value': i} for i in input_options['wheelsize']],
                value = input_options['wheelsize'][0]),
            html.Label('condition', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'condition',
                options = [{'label': i, 'value': i} for i in input_options['condition']],
                value = 'good'),
            html.Label('year', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'year',
                options = [{'label': i, 'value': i} for i in input_options['year']],
                value = '2016'),
            html.Label('material', style = {'color': theme_blue}),
            dcc.Dropdown( id = 'material',
                options = [{'label': i, 'value': i} for i in input_options['material']],
                value = 'unknown'),
        ], className = 'four columns'),
    ]),
    html.Br(),
    dcc.Checklist( id = 'check-list',
        options=[
            {'label': 'Ultegra', 'value': 'ultegra'},
            {'label': 'Sram', 'value': 'sram'},
            {'label': 'Low mileage', 'value': 'miles'},
            {'label': 'Fox', 'value': 'fox'}],
        values=[],
        labelStyle={'display': 'inline-block'},
        inputStyle={"margin-left": "70px"},
        style = {'width':'60%', 'margin-left': 'auto', 'margin-right': 'auto'}),
    
    html.Br(), 
    html.Div(id = 'output-price', style = {'font-size': '30px', 'font-weight': 'bold', 'color':theme_blue,
                                           'textAlign':'center'}),
    html.Br(),        
    html.Button(id = 'submit-button', n_clicks = 0, children = 'Get Price!', 
                style = {'background-color':theme_blue, 'color': 'white',
                #style = {'color': theme_blue,         
                         'display':'block', 'margin-left': 'auto', 'margin-right':'auto',
                         'font-size': '18px'}),

    html.Hr(),
    html.Ul(children = [html.Li(html.Strong('Pick Your Bike', style = {'font-size': '150%'}))]),
    html.Label('I like this bike:'),
    dcc.Textarea(id = 'url', placeholder = 'Please paste the craigslist URL of the bicycle you like here', rows = "1",cols = "80",
                  style = {'display': 'block', 'margin-left': 'auto', 'margin-right':'auto'} ),
    html.Label('Demo: '),
    dcc.Dropdown(id = 'pick-list',
                options = [{'label': i, 'value': i} for i in pick_list],
                value = pick_list[0]),
    html.Br(),
    html.Button(id = 'submit-button-2', n_clicks = 0, children = 'Get recommendation!', 
                style = {'background-color':theme_blue, 'color': 'white',
                         'display':'block', 'margin-left': 'auto', 'margin-right':'auto',
                         'font-size': '18px'}),

    html.Div(id = 'output-img')    
    
], style = { 'max-width': '1000px', 'margin':'auto'})

#'backgroundColor': '#f2f2f2',    
@app.callback(Output('output-price', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('condition', 'value'),State('year', 'value'),State('bikeType', 'value'),State('make', 'value'),
               State('modelname', 'value'),State('wheelsize', 'value'),State('framesize', 'value'),State('material', 'value'),
               State('brakeType', 'value'),State('suspension', 'value'),State('elecAss', 'value'),State('handleType', 'value'),
               State('check-list', 'values'),State('desp', 'value')
              ])

def update_price(n_clicks, cond, yr, bike_type, make, model, wz, fz, material, brake_type, susp, elec, handle_type, checklist,desp):
    if n_clicks == 0:
        return ""
    else:
        #price = max(50,input_options['condition'].index(cond)*150)  
        price = predict_price.predict_price(cond, yr, bike_type, make, model, wz, fz, material, brake_type, susp, elec, handle_type, checklist,desp)
        return "$ {0:.2f}".format(price)
        
@app.callback(Output('output-img', 'children'),
              [Input('submit-button-2', 'n_clicks')],
              [State('url', 'value'),State('pick-list', 'value')
              ])
def update_img(n_clicks, url, pick_one):
    if n_clicks == 0:
        return ""
    else:
        # read df to show output, should be output from function in real-time
        #df = pd.read_pickle('df_recom.pickle')
        
        df,df2 = recommend_bike.recommend_bike(url,pick_one,city='US')

        #img_src="https://i.ibb.co/8N2fvwW/bike3.jpg"
        #web_url = "https://ibb.co/Kb7f4gM"
        #price = 1000
        #html.Img(src = img_src , alt = "Bike Images 1", width = "500", height= "600")
        #html.A(html.Img(src = img_src, alt = "Bike Image", width = "200", height = "300"), href = web_url), 
        #className = 'four columns'
        return html.Div([html.Br(),
                html.Div(className = 'row', children = [
                    html.Div([html.H6('THE BIKE YOU PICKED: {}'.format(df2.iloc[0]['title'])),
                          html.H6('Price: $ {0:.2f}'.format(df2.iloc[0]['price'])),
                          html.P('Bicycle Type: {}'.format(df2.iloc[0]['bicycletype'])),
                          html.P('Manufacturer: {}'.format(df2.iloc[0]['makemanufacturer'])),
                          html.P('Condition: {}'.format(df2.iloc[0]['condition'])),
                          html.P('Frame Size: {}'.format(df2.iloc[0]['framesize'])),
                          html.P('Wheel Size: {}'.format(df2.iloc[0]['wheelsize'])),
                          html.A(children = 'Link to the bicycle listing', href = df2.iloc[0]['URL'].strip())
                    ], className = 'eight columns'),
                    html.Div([html.Br(),html.Br(),
                        html.Img(src = df2.iloc[0]['imageURL'].strip(), alt = 'Bike Image', width = '300', height = '200' )], 
                         className = 'four columns')]),
                html.Hr(style = {'margin-bottom' : '1.5rem', 'margin-top': '1.5rem'}),
                html.Div(className = 'row', children = [
                    html.Div([html.H6('Title: {}'.format(df.iloc[0]['title']), style = {'color': theme_blue}),
                          html.H6('Price: $ {0:.2f}'.format(df.iloc[0]['price']), style = {'color': theme_blue}),
                          html.P('Bicycle Type: {}'.format(df.iloc[0]['bicycletype'])),
                          html.P('Manufacturer: {}'.format(df.iloc[0]['makemanufacturer'])),
                          html.P('Condition: {}'.format(df.iloc[0]['condition'])),
                          html.P('Frame Size: {}'.format(df.iloc[0]['framesize'])),
                          html.P('Wheel Size: {}'.format(df.iloc[0]['wheelsize'])),
                          html.A(children = 'Link to the bicycle listing', href = df.iloc[0]['URL'].strip())
                    ], className = 'eight columns'),
                    html.Div([html.Br(),html.Br(),
                        html.Img(src = df.iloc[0]['imageURL'].strip(), alt = 'Bike Image', width = '300', height = '200' )], 
                         className = 'four columns')]),
                html.Hr(style = {'margin-bottom' : '1.5rem', 'margin-top': '1.5rem'}),
                html.Div(className = 'row', children = [
                    html.Div([html.H6('Title: {}'.format(df.iloc[1]['title']), style = {'color': theme_blue}),
                          html.H6('Price: $ {0:.2f}'.format(df.iloc[1]['price']), style = {'color': theme_blue}),
                          html.P('Bicycle Type: {}'.format(df.iloc[1]['bicycletype'])),
                          html.P('Manufacturer: {}'.format(df.iloc[1]['makemanufacturer'])),
                          html.P('Condition: {}'.format(df.iloc[1]['condition'])),
                          html.P('Frame Size: {}'.format(df.iloc[1]['framesize'])),
                          html.P('Wheel Size: {}'.format(df.iloc[1]['wheelsize'])),
                          html.A(children = 'Link to the bicycle listing', href = df.iloc[1]['URL'].strip())
                    ], className = 'eight columns'),
                    html.Div([html.Br(),html.Br(),
                        html.Img(src = df.iloc[1]['imageURL'].strip(), alt = 'Bike Image', width = '300', height = '200' )], 
                         className = 'four columns')]),
                html.Hr(style = {'margin-bottom' : '1.5rem', 'margin-top': '1.5rem'}),
                html.Div(className = 'row', children = [
                    html.Div([html.H6('Title: {}'.format(df.iloc[2]['title']), style = {'color': theme_blue}),
                          html.H6('Price: $ {0:.2f}'.format(df.iloc[2]['price']), style = {'color': theme_blue}),
                          html.P('Bicycle Type: {}'.format(df.iloc[2]['bicycletype'])),
                          html.P('Manufacturer: {}'.format(df.iloc[2]['makemanufacturer'])),
                          html.P('Condition: {}'.format(df.iloc[2]['condition'])),
                          html.P('Frame Size: {}'.format(df.iloc[2]['framesize'])),
                          html.P('Wheel Size: {}'.format(df.iloc[2]['wheelsize'])),
                          html.A(children = 'Link to the bicycle listing', href = df.iloc[2]['URL'].strip())
                    ], className = 'eight columns'),
                    html.Div([html.Br(),html.Br(),
                        html.Img(src = df.iloc[2]['imageURL'].strip(), alt = 'Bike Image', width = '300', height = '200' )], 
                         className = 'four columns')]),
                html.Hr(style = {'margin-bottom' : '1.5rem', 'margin-top': '1.5rem'}),
                html.Div(className = 'row', children = [
                    html.Div([html.H6('Title: {}'.format(df.iloc[3]['title']), style = {'color': theme_blue}),
                          html.H6('Price: $ {0:.2f}'.format(df.iloc[3]['price']), style = {'color': theme_blue}),
                          html.P('Bicycle Type: {}'.format(df.iloc[3]['bicycletype'])),
                          html.P('Manufacturer: {}'.format(df.iloc[3]['makemanufacturer'])),
                          html.P('Condition: {}'.format(df.iloc[3]['condition'])),
                          html.P('Frame Size: {}'.format(df.iloc[3]['framesize'])),
                          html.P('Wheel Size: {}'.format(df.iloc[3]['wheelsize'])),
                          html.A(children = 'Link to the bicycle listing', href = df.iloc[3]['URL'].strip())
                    ], className = 'eight columns'),
                    html.Div([html.Br(),html.Br(),
                        html.Img(src = df.iloc[3]['imageURL'].strip(), alt = 'Bike Image', width = '300', height = '200' )], 
                         className = 'four columns')]),
                html.Hr(style = {'margin-bottom' : '1.5rem', 'margin-top': '1.5rem'}),
                html.Div(className = 'row', children = [
                    html.Div([html.H6('Title: {}'.format(df.iloc[4]['title']), style = {'color': theme_blue}),
                          html.H6('Price: $ {0:.2f}'.format(df.iloc[4]['price']), style = {'color': theme_blue}),
                          html.P('Bicycle Type: {}'.format(df.iloc[4]['bicycletype'])),
                          html.P('Manufacturer: {}'.format(df.iloc[4]['makemanufacturer'])),
                          html.P('Condition: {}'.format(df.iloc[4]['condition'])),
                          html.P('Frame Size: {}'.format(df.iloc[4]['framesize'])),
                          html.P('Wheel Size: {}'.format(df.iloc[4]['wheelsize'])),
                          html.A(children = 'Link to the bicycle listing', href = df.iloc[4]['URL'].strip())
                    ], className = 'eight columns'),
                    html.Div([html.Br(),html.Br(),
                        html.Img(src = df.iloc[4]['imageURL'].strip(), alt = 'Bike Image', width = '300', height = '200' )], 
                         className = 'four columns')]),
#                dcc.Graph(figure = dict(
#                    data = [go.Scattermapbox(
#                            lat=[s.strip() for s in df['latitude'].values],
#                            lon=['-' + s.strip() for s in df['longitude'].values],
#                            mode='markers',
#                            marker=dict(size=12,color = 'rgb(255,0,0)'),
#                            text=list(df['title'].values),)],
#                    layout = go.Layout(
#                                autosize=True,
#                                hovermode='closest',
#                                mapbox=dict(
#                                        accesstoken=mapbox_access_token,
#                                        bearing=0,
#                                        center=dict(lat=40,lon=-95),
#                                        pitch=0,
#                                        zoom=3),)))
        ])

    

#<a href="https://ibb.co/Kb7f4gM"><img src="https://i.ibb.co/8N2fvwW/bike3.jpg" alt="bike3" border="0"></a>
#html.A(html.Button('Submit feedback!', className='three columns'),
#    href='https://github.com/czbiohub/singlecell-dash/issues/new')
#),

# run app
if __name__ == '__main__':
    app.run_server(host = '0.0.0.0', port = '5000',debug = True)