# %%
# import dependencies
import pandas as pd
import plotly.express as px
import numpy as n
from dash import Dash, dcc, html, Input, Output, dash_table, State

# %%
# read in csv file & view first 5 rows
df = pd.read_csv("data.csv")

# %%
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
               'https://use.fontawesome.com/releases/v5.7.2/css/all.css'] # load the CSS stylesheet

app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app
server=app.server

states = df['State'].unique() #Creates list of states 
zipcodes = df['ZIP Code'].unique() #Creates list of zipcodes
conditions = df["Condition"].unique() #Creates list of conditions

app.layout = html.Div(style={'backgroundColor': 'beige'}, children=[
    ##Makes title of dashboard, including surrounding by hospital icons
html.Div([
    html.Div([
    html.I(className = "fas fa-hospital", style={"font-size": "48px"}),
    html.H1("Find the Best Medical Service For You!", style={"font-family": "Montserrat, sans-serif"}),
    html.I(className = "fas fa-hospital", style={"font-size": "48px"})],
        style={"color": "maroon", "display": "flex", "align-items": "center", "justify-content": "center"})], className="twelve columns"), #styles to center heading and make it maroon
html.Br(),
html.Br(),
html.Div([
html.Div([ #Subheading providing instructions for using website
    html.P("Select your state and/or nearest ZIP Code. Additionally, choose the condition for which you are seeking treatment. Based on these parameters, you will receive a list of hospitals along with their corresponding scores, indicating their performance in addressing your condition. Higher scores indicate better-performing hospitals."
, style={"color": "maroon", "font-family": "Montserrat, sans-serif", "font-size": "17px"}, className="twelve columns"), #description under title
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    dcc.Dropdown(      #use dcc to create dropdown menu
        id='state-dropdown',      #ID tag for dropdown
        options=[{'label': state, 'value': state} for state in states],   #specifies to go through each state in the dataframe as the options for the dropdown
        multi=False,     #allows to click single state
        placeholder="Select State",   #name of the dropdown before state is selected
        className= "twelve columns",      #formats dropdown to be on left half of screen
),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    dcc.Dropdown(      #use dcc to create dropdown menu
        id='zipcode-dropdown',      #ID tag for dropdown
        multi=True,     #allows to click multiple zipcodes
        placeholder="Select Zipcode",   #name of the dropdown before zipcodes are selected
        className= "twelve columns",                   #formats dropdown to be on right half of screen
),
    html.Br(),
    html.Br(),
    html.Br(),
    html.P("Enter Condition:", style={"color": "maroon", "font-family": "Montserrat, sans-serif", "font-size": "17px"},
                className="twelve columns"),
        #Creating radio button for conditions from list
        dcc.RadioItems(
        id='condition-dropdown',
        options = [{'label': condition, 'value': condition} for condition in conditions],
        style={"color": "maroon","font-size": "17px"},
        className= "twelve columns",

), ], className="six columns")]),
html.Div([
    #Creating bar graph
    dcc.Graph(
        id="Bar-Graph",
        className="six columns"),
]),
   html.Div([
       #Heading for data table
        html.H2("Hospital Addresses Based On Your Selection:", style = {"font-family": "Montserrat, sans-serif"}),
        html.P("The best performing hospitals are listed at the top.", style={"font-family": "Montserrat, sans-serif", "font-size": "15px"}),
        # Creating data table that will adjust based on output, want to include name, address, county, state, and zip code
        dash_table.DataTable(
            id='data-table',
            columns=[
                {'name': 'Hospital Name', 'id': 'Hospital Name'},
                {'name': 'Address', 'id': 'Address'},
                {'name': 'County Name', 'id': 'County Name'},
                {'name': 'State', 'id': 'State'},
                {'name': 'ZIP Code', 'id': 'ZIP Code'},
            ], style_table={'overflowX': 'auto', 'margin-left': '0px'}, style_cell={'font_size': '16px'})],  style={"color": "maroon"}, 
            className = "table-style"),
            html.A('Link to github', href='https://github.com/heba-shaikh/final')
])

#Callbacks
@app.callback(
    Output('zipcode-dropdown', 'options'),
    Input('state-dropdown', 'value')
)
def update_zipcodes(selected_state):   #To update zipcode selection list based on state that is selected
    if selected_state is None:
        return []
    else:
        zipcodes = df[df['State'] == selected_state]['ZIP Code'].unique()
        return [{'label': zipcode, 'value': zipcode} for zipcode in zipcodes]
    

@app.callback(
    Output('Bar-Graph', 'figure'),
    Input('state-dropdown', 'value'),
    Input('zipcode-dropdown', 'value'),
    Input('condition-dropdown', 'value')
)
def update_graph(selected_state, selected_zipcodes, selected_condition):  #To update bar graph based on selected parameters
    #Copy dataframe and filter it based on selections
    filtered_df = df.copy()
    if selected_state:
        filtered_df = filtered_df[filtered_df['State'] == selected_state]
    if selected_zipcodes:
        filtered_df = filtered_df[filtered_df['ZIP Code'].isin(selected_zipcodes)]
    if selected_condition:
        filtered_df = filtered_df[filtered_df['Condition'] == selected_condition]

    filtered_df = filtered_df.groupby('Hospital Name')['Score'].mean().reset_index() #some hospitals have multiple score's per condition, best to average these to make them cohesive in the bar graph
    filtered_df = filtered_df.sort_values(by='Score', ascending=False) #sort bar graph in descending order

    #Define min and max for bar graph y axis
    min_score = filtered_df['Score'].min() 
    max_score = filtered_df['Score'].max()

    #Define bar graph
    fig = {
        'data': [
            {'x': filtered_df['Hospital Name'].str.slice(0, 10),  #Want only first few characters or it messes up appearance of x axis
             'y': filtered_df['Score'],     #Hospital's associated score on y-axis
             'type': 'bar',
             'marker': {'color': 'maroon'}}],
        #Define layout for title and axes
        'layout': {
            'title': 'Scores based on Zipcode, State, and Condition',
            'xaxis': {'title': {'text':'Hospitals', 'standoff':50}},
            'yaxis': {'title': 'Score', 'range': [min_score, max_score]},
            'margin': {'b': 120}}}
    return fig

@app.callback( 
    Output('data-table', 'data'),
    Input('state-dropdown', 'value'),
    Input('zipcode-dropdown', 'value'),
    Input('condition-dropdown', 'value')
)
def update_table(selected_state, selected_zipcodes, selected_condition): #Update data table based on selected parameters
        #Copy dataframe and filter it based on selections
    filtered_df = df.copy()
    if selected_state:
        filtered_df = filtered_df[filtered_df['State'] == selected_state]
    if selected_zipcodes:
        filtered_df = filtered_df[filtered_df['ZIP Code'].isin(selected_zipcodes)]
    if selected_condition:
        filtered_df = filtered_df[filtered_df['Condition'] == selected_condition]

    #Based on filtered dataframe, get the associated other parameters for the data table
    filtered_df = filtered_df.groupby('Hospital Name').agg({
        'Address': 'first',
        'County Name': 'first',
        'State': 'first',
        'ZIP Code': 'first',
        'Score': 'mean'}).reset_index()

    filtered_df = filtered_df[['Hospital Name', 'Address', 'County Name', 'State', 'ZIP Code', 'Score']]     # Reorder columns
    filtered_df = filtered_df.sort_values(by='Score', ascending=False) #Sort them in descending order by score
    newcols = filtered_df.to_dict('records')     # Convert DataFrame to list of dictionaries
    
    return newcols

if __name__ == '__main__':
    app.run_server(debug=True)
