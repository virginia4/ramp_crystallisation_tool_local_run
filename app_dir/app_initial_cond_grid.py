# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
from builtins import range  # pylint: disable=redefined-builtin
import dash_table
import collections
import os 
import fnmatch
import glob
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import xlrd   
import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash import html, dcc
from dash.dependencies import Input, Output, State
#import dash_table_experiments as dt
from .common import generate_table


import pandas as pd
import numpy as np
#from . import uniform
from . import opti_models
from . import app
import chart_studio.plotly as plt

# pylint: disable=redefined-builtin
script_path = os.path.dirname(os.path.realpath(__file__))
myPath= os.path.join( script_path,'MDL_screens_database')


###############################################################################
def get_controls_var(id, desc, unit, range):
    """Get controls for each variable.

    This includes
     * the description
     * range 
    """
    label_reagent = dcc.Input(
        id=id + "_label", type='text', value=desc, className="label")
    unit_reagent = dcc.Input(
        id=id + "_unit", type='text', value=unit, className="label")
    range_low = dcc.Input(
        id=id + "_low", type='number', value=range[0], className="range")
    range_high = dcc.Input(
        id=id + "_high", type='number', value=range[1], className="range")

    return html.Tr([
        html.Td(label_reagent),
        html.Td(unit_reagent),
        html.Td([range_low, html.Span('to'), range_high])], id=id + "_tr")

#------------------------------------------------------------------------------


###############################################################################
def get_controls_screen(id, desc, range):
    """ Get screen dimensions nsamples_x and nsamples_y
    """
    label = dcc.Input(id = id + "_label", type = 'text', value=desc,
        className = 'label')
    dimensions_x = dcc.Input(
        id=id + "_x", type='number', value=range[0], className="range")
    dimensions_y = dcc.Input(
        id=id + "_y", type='number', value=range[1], className="range")
    return html.Tr([
        html.Td(label),
        html.Td([dimensions_x, html.Span('\\times'), dimensions_y])], id=id + "_tr")
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------

code = collections.OrderedDict([
    ('code_number',
     dict(label=['MDL file code'])),
    ])


##############################################################################
# reagents_grid = collections.OrderedDict([
#     ('reagent_1_grid', dict(label='Reagent 1', unitslabel='[Units 1]', range=[100.0, 200.0])),
#     ('reagent_2_grid', dict(label='Reagent 2', unitslabel='[Units 2]', range=[1.0, 6.0]))])

# NVARS_DEFAULT = len(reagents_grid)


# Fill up to NVARS_MAX (needed to define callbacks)
NVARS_MAX = 10
# for i in range(len(reagents_grid), NVARS_MAX):
#     k = 'Reagent {}'.format(i + 1)
#     l = '[Units {}]'.format(i + 1)
#     reagents_grid[k] = dict(label=k,  unitslabel=l, range=[0, 1])

# var_grid_ids = list(reagents_grid.keys())
# print('var_grid_ids', var_grid_ids )

# # var_labels = [v['label'] for v in list(reagents_grid.values())]


# controls_dict = collections.OrderedDict()
# for k, v in list(reagents_grid.items()):
#     controls = get_controls_var(k, v['label'], v['unitslabel'], v['range'])
#     print("controls (l.104): \n",type(controls))
#     controls_dict[k] = controls


# head_row = html.Tr([
#     html.Th('Reagent   '),
#     html.Th('[Units]  '),
#     html.Th('Range  ')
# ])

# controls_html = html.Table(
#     [head_row] + list(controls_dict.values()), id='controls_grid')
# label_states = [State(k + "_label", 'value') for k in var_grid_ids
# ]
# unit_states = [State(l + "_label", 'value') for l in var_grid_ids
# ]
# low_states = [State(k + "_low", 'value') for k in var_grid_ids]
# high_states = [State(k + "_high", 'value') for k in var_grid_ids]
# # weight_states = [
# #     dash.dependencies.State(k + "_weight", 'value') for k in var_ids
# # ]



inp_nvars = html.Tr([
    html.Td('Number of reagents: '),
    html.Td(
        dcc.Input(
            id='inp_nvars_grid',
            value=' ',
            max=NVARS_MAX,
            min=1,
            className="nvars range"))
])

inp_code_hitwell = html.Tr([
    html.Td('Enter screen code (e.g. MD1-40) and hit well (e.g. B1):'),
    html.Td(dcc.Input(id='inp_code_grid',
            type='text', 
            value="MD1-40")),
    html.Td(dcc.Input(
            id='inp_hitwell_grid',
            type='text', 
            value="B1")),
    html.Div('', id='input_info_grid')])

btn_submit = html.Tr([html.Td(html.Button('Submit', id = 'submit-button_grid', className='action-button', n_clicks=0)),
    html.Div('', id='submit_info_grid')
    ])

###########################################################################################
grid_text = '''
Grid search is the process of searching on the nearby space of a set of data for the optimal 
parameters. Here, the search is performed by separating the two-dimensional space equally 
and then dividing the given range into equally distributed spaces. The result is a set of 96 
conditions that cover the whole range. 

In this implementation, the grid search is limited to the search of two conditions, depending 
on the parameters in the hit well. The grid algorithm optimises first the **precipitant** and the **salt concentration** 
(first reagents found in the file). If there is not a precipitant in the screen, 
it will vary the **pH of the buffer** and the **salt concentration**. If there is no buffer but there 
are two salts in the screen, it optimises the **concentrations of the salts**. Finally, if there 
are not salts present, it optimises the concentration of **precipitant concentration and the pH 
of the buffer**. 

We are working on giving the option for the users to choose which two conditions they want to 
optimise. That will allow the user to have more control of the optimisation process. 
'''
grid_text_html = dcc.Markdown(grid_text)
# [html.P(i) for i in grid_text.split("\n\n")]

grid_layout = html.Div([html.H2("About the grid search"),
                    dcc.Markdown(grid_text, className="text-container", id="grid_container",
                    # **{'data-iframe-height': ''}, 
                    style={ 'width': '50%','padding': '20px', 
                    'margin': '10px','justify-content': 'center','align-items': 'center'})])

###########################################################################################

fnameDict = {'chriddy': ['opt1_c', 'opt2_c', 'opt3_c'], 'jackp': ['opt1_j', 'opt2_j']}

names = list(fnameDict.keys())
nestedOptions = fnameDict[names[0]]

@app.callback(
    Output('opt-dropdown', 'options'),
    [Input('name-dropdown', 'value')]
)
def update_date_dropdown(name):
    return [{'label': i, 'value': i} for i in fnameDict[name]]

@app.callback(
    Output('display-selected-values', 'children'),
    [Input('opt-dropdown', 'value')])
def set_display_children(selected_value):
    return 'you have selected {} option'.format(selected_value)


##############################################################################
# print("label_states, type(label_states)", label_states, type(label_states))
states = [State('inp_code_grid', 'value')]
states += [State('inp_hitwell_grid', 'value')]

@app.callback(
    [Output('submit_info_grid', 'children'),
     Output('inp_nvars_grid', 'value')],
    [Input('submit-button_grid', 'n_clicks')],
    states
)
def update_output_code_hitwell(n_clicks, *args):
    # Default output when waiting for user input
    if n_clicks is None or n_clicks <= 0:
        return [
            html.Tr([
                html.Td(dcc.Textarea(
                    placeholder=' ',
                    value='Awaiting input...',
                    style={'width': '50%'}
                ))
            ]), 0
        ]

    hitwell = args[-1]
    code_name = args[-2] + "*"
    file_list = sorted([file for file in os.listdir(myPath) if fnmatch.fnmatch(file, code_name)])

    if not file_list:
        return [
            html.Tr([
                html.Td(dcc.Textarea(
                    placeholder=' ',
                    value='No matching file found. Please check the inputs.',
                    style={'width': '50%'}
                ))
            ]), 0
        ]

    file_found = file_list[0]
    newpath = os.path.join(myPath, file_found)

    try:
        xls = pd.ExcelFile(newpath)
        df1 = pd.read_excel(xls)
    except Exception as e:
        return [
            html.Tr([
                html.Td(dcc.Textarea(
                    placeholder=' ',
                    value=f'Error reading file: {str(e)}. Please report this issue.',
                    style={'width': '50%'}
                ))
            ]), 0
        ]

    # Processing dataframe
    searched_value = hitwell
    try:
        if "Tube #" in df1.columns:
            df_searched_value = df1[df1["Tube #"] == int(searched_value)]
        else:
            df_searched_value = df1[df1["Well #"] == searched_value]

        if df_searched_value.empty:
            raise ValueError("No matching rows found for the provided value.")
    except Exception as e:
        return [
            html.Tr([
                html.Td(dcc.Textarea(
                    placeholder=' ',
                    value=f'Error processing input: {str(e)}. Check the inputs.',
                    style={'width': '50%'}
                ))
            ]), 0
        ]

    # Cleanup and filtering
    df_searched_value.replace(r'None', np.nan, inplace=True)
    df_searched_value.replace(r'-', np.nan, inplace=True)
    df_filtered = df_searched_value.dropna(axis='columns')

    # Creating the table
    kk = dash_table.DataTable(
        id='table_grid',
        data=df_filtered.to_dict('records'),
        editable=True,
        columns=[{"name": i, "id": i} for i in df_filtered.columns],
        fixed_columns={'headers': True, 'data': 1},
        style_cell={
            'minWidth': '180px', 'width': '100px', 'maxWidth': '180px',
            'overflow': 'hidden', 'textOverflow': 'ellipsis',
        },
        style_table={
            'maxHeight': '500px',
            'overflowY': 'scroll',
        },
        style_as_list_view=True,
    )

    # Calculating new variables
    concentrations = df_filtered.filter(like='Conc').columns
    nvars_new = len(concentrations)

    return [html.Tr([html.Td(kk)]), nvars_new]


# @app.callback(
#     [Output('submit_info_grid', 'children'),
#      Output('inp_nvars_grid', 'value')], 
#     [Input('submit-button_grid', 'n_clicks')],
#     states)
# def update_output_code_hitwell(n_clicks, *args):
#     hitwell = args[-1]
#     code_name = args[-2]


#     code_name = code_name + "*"
#     counter = 0
#     file_list = []
#     for file in os.listdir(myPath):
#         if fnmatch.fnmatch(file, code_name):
#             file_list.append(file)
#     file_list.sort()
#     print(file_list)
#     if len(file_list) > 1:
#         file_found = file_list[0]
#     elif len(file_list) == 1:
#         file_found = file_list[0]
#     print ("The file you called is: \n", file_found)
#     newpath = os.path.join(myPath, file_found)
#     xls = pd.ExcelFile(newpath)
#     df1 = pd.read_excel(xls)
#     print("hitwell type: ", type(hitwell))
#     searchedValue = hitwell
#     print("searchedValue type: ", type(searchedValue))
#     tube = df1.filter(like='Tube').columns
#     print("tube:", tube)
#     well = df1.filter(like='Well').columns

#     if well.empty == True: 
#         print('tube and tube number:', searchedValue)
#         # df_searchedValue = df1[df1["Tube #"] == searchedValue]
#         try:
#             df_searchedValue = df1[df1["Tube #"] == int(searchedValue)]
#             print("df_searchedValue \n", df_searchedValue)
#         except:
#             print("Something went wrong, try something new")
#             df_searchedValue = df1[df1["Tube #"] == searchedValue]
#             print("df_searchedValue \n", df_searchedValue)

#         df_new = df1.set_index("Tube #", drop = False)
#         df_new.astype('str') 
#         print("df_new \n", df_new)
#         df_hit_well = df_searchedValue
#         print("df_hit_well \n", df_hit_well)
#         print("type(df_hit_well) =  ", type(df_hit_well.index))
#     else: 
#         try:
#             df_searchedValue = df1[df1["Well #"] == searchedValue]
#             df_new = df1.set_index("Well #", drop = False)
#             df_hit_well = df_new.loc[[searchedValue]]
#             print("df_hit_well \n", df_hit_well)
#             print("type(df_hit_well) =  ", type(df_hit_well.index))
#         except:
#             return ([ html.Tr([ html.Td(dcc.Textarea(
#                 placeholder=' ',
#                 value='An error occurred. Check if the inputs are correct. If there the error persists, please report at: enquiries@moleculardimensions.com',
#                 style={'width': '50%'}))]), 0])

    
#     df_hit_well = df_hit_well.replace(r'None', np.nan)
#     df_hit_well = df_hit_well.replace(r'-', np.nan)
#     df_hit_values = df_hit_well.dropna(axis='columns')
            
#     rows = np.shape(df_hit_values)[0]
#     columns = np.shape(df_hit_values)[1]
#     concentrations = df_hit_values.filter(like='Conc').columns
#     kk = dash_table.DataTable(
#                                 id='table_grid',
#                                 data=df_hit_values.to_dict('records'), editable=True,
#                                 columns=[{"name": i, "id": i} for i in df_hit_values.columns], 
#                                 fixed_columns={ 'headers': True, 'data': 1}, 
#                                 style_cell = {
#                                 # all three widths are needed
#                                 'minWidth': '180hpx', 'width': '100px', 'maxWidth': '180px',
#                                 'overflow': 'hidden',
#                                 'textOverflow': 'ellipsis',
#                                 },style_as_list_view=True,) 

#     nvars_new = len(concentrations)

#     salts_labels = df_hit_values.filter(like='Salt').columns.values
#     buff_labels = df_hit_values.filter(like='Buffer').columns.values
#     perci_labels = df_hit_values.filter(like='Precipitant').columns.values
#     units_labels = df_hit_values.filter(like='Unit').columns.values

#     reagent_name = np.concatenate([df_hit_values.iloc[0][salts_labels[:]], df_hit_values.iloc[0][buff_labels[:]], df_hit_values.iloc[0][perci_labels[:]] ])
#     reagent_name = reagent_name.tolist()
#     reagent_name_1 = reagent_name[0]
#     reagent_name_2 = reagent_name[1]


#     if n_clicks > 0:
#         return ([ html.Tr([html.Td(kk)]), nvars_new])
#------------------------------------------------------------------------------

inp_nsamples = html.Tr([
    html.Td('Enter screen dimensions '),
    html.Td(
        dcc.Input(
            id='nsamples_x_grid', type='number', value=8,
            className="nsamples range")), 
    html.Td(html.Span('x')),
    html.Td(
        dcc.Input(
            id='nsamples_y_grid', type='number', value=12,
            className="nsamples range"))
])

##############################################################################

#------------------------------------------------------------------------------



##############################################################################

#------------------------------------------------------------------------------

btn_compute = html.Div([
    html.Button('Grid method', id='btn_compute_grid', className='action-button', n_clicks = 0),
    html.Div('', id='compute_info_grid')
])

# Creation of dash app

layout = html.Div(
    [
        grid_layout,
        html.Table([inp_code_hitwell]),
        html.Br(),
        html.Table([btn_submit]),
        html.Br(),
        html.Table([inp_nvars, inp_nsamples]),
        html.Br(),
        btn_compute,
    ],
    style={'padding': 20},
    id="container_grid",
    # tag for iframe resizer
    **{'data-iframe-height': ''},
)
#------------------------------------------------------------------------------

#############################################################################

#------------------------------------------------------------------------------
ninps = 5
# print("label_states, type(label_states)", label_states, type(label_states))
# states = label_states + unit_states + low_states + high_states 
states = [State('inp_nvars_grid', 'value')]
states += [State('nsamples_x_grid', 'value')]
states += [State('nsamples_y_grid', 'value')]
states += [State('inp_code_grid', 'value')]
states += [State('inp_hitwell_grid', 'value')]


# ##############################################################################


@app.callback(
    Output('compute_info_grid', 'children'),
    [Input('table_grid', 'data'),
     Input('btn_compute_grid', 'n_clicks')
    ], states)

def on_compute(submit_info, n_clicks, *args):
    """Callback for clicking compute button"""
    if n_clicks is None :
        return ''

    df_hit_values = pd.DataFrame(submit_info)
    if len(args) != ninps:
        raise ValueError("Expected {} arguments".format(ninps))

    # parse arguments
    hitwell = args[-1]
    code_name = args[-2]
    nsamples_y = args[-3]
    nsamples_x = args[-4]

    n_pH = len(df_hit_values.filter(like='pH').columns)
    n_units = len(df_hit_values.filter(like='Units').columns)
    n_salts = len(df_hit_values.filter(like='Salt').columns)
    n_buff =  len(df_hit_values.filter(like='Buffer').columns)
    n_precip = len(df_hit_values.filter(like='Precipitant').columns)
    
    concentrations = df_hit_values.filter(like='Conc').columns
    var = df_hit_values[concentrations].to_numpy()
    var = var.T
    var_float = var.astype(float)

    pH =  df_hit_values.filter(like='pH').columns
    pH = df_hit_values[pH].to_numpy()
    
    salt_conc = var[0:n_salts]
    buff_conc = var[(n_salts):(n_salts+n_buff)]
    precip_conc = var[(n_salts+n_buff):(n_salts+n_buff+n_precip)]

    # VARY RANGE OF CONCERN: 
    # For grid we can only use two parameters. I chose the salt conconcetration
    # low_vals = np.array([args[i + NVARS_MAX] for i in range(nvars)])
    # high_vals = np.array([args[i + 2 * NVARS_MAX] for i in range(nvars)
    # NOTE: check if salt_conc, ph and precip_conc are float arrays. This check is 
    # important, cause after the user will update the number in the table, 
    # the values are parsed as str. 

    # low_vals = np.array([args[i + NVARS_MAX] for i in range(nvars)])
    # high_vals = np.array([args[i + 2 * NVARS_MAX] for i in range(nvars)])

    nvars = n_salts + n_pH + n_precip
    nsamples = nsamples_x*nsamples_y

    salts_labels = df_hit_values.filter(like='Salt').columns.values
    buff_labels = df_hit_values.filter(like='Buffer').columns.values
    perci_labels = df_hit_values.filter(like='Precipitant').columns.values
    name_salts = np.concatenate([df_hit_values.iloc[0][salts_labels[:]]])
    name_buff = np.concatenate([df_hit_values.iloc[0][buff_labels[:]]])
    name_perci = np.concatenate([df_hit_values.iloc[0][perci_labels[:]]])


    units_labels = df_hit_values.filter(like='Unit').columns.values
    units_labels_salts = units_labels[0:n_salts]
    units_labels_buff = units_labels[(n_salts):(n_salts+n_buff)]
    units_labels_perci = units_labels[(n_salts+n_buff):(n_salts+n_buff+n_precip)]
    unit_name_salts = np.concatenate([df_hit_values.iloc[0][units_labels_salts[:]]])
    unit_name_buff = np.concatenate([df_hit_values.iloc[0][units_labels_buff[:]]])
    unit_name_perci = np.concatenate([df_hit_values.iloc[0][units_labels_perci[:]]])

    print("units_labels = \n", units_labels)
    print("units_labels_salts = \n", units_labels_salts)
    print("units_labelslabels_buff = \n", units_labels_buff)
    print("units_labels_perci = \n", units_labels_perci)

    reagent_name = np.concatenate([df_hit_values.iloc[0][salts_labels[:]], df_hit_values.iloc[0][buff_labels[:]], df_hit_values.iloc[0][perci_labels[:]] ])
    reagent_name = reagent_name.tolist()

    labels = reagent_name 
    labels_array = np.asarray(labels)
    # dim = len(labels_array)
    dim = 2 # because for grid we always want two dimensions 
    styling_label_1 = [' ['] * dim
    styling_label_2 = [']'] * dim
    styling_label_1_array = np.asarray(styling_label_1)
    styling_label_2_array = np.asarray(styling_label_2)
    labels_array_new = ["" for x in range(dim)]

    if len(precip_conc) > 0 and len(salt_conc) > 0:
        grid_var_1_range = [precip_conc[0]/4, precip_conc[0]*4]
        grid_var_2_range = [salt_conc[0]/2, salt_conc[0]*2]
        
        try:
            label_1 = name_perci[0] + styling_label_1[0] + unit_name_perci[0] + styling_label_2[0]
            label_2 = name_salts[0] + styling_label_1[0] +unit_name_salts[0] + styling_label_2[0]
            labels_array_new[0:dim] =  [label_1, label_2]
        except:
            return dcc.Textarea(
                placeholder='Enter a value...',
                value='An error occurred. Please report at: enquiries@moleculardimensions.com',
                style={'width': '40%'}
                )  

    elif len(pH) > 0 and len(salt_conc) > 0:
        grid_var_1_range = [pH[0]-1, pH[0]+1]
        grid_var_2_range = [salt_conc[0]/2, salt_conc[0]*2] 

        try: 
            label_1 = name_buff[0] + styling_label_1[0] + 'pH' + styling_label_2[0]
            label_2 = name_salts[0] + styling_label_1[0] + unit_name_salts[0] + styling_label_2[0]
            labels_array_new[0:dim] =  [label_1, label_2] 
        except:
            return dcc.Textarea(
                placeholder='Enter a value...',
                value='An error occurred. Please report at: enquiries@moleculardimensions.com',
                style={'width': '40%'}
                )  

            # html.Div('An error occurred')
            # Textarea


    elif len(salt_conc) == 0: 
        grid_var_1_range = [precip_conc[0]/4, precip_conc[0]*4]
        grid_var_2_range = [pH[0]-1, pH[0]+1]

        try:
            label_1 = name_perci[0] + styling_label_1[0] + unit_name_perci[0] + styling_label_2[0]
            label_2 = name_buff[0] + styling_label_1[0] + 'pH' + styling_label_2[0]
            labels_array_new[0:dim] =  [label_1, label_2] 
        except: 
            return dcc.Textarea(
                placeholder='Enter a value...',
                value='An error occurred. Please report at: enquiries@moleculardimensions.com',
                style={'width': '40%'}
                )  
    
    else:
        grid_var_1_range = [salt_conc[0]/2, salt_conc[0]*2]
        grid_var_2_range = [salt_conc[1]/2, salt_conc[1]*2]

        try: 
            label_1 = name_salts[0] + styling_label_1[0] + unit_name_salts[0] + styling_label_2[0]
            label_2 = name_salts[1] + styling_label_1[0] + unit_name_salts[1] + styling_label_2[0]
            labels_array_new[0:dim] =  [label_1, label_2]
        except: 
            return dcc.Textarea(
                placeholder='Enter a value...',
                value='An error occurred. Please report at: enquiries@moleculardimensions.com',
                style={'width': '40%'}
                )  
    
    print("Range for grid method: \n", grid_var_1_range, grid_var_2_range)
    low_vals = np.concatenate([grid_var_1_range[0], grid_var_2_range[0]])
    high_vals = np.concatenate([grid_var_1_range[1], grid_var_2_range[1]])

 
    # For grid he NVARS must be always 2 cause   
    samples_1 = maxmin.compute_grid(nsamples_x, nsamples_y, low_vals, high_vals,  NVARS = 2)
    df = pd.DataFrame(data=samples_1, columns=labels_array_new)
    table = generate_table(df, nsamples_x, nsamples_y, download_link=True)
    np.set_printoptions(precision=3)
    if n_clicks > 0:
        try:
            return table
        except: 
            return html.Div('An error occurred')

#------------------------------------------------------------------------------


