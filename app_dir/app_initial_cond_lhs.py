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
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
#import dash_table_experiments as dt
from .common import generate_table
import pandas as pd
import numpy as np
from . import opti_models
from . import app
import chart_studio.plotly as plt

# pylint: disable=redefined-builtin

# this command is necessary for the app to find the MDL_screens_database 
# direcotry when you deploy 
script_path = os.path.dirname(os.path.realpath(__file__))
myPath= os.path.join( script_path,'MDL_screens_database')


###############################################################################
def get_controls_var(id, desc, unit, range):
    """
    Get controls for each variable.

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
        html.Td([range_low, html.Span('to'), range_high])], id=id + "_tr_lhs")
#------------------------------------------------------------------------------



###############################################################################
def get_controls_screen(id, desc, range):
    """ 
    Get screen dimensions nsamples_x and nsamples_y
    """
    label = dcc.Input(id = id + "_label", type = 'text', value=desc,
        className = 'label')
    dimensions_x = dcc.Input(
        id=id + "_x", type='number', value=range[0], className="range")
    dimensions_y = dcc.Input(
        id=id + "_y", type='number', value=range[1], className="range")
    return html.Tr([
        html.Td(label),
        html.Td([dimensions_x, html.Span('\\times'), dimensions_y])
         ,
         # html.Td([
         #    # html.Span(slider, className="slider")
         #    # ,
         #    # html.Span('', id=id + "_weight_label")
         # ])
    ], id=id + "_tr_lhs")
#------------------------------------------------------------------------------
###
# 'code' is the variable that gets as input the value from the user. 
# This corresponds to a certain code name of the xlxs files. The program 
# use this to to search in the directory for matches. 
# First, the characteristics of the variable are set, i.e. how to link the 
# variable to the layout-input environment that the user interacts with. 
###
code = collections.OrderedDict([
    ('code_number',
     dict(label=['MDL file code'])),
    ])

NVARS_MAX = 10
###
# inp_nvars: an input variable that is updated with btn_submit and takes the numbers of the reagents 
# that are in each hit condition.
###
inp_nvars = html.Tr([
    html.Td('Number of reagents: '),
    html.Td(
        dcc.Input(
            id='inp_nvars_lhs',
            # type='text',
            value=' ',
            # max=NVARS_MAX,
            # min=1,
            className="nvars range"))
])

###
# inp_code_hitwell: two-input variable, caries the values of both the hitwell and the code of the 
# screen
###
inp_code_hitwell = html.Tr([
    html.Td('Enter screen code (e.g. MD1-40) and hit well (e.g. B1):'),
    html.Td(dcc.Input(id='inp_code_lhs',
            type='text', 
            value="MD1-40")),
    html.Td(dcc.Input(
            id='inp_hitwell_lhs',
            type='text', 
            value="B1")),
    html.Div('', id='input_info_lhs')])

btn_submit = html.Tr([html.Td(html.Button('Submit', id = 'submit-button_lhs', className='action-button', n_clicks=0)),
    html.Div('', id='submit_info_lhs',style={'width': '50%'}), 
    ])

##############################################################################
lhs_text = """
Latin hypercube sampling (LHS) is a sampling method for searching for optimal 
parameters in a high dimensional space. The LHS is a near-random method, i.e. 
the optimised condtions are not completely random, instead they obey certain 
requirements. These requirements assure that the final sample points 
will be spread more evenly across the range. LHS can be used for high-dimension 
spaces, i.e. for more than two conditions.
"""
lhs_text_html = [html.P(i) for i in lhs_text.split("\n\n")]

lhs_layout = html.Div( [html.H2("About the Latin Hybercube sampling"),
                    dcc.Markdown(lhs_text, className="text-container", id="lhs_container",
                    # **{'data-iframe-height': ''}, 
                    style={ 'width': '50%','padding': '20px', 
                    'margin': '10px','justify-content': 'center','align-items': 'center'})])

##############################################################################
# states = label_states + unit_states + low_states + high_states 
states = [State('inp_code_lhs', 'value')]
states += [State('inp_hitwell_lhs', 'value')]

@app.callback(
    [Output('submit_info_lhs', 'children'),
     Output('inp_nvars_lhs', 'value')],
    [Input('submit-button_lhs', 'n_clicks')],
    states)
def update_output_code_hitwell(n_clicks, *args):
    ###
    # arg caries the values of the inputs from the submit button and the inp_nvars_lhs
    ###
    hitwell = args[-1]
    code_name = args[-2]
    
    ###
    # "*" is necessary for finding the file 
    ###
    code_name = code_name + "*"
    counter = 0
    file_list = []
    for file in os.listdir(myPath):
        if fnmatch.fnmatch(file, code_name):
            file_list.append(file)

    ###
    # There are files that have similar names, e.g. MD1-10, MD1-10-ECO. 
    # The following logical statements assure that the correct file is  
    # selected. 
    ###
    file_list.sort()
    print(file_list)
    if len(file_list) > 1:
        file_found = file_list[0]
    elif len(file_list) == 1:
        file_found = file_list[0]
    # print ("The file you called is: \n", file_found)

    ###
    # Find file and assign new path. Then read the the xlxs file in  
    # a Dataframe. 
    ###
    newpath = os.path.join(myPath, file_found)
    xls = pd.ExcelFile(newpath)
    df1 = pd.read_excel(xls)

    ###
    # Search in columns with labels "Tube" and "Well" for the the hit well
    ###
    searchedValue =  hitwell
    tube = df1.filter(like='Tube').columns
    well = df1.filter(like='Well').columns

    ###
    # Each file might has either well or tube, so the program has to check
    # which is the case.
    ###
    if well.empty == True: 
        print('tube and tube number:', searchedValue)
        # df_searchedValue = df1[df1["Tube #"] == searchedValue]
        try:
            df_searchedValue = df1[df1["Tube #"] == int(searchedValue)]
            # print("df_searchedValue \n", df_searchedValue)
        except:
            print("Something went wrong, try something new")
            df_searchedValue = df1[df1["Tube #"] == searchedValue]
            # print("df_searchedValue \n", df_searchedValue)

        df_new = df1.set_index("Tube #", drop = False)
        df_new.astype('str') 
        df_hit_well = df_searchedValue
        # print("df_hit_well \n", df_hit_well)
        # print("type(df_hit_well) =  ", type(df_hit_well.index))
    else: 
        try:
            df_searchedValue = df1[df1["Well #"] == searchedValue]
            df_new = df1.set_index("Well #", drop = False)
            df_hit_well = df_new.loc[[searchedValue]]
            # print("df_hit_well \n", df_hit_well)
            # print("type(df_hit_well) =  ", type(df_hit_well.index))
        except:
            return ([ html.Tr([ html.Td(dcc.Textarea(
                value='An error occurred. Check if the inputs are correct. If there the error persists, please report at:  enquiries@moleculardimensions.com',
                style={'width': '50%'}))]), 0])

    ###
    # Clean empty or nan rows
    ###
    df_hit_well = df_hit_well.replace(r'None', np.nan)
    df_hit_well = df_hit_well.replace(r'-', np.nan)
    df_hit_values = df_hit_well.dropna(axis='columns')

    rows = np.shape(df_hit_values)[0]
    columns = np.shape(df_hit_values)[1]
    ###
    # Concentrations is an array containing the indexes of the 
    # columns which have the "Conc" in the title.
    ###
    concentrations = df_hit_values.filter(like='Conc').columns

    ###
    # convert to dataframe the chosen columns. This way you can share the data with 
    # the between callback and the also print on screen with generate_table function 
    # later on. 
    ###
    kk = dash_table.DataTable(
                                id='table_lhs',
                                data=df_hit_values.to_dict('records'), editable=True,
                                columns=[{"name": i, "id": i} for i in df_hit_values.columns], 
                                # 
                                fixed_columns={ 'headers': True, 'data': 1}, 
                                style_cell = {
                                # all three widths are needed
                                'minWidth': '180hpx', 'width': '100px', 'maxWidth': '180px',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                },style_as_list_view=True,) 
    

    nvars_new = len(concentrations)
    if n_clicks > 0:
        return ([ html.Tr([html.Td(kk)]), nvars_new])


#------------------------------------------------------------------------------
###
# This feature is so the user can change the dimensions of the screen, i.e. the
# number of the wells. Initialises by the the dimensions of a common crystallisation 
# screen 12x8
###
inp_nsamples = html.Tr([
    html.Td('Enter screen dimensions '),
    html.Td(
        dcc.Input(
            id='nsamples_x_lhs', type='number', value=8,
            className="nsamples range")), 
    html.Td(html.Span('x')),
    html.Td(
        dcc.Input(
            id='nsamples_y_lhs', type='number', value=12,
            className="nsamples range"))
])

##############################################################################
btn_compute = html.Div([
    html.Button('compute using LHS', id='btn_compute_lhs', className='action-button', 
        n_clicks = 0),
    html.Div('', id='compute_info_lhs')
])

###
# Creation of dash app: setting up the layout
###
layout = html.Div(
    [
        lhs_layout,
        html.Table([inp_code_hitwell]),
        html.Br(),
        html.Table([btn_submit]),
        html.Br(),
        html.Table([inp_nvars, inp_nsamples]),
        html.Br(),
        btn_compute,
        #graph, hover_info,
    ],
    style={'padding': 20},
    id="container_lhs",
    # tag for iframe resizer
    **{'data-iframe-height': ''},
)
#------------------------------------------------------------------------------


##############################################################################
###
# Using State to share more than one input in the callback. 
# ninps: no of inputs 
###
# ninps = len(label_states + unit_states + low_states + high_states) + 5

ninps = 5 # no of inputs 
states = [State('inp_nvars_lhs', 'value')]
states += [State('nsamples_x_lhs', 'value')]
states += [State('nsamples_y_lhs', 'value')]
states += [State('inp_code_lhs', 'value')]
states += [State('inp_hitwell_lhs', 'value')]
#------------------------------------------------------------------------------


###############################################################################
@app.callback(
    dash.dependencies.Output('compute_info_lhs', 'children'),
    [dash.dependencies.Input('table_lhs', 'data'),
     dash.dependencies.Input('btn_compute_lhs', 'n_clicks'),
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
    
    ###
    # Count how many columns from each category are on the selected file
    ###
    n_pH = len(df_hit_values.filter(like='pH').columns)
    n_units = len(df_hit_values.filter(like='Units').columns)
    n_salts = len(df_hit_values.filter(like='Salt').columns)
    n_buff =  len(df_hit_values.filter(like='Buffer').columns)
    n_precip = len(df_hit_values.filter(like='Precipitant').columns)
    
    ###
    # Only the values of concentration and pH are going to change 
    ###
    concentrations = df_hit_values.filter(like='Conc').columns
    var = df_hit_values[concentrations].to_numpy()
    var = var.T
    var_float = var.astype(np.float)

    pH =  df_hit_values.filter(like='pH').columns
    pH = df_hit_values[pH].to_numpy()
    
    ###
    # In the following lines, the values of the concentration for salt/prec/buffer are assigned. 
    # The format of the file is crucial in order the following to work.
    ###
    salt_conc = var[0:n_salts]
    buff_conc = var[(n_salts):(n_salts+n_buff)]
    precip_conc = var[(n_salts+n_buff):(n_salts+n_buff+n_precip)]

    # VARY RANGE OF CONCERN --- ATTEMPTS TO MAKE THE RANGE CHANGE 
    # low_vals = np.array([args[i + NVARS_MAX] for i in range(nvars)])
    # high_vals = np.array([args[i + 2 * NVARS_MAX] for i in range(nvars)
    # NOTE: check if salt_conc, ph and precip_conc are float arrays. This check is 
    # important, cause after the user will update the number in the table, 
    # the values are parsed as str. 

    pH = pH.astype(float)
    pH = pH.T
    salt_conc = salt_conc.astype(float)
    precip_conc = precip_conc.astype(float)

    salt_range = [salt_conc[:]/2, salt_conc[:]*2]
    pH_range = [pH[:]-1, pH[:]+1]
    precip_range = [precip_conc[:]/4, precip_conc[:]*4]

    low_vals = np.concatenate([salt_range[0], pH_range[0], precip_range[0]])
    high_vals = np.concatenate([salt_range[1], pH_range[1], precip_range[1]])

    nvars = n_salts + n_pH + n_precip
    nsamples = nsamples_x*nsamples_y

    salts_labels = df_hit_values.filter(like='Salt').columns.values
    print('salts_labels',salts_labels)
    buff_labels = df_hit_values.filter(like='Buffer').columns.values
    print('buff_labels',buff_labels)
    perci_labels = df_hit_values.filter(like='Precipitant').columns.values
    print('perci_labels',perci_labels)
    units_labels = df_hit_values.filter(like='Unit').columns.values
    print('unit_labels',units_labels)
   
    reagent_name = np.concatenate([df_hit_values.iloc[0][salts_labels[:]], df_hit_values.iloc[0][buff_labels[:]], df_hit_values.iloc[0][perci_labels[:]] ])
    print('reagent_name', reagent_name)
    reagent_name = reagent_name.tolist()
    reagent_name_1 = reagent_name[0]
    reagent_name_2 = reagent_name[1]

    labels = reagent_name 
    labels_array = np.asarray(labels)
    dim = len(labels_array)
    styling_label_1 = [' ['] * len(labels)
    styling_label_2 = [']'] * len(labels)
    styling_label_1_array = np.asarray(styling_label_1)
    styling_label_2_array = np.asarray(styling_label_2)
    unit_name = np.concatenate([df_hit_values.iloc[0][units_labels[:]]])
    labels_array_new = ["" for x in range(dim)]
    
    ll = 0
    for i in range(dim):
        try: 
            ll = ll+1
            counter = labels_array[i] + styling_label_1[i] + unit_name[i] + styling_label_2[i]
            labels_array_new[ll-1] = counter
        except:
            return dcc.Textarea(
                placeholder='Enter a value...',
                value='An error occurred. Please report at: enquiries@moleculardimensions.com ',
                style={'width': '40%'}
                ) 

    samples = opti_models.compute_LHS(num_samples=nsamples, 
        var_LB=low_vals, 
        var_UB=high_vals)

    df = pd.DataFrame(data=samples, columns=labels_array_new)
    table = generate_table(df, nsamples_x, nsamples_y, download_link=True)
    np.set_printoptions(precision=3)
    if n_clicks > 0:
        return table
    
       
# #------------------------------------------------------------------------------


