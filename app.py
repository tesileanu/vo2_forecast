import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_percentile(row):
    if row['gender'] == 'm':
        return np.exp(row['SumM'])/(1+np.exp(row['SumM']))
    elif row['gender'] == 'f':
        return np.exp(row['SumF'])/(1+np.exp(row['SumF']))
    
app = dash.Dash()   #initialising dash app
server = app.server

app.layout = html.Div(
    id = 'parent', children = [
        html.H1(
            id = 'H1', 
            children = 'VO2max Predictor', 
            style = {'textAlign':'center','marginTop':40,'marginBottom':40}
        ),
        dcc.Dropdown(
            id = 'dropdown',
            options = [
                {'label':'Male', 'value':'m' },
                {'label': 'Female', 'value':'f'},
            ],
            placeholder='Select Gender...',
            style={
                'width': '50%'
            }
        ),
        'Age: ', dcc.Input(
            id="input_age",
            type="number",
            placeholder="Age",
            value=20
        ),
        html.Br(),
        'VO2max ', dcc.Input(
            id="input_vo2",
            type="number",
            placeholder="VO2max",
            value=48
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        'Activities', dcc.Checklist(
            id='activities',
            options=[
                {'label': 'Run at 6 MPH', 'value': 'run'},
                {'label': 'Hiking', 'value': 'hike'},
                {'label': 'Slow walk (3.5MPH)', 'value': 'walk'},
            ],
            value=[]
        ),   
        dcc.Graph(
            id = 'bar_plot'
        )
    ]
)
    
    
@app.callback(
        Output(component_id='bar_plot', component_property= 'figure'),
        [Input(component_id='dropdown', component_property= 'value'),
         Input(component_id='input_age', component_property= 'value'),
         Input(component_id='input_vo2', component_property= 'value'),
         Input(component_id='activities', component_property= 'value')]
)
def graph_update(dropdown_value, input_age, input_vo2, list_of_activities):

    age = input_age
    vo2_max = input_vo2
    gender = dropdown_value
    df = pd.DataFrame(columns = ['years','vo2_max','gender','aM','bM','SumM','aF','bF','SumF','percentile'])
    df['years'] = range(age, 105, 10)
    df['gender'] = gender
    df.loc[0, 'vo2_max'] = vo2_max
    for index, row in df.iterrows():
        if index==0:
            continue
        else:
            df.loc[index, 'vo2_max'] = df.loc[index-1,'vo2_max']*0.9

    df['aM'] = - 9.27 - 0.0722*df['years'] + 0.001209*df['years']**2
    df['bM'] = 0.209 + 0.0012*df['years'] - 0.000006*df['years']**2
    df['SumM'] = df['aM'] + df['bM']*df['vo2_max']
    df['aF'] = - 9.3 + 0.0069*df['years'] - 0.0003*df['years']**2
    df['bF'] = 0.25 - 0.0012*df['years'] + 0.00004*df['years']**2
    df['SumF'] = df['aF'] + df['bF']*df['vo2_max']
    df['percentile'] = df.apply(lambda row: calculate_percentile(row), axis=1).round(2)
    
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x = df['years'], y = df['vo2_max'],\
                     line = dict(color = 'blue', width = 4), name= 'VO2_max'), secondary_y=False
                     )
    fig.add_trace(go.Scatter(x = df['years'], y = df['percentile'],\
                     line = dict(color = 'firebrick', width = 4), name='Percentile'), secondary_y=True
                     )
    fig.update_yaxes(
        title_text="VO2max", 
        secondary_y=False,
        range=[0,70]
        )
    fig.update_yaxes(
        title_text="Percentile", 
        secondary_y=True,
        range=[0, 1]
    )

    if 'hike' in list_of_activities:
        fig.add_hline(y=25.5, line_dash="dot",
                annotation_text="Hiking", 
                annotation_position="bottom right",
                annotation_font_size=10,
                annotation_font_color="black"
                )
        #fig.add_annotation(text="You will have difficulty hiking starting at " +  + "years old",
        #          xref="paper", yref="paper",
        #          x=0.3, y=0.3, showarrow=False)
    if 'run' in list_of_activities:
        fig.add_hline(y=34.3, line_dash="dot",
                annotation_text="Running", 
                annotation_position="bottom right",
                annotation_font_size=10,
                annotation_font_color="black"
                )
    if 'walk' in list_of_activities:
        fig.add_hline(y=15, line_dash="dot",
                annotation_text="Slow Walk", 
                annotation_position="bottom right",
                annotation_font_size=10,
                annotation_font_color="black"
                )
    
    
    fig.update_xaxes(
        title_text="Age", 
        )
    
    #fig.update_layout(title = 'VO2max over time',
    #                  xaxis_title = 'Years',
    #                  yaxis_title = 'VO2max Percentile'
    #                  )
    return fig  

if __name__ == '__main__': 
    app.run_server(debug=False)