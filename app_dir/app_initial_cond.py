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
#from . import uniform
from . import maxmin
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

reagents = collections.OrderedDict([
    ('reagent_1', dict(label='Reagent 1', unitslabel='[Units 1]', range=[100.0, 200.0])),
    ('reagent_2', dict(label='Reagent 2', unitslabel='[Units 2]', range=[1.0, 6.0]))])

NVARS_DEFAULT = len(reagents)


# Fill up to NVARS_MAX (needed to define callbacks)
NVARS_MAX = 10
for i in range(len(reagents), NVARS_MAX):
    k = 'Reagent {}'.format(i + 1)
    l = '[Units {}]'.format(i + 1)
    reagents[k] = dict(label=k,  unitslabel=l, range=[0, 1])

var_ids = list(reagents.keys())
print('var_ids', var_ids )

controls_dict = collections.OrderedDict()
for k, v in list(reagents.items()):
    controls = get_controls_var(k, v['label'], v['unitslabel'], v['range'])
    print("controls (l.104): \n",type(controls))
    controls_dict[k] = controls


head_row = html.Tr([
    html.Th('Reagent   '),
    html.Th('[Units]  '),
    html.Th('Range  ')
])

controls_html = html.Table(
    [head_row] + list(controls_dict.values()), id='controls')
label_states = [State(k + "_label", 'value') for k in var_ids
]
unit_states = [State(l + "_label", 'value') for l in var_ids
]
low_states = [State(k + "_low", 'value') for k in var_ids]
high_states = [State(k + "_high", 'value') for k in var_ids]
# weight_states = [
#     dash.dependencies.State(k + "_weight", 'value') for k in var_ids
# ]

inp_nvars = html.Tr([
    html.Td('Number of reagents: '),
    html.Td(
        dcc.Input(
            id='inp_nvars',
            type='number',
            value=NVARS_DEFAULT,
            max=NVARS_MAX,
            min=1,
            className="nvars range"))
])



inp_code_hitwell = html.Tr([
    html.Td('Enter screen code (e.g. MD1-40) and hit well (e.g. B1):'),
    html.Td(dcc.Input(id='inp_code',
            type='text', 
            value="MD1-40")),
    html.Td(dcc.Input(
            id='inp_hitwell',
            type='text', 
            value="B1")),
    html.Div('', id='input_info')])

btn_submit = html.Tr([html.Td(html.Button('Submit', id = 'submit-button', className='action-button', n_clicks=0)),
    html.Div('', id='submit_info')
    ])

##############################################################################
print("label_states, type(label_states)", label_states, type(label_states))
states = [State('inp_code', 'value')]
states += [State('inp_hitwell', 'value')]


@app.callback(
    [Output('submit_info', 'children'),
     Output('inp_nvars', 'value'),
     Output('reagent_1_label', 'value')],
    [Input('submit-button', 'n_clicks')],
    states)
def update_output_code_hitwell(n_clicks, *args):
    hitwell = args[-1]
    code_name = args[-2]


    code_name = code_name + "*"
    for file in os.listdir(myPath):
        if fnmatch.fnmatch(file, code_name):
            print ("The file you called is: \n", file)
            file_found = file 
            newpath = os.path.join(myPath, file_found)
            xls = pd.ExcelFile(newpath)
            df1 = pd.read_excel(xls)
            searchedValue =  hitwell
            df_searchedValue = df1[df1["Well #"] == searchedValue]
            df_new = df1.set_index("Well #", drop = False)
            df_hit_well = df_new.loc[[searchedValue]]
            df_hit_values = df_hit_well.dropna(axis='columns')
    rows = np.shape(df_hit_values)[0]
    columns = np.shape(df_hit_values)[1]
    concentrations = df_hit_values.filter(like='Conc').columns


    v_index = df_hit_values.index.values
    print("v_index", v_index)
    salts_labels = df_hit_values.filter(like='Salt').columns.values
    print("type of salts_labels: \n",salts_labels[0])
    print('Test if the correct cell is chosen',df_hit_values.iloc[0][salts_labels[0]])

    # reagent_name = df_hit_values.iloc[0][salts_labels[:]]

    reagent_name = df_hit_values.iloc[0][salts_labels[0]]

    table_test = generate_table(df_hit_values, download_link=False)
    kk = dash_table.DataTable(
                                id='table',
                                data=df_hit_values.to_dict('records'), editable=True,
                                columns=[{"name": i, "id": i} for i in df_hit_values.columns], 
                                # fixed_columns={ 'headers': True, 'data': 1}, 
                                style_cell = {
                                # all three widths are needed
                                'minWidth': '180hpx', 'width': '100px', 'maxWidth': '180px',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                },style_as_list_view=True,) 
    

    nvars_new = len(concentrations)
    if n_clicks > 0:
        return ([ html.Tr([html.Td(kk)]), nvars_new, reagent_name])
#------------------------------------------------------------------------------

inp_nsamples = html.Tr([
    html.Td('Enter screen dimensions '),
    html.Td(
        dcc.Input(
            id='nsamples_x', type='number', value=8,
            className="nsamples range")), 
    html.Td(html.Span('x')),
    html.Td(
        dcc.Input(
            id='nsamples_y', type='number', value=12,
            className="nsamples range"))
])



ninps = len(label_states + unit_states + low_states + high_states) + 5
print("ninps = ", ninps)

#------------------------------------------------------------------------------


##############################################################################

btn_compute = html.Div([
    html.Button('compute using LHS', id='btn_compute', className='action-button', 
        n_clicks_timestamp = 0),
    html.Button('compute using grid', id='btn_compute_2', className='action-button', 
        n_clicks_timestamp = 0),
    html.Div('', id='compute_info')
])

# Creation of dash app

layout = html.Div(
    [
        html.Table([inp_code_hitwell]),
        html.Table([btn_submit]),
        html.Table([inp_nvars, inp_nsamples]),
        # html.Table([btn_submit]),
        controls_html,
        btn_compute,
        #graph, hover_info,
    ],
    id="container",
    # tag for iframe resizer
    **{'data-iframe-height': ''},
)
#------------------------------------------------------------------------------



##############################################################################
# Callbacks to hide unselected reagents
for i in range(NVARS_MAX):

    @app.callback(
        dash.dependencies.Output(var_ids[i] + "_tr", 'style'),
        [dash.dependencies.Input('inp_nvars', 'value')])
    def toggle_visibility(nvars, i=i):
        """Callback for setting variable visibility"""
        style = {}

        if i + 1 > nvars:
            style['display'] = 'none'

        return style
#------------------------------------------------------------------------------



##############################################################################
print("label_states, type(label_states)", label_states, type(label_states))
states = label_states + unit_states + low_states + high_states 

states += [State('inp_nvars', 'value')]
states += [State('nsamples_x', 'value')]
states += [State('nsamples_y', 'value')]
states += [State('inp_code', 'value')]
states += [State('inp_hitwell', 'value')]


#------------------------------------------------------------------------------

##############################################################################


@app.callback(
    dash.dependencies.Output('compute_info', 'children'),
    [dash.dependencies.Input('table', 'data'),
     dash.dependencies.Input('btn_compute', 'n_clicks_timestamp'), 
     dash.dependencies.Input('btn_compute_2', 'n_clicks_timestamp'),
     ], states)

def on_compute(submit_info, btn_compute, btn_compute_2, *args):
    """Callback for clicking compute button"""
    # if n_clicks is None :
    #     return ''

    print('testing:', type(submit_info))
    df_hit_values = pd.DataFrame(submit_info)
    print("testing conversion from DATATABLE to DATAFRAME:\n", df_hit_values)
    print("len(args) = ", len(args) )
    if len(args) != ninps:
        raise ValueError("Expected {} arguments".format(ninps))

    # parse arguments
    hitwell = args[-1]
    code_name = args[-2]
    nsamples_y = args[-3]
    nsamples_x = args[-4]
    nvars = args[-5]
    concentrations = df_hit_values.filter(like='Conc').columns
    print("concentrations", concentrations)
    ph =  df_hit_values.filter(like='pH').columns
    units = df_hit_values.filter(like='Units').columns
    salts = df_hit_values.filter(like='Salt').columns
    buff =  df_hit_values.filter(like='Buffer').columns
    precip =  df_hit_values.filter(like='Precipitant').columns
    var = df_hit_values[concentrations].to_numpy()
    var = var.T
    var_float = var.astype(np.float)
    print(var_float)

    nsamples = nsamples_x*nsamples_y
    labels = args[:nvars]


    # low_vals = np.array([args[i + NVARS_MAX] for i in range(nvars)])
    # high_vals = np.array([args[i + 2 * NVARS_MAX] for i in range(nvars)])
    low_vals = ([var_float[0] - 0.01, var_float[1] - 0.1])
    high_vals = ([var_float[0] + 0.1, var_float[1] + 0.1])
    print ("NVARS_MAX = ", NVARS_MAX)
    print ("low_vals = ", low_vals)
    print ("high_vals = ", high_vals)

    # print("int(btn_compute) = ", int(btn_compute))


    if int(btn_compute) > int(btn_compute_2):

        samples = maxmin.compute_LHS(num_samples=nsamples, 
            var_LB=low_vals, 
            var_UB=high_vals)
        print (samples)
        df = pd.DataFrame(data=samples, columns=labels)
        table = generate_table(df, download_link=True)
        return table
    elif int(btn_compute_2) > int(btn_compute):
        
        samples_1 = maxmin.compute_grid(nsamples_x, nsamples_y, low_vals, high_vals, 
            NVARS = len(low_vals))
        df = pd.DataFrame(data=samples_1, columns=labels)
        # print ("samples_1 (l 249) = \n", samples_1)
        table = generate_table(df, download_link=True)
        return table
#------------------------------------------------------------------------------


