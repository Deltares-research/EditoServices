#%%

import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import display
from ipywidgets import interactive, VBox, HTML, Layout
import yaml
#%%

def check_specie(specie):
    #path=''
    if specie=="Pacific Oyster":
        data=yaml.safe_load(open("PacificOyster.yaml"))
    elif specie=="Mussel":
        data=yaml.safe_load(open("Mussel.yaml"))
    return data

def reformat_vars(variables):
    reformated_vars=[]
    for i in variables:
        split_words = i.split("_")
        formatted_string = " ".join(word.capitalize() for word in split_words)
        formatted_string = formatted_string[0].upper() + formatted_string[1:]
        reformated_vars.append(formatted_string)
    return reformated_vars

def create_dictionaries(specie):

    """ 
    Get the input and output variables available in the yaml file
    """
    data=check_specie(specie)

    input_vars=list(data["input-data"][0]["dataset"]["variable_mapping"].values())
    index_hsi_rule = None  # Initialize index_hsi_rule

    for index in range(len(data['rules'])):
        if 'formula_rule' in data['rules'][index].keys():
            if data['rules'][index]['formula_rule']['name']=='total probability':
                index_hsi_rule = index
                break  # Stop the loop once the item is found
    output_vars_hsi=list(data['rules'][index_hsi_rule]['formula_rule']['input_variables'])
    
    #get only variables name
    output_vars=[]
    for name in output_vars_hsi:
        var=name.split("_", 1)[1]
        output_vars.append(var)

    return input_vars, output_vars


def on_update_button_clicked(button, variables_yaml):

    """Update input and output variables in yaml file when button is clicked"""

    # Define the update function
    def update_variables(specie):
        input_vars, output_vars = create_dictionaries(specie)
        return input_vars, output_vars
    
    # Define the interactive widgets
    variables = interactive(update_variables, specie=s.value)
    
    # Update the dictionary values
    variables_yaml["input"] = variables.result[0]
    variables_yaml["output"] = variables.result[1]

def get_layer(selected_layer):

    if selected_layer == 2:
        layer = widgets.IntSlider(value=1,min=1,max=50,step=1,description='Layer:',
            disabled=False, continuous_update=False, orientation='horizontal',
            readout=True, readout_format='d')
        layer.layout = Layout(width='700px')
        layer.style.handle_color = 'lightblue'
        display(layer)

    else:
        layer = widgets.IntSlider(value=1)
    
    return layer

def input_variables(variables): 
    variable_widgets = {}
    units_widgets={}

    variables_names=reformat_vars(variables)

    for i in range(len(variables)):
        label_style = "width: 400px;"  # Adjust the width using CSS style
        label_html = f'<label style="{label_style}"><b>{variables_names[i]}</b> </label>'
        label = widgets.HTML(value=label_html)
        
        variable_name = widgets.Text(value='mesh2d_')
        variable_name.layout=Layout(width='200px')
        dropdown_units = widgets.Text(value='Unitless')
        dropdown_units.layout=Layout(width='200px')

        display(label)
        display(widgets.HBox([variable_name, dropdown_units]))

        variable_widgets[variables[i]] = variable_name
        units_widgets[variables[i]] = dropdown_units.value
    
    units_outputs=dict(units_widgets)

    if units_widgets['Salinity']=='PSU':
        units_outputs['Salinity']='g(Cl)/L' #account for conversion within file
    units_outputs['Inundation_Time']='%'
    units_outputs['Chloride_Concentration']='g(Cl)/L'

    return variable_widgets, units_widgets, units_outputs

def on_update_button_clicked_vars(button, input_boxes_output, variables_yaml, write_yaml_button):
    with input_boxes_output:
        input_boxes_output.clear_output(wait=True)
        
        # Define the update function
        v = input_variables(variables_yaml["input"])
        
        # Update the variables_model dictionary
        variables_model['name_inputs'] = v[0]
        variables_model['units_inputs'] = v[1]  # dictionary
        variables_model['units_outputs'] = v[2]

        display(write_yaml_button)
        

def create_yaml(specie, input_model, output_model, output_file, layer, units, name_inputs):
    data=check_specie(specie)

    data["output-data"]["filename"]= f'"{output_model}"' 
    data["input-data"][0]["dataset"]["filename"]= f'"{input_model}"' 

    # Assuming data is your dictionary
    new_variable_mapping = {}
    for old_key in data["input-data"][0]["dataset"]["variable_mapping"].keys():
        name=data["input-data"][0]["dataset"]["variable_mapping"][old_key]
        new_key = name_inputs[name].value
        new_variable_mapping[new_key] = name

    # Update the original dictionary with the new variable mapping
    data["input-data"][0]["dataset"]["variable_mapping"] = new_variable_mapping
    
    for i, elem in enumerate(data['rules']):
        if elem.keys()== {'layer_filter_rule'}:
            data["rules"][i]['layer_filter_rule']['layer_number']=layer
    
    if units['Salinity']=='g(Cl)/L':
        for i, elem in enumerate(data['rules']):
            if 'formula_rule' in data['rules'][i].keys():
                if data['rules'][i]['formula_rule']['name']=='Salinity to Chloride':
                    data['rules'][i]['formula_rule']['formula']= 'Salinity_2D_avg*1'

    yaml.safe_dump(data, open(output_file, 'w'))


def on_write_button_clicked(button):
  #  with input_boxes_output:
   #     input_boxes_output.clear_output()  # Clear previous output
    create_yaml(s.value, input_file.value, output_file.value,
                    yaml_file.value, layer.result.value, variables_model['units_inputs'], variables_model['name_inputs'])

def plot_functional_curves(specie, variables, units):
    data=check_specie(specie)

    for i, elem in enumerate(data['rules']):
        for j in elem.values():
            name=j['name'].replace("HSI ", "").replace("_", " ")
            for i in range(len(variables)):
                if name==variables[i]:
                    x=j['input_values']
                    y=j['output_values']

                    fig, ax = plt.subplots(1, 1, figsize=(6, 4)) 
                    ax.plot(x, y, color='dodgerblue')
                    ax.plot(x, y, color='dodgerblue')
                    ax.set_xlabel(f'{variables[i]} [{units[i]}]')
                    ax.set_ylabel('HSI')
                    ax.set_title(f'Functional curve of {variables[i]} for {specie}')
                    plt.show()

def on_plot_button_clicked_plotting(button, variable_plot, output):
    #with output:
     #   output.clear_output()  # Clear previous output
    plot_functional_curves(s.value, variable_plot.value, list(variables_model['units_outputs'].values()))

def get_variable(output_vars):
    output_names=reformat_vars(output_vars)

    vars = widgets.TagsInput(allowed_tags=output_names, allow_duplicates=False)
    vars.layout.width = '400px'  
    display(vars)
    return vars

def plotting_func(flag):
    if flag==True:
        text = "<p3>Choose for which physical variables their corresponding response or functional curves are displayed:<p3>"+"<br><i>Click on the default box to see other options.</i>"
        description = HTML(value=text)
        display(VBox([description]))

        variable_plot=get_variable(variables_yaml['output'])

        #plotting button
        output = widgets.Output()
        plot_button = widgets.Button(description='Plot', button_style='success')
        plot_button.on_click(lambda button: on_plot_button_clicked_plotting(flag, variable_plot, output) )

        display(plot_button)

#%% 
# Create a dictionary to store variable names
variables_yaml = { "input": ['Salinity'], "output": []}

# Create a dictionary to store the information of the variables
variables_model={ 'name_inputs': [], 'units_inputs': [], 'units_outputs': []}


#%%
"""DEFINITION OF BUTTONS"""

# Specie 
s=widgets.RadioButtons(options=['Pacific Oyster', 'Mussel'],disabled=False)
# Define the update button for specie
update_button_specie = widgets.Button(description="Load information", button_style='success')
# Attach the function to the button's click event
update_button_specie.on_click(lambda button: on_update_button_clicked(button, variables_yaml))

# Depth layer dropdown
layer_widget=widgets.Dropdown(options=[('Bottom', 1), ('Other', 2)], value=1, description='Select layer:')
layer=interactive(get_layer, selected_layer=layer_widget)

#Input file text box
input_file=widgets.Text(value='/path/input.nc',placeholder='Type something',description='File:', disabled=False)

#output file text box
output_file=widgets.Text( value='/path/output.nc', placeholder='Type something', description='File:', disabled=False   )

#yaml file text box
yaml_file=widgets.Text(value='rules.yaml', placeholder='Type something', description='File:', disabled=False   )

#load variables button
input_boxes_output = widgets.Output()
update_button_variables = widgets.Button(description="Load available variables", button_style='success')
update_button_variables.layout =Layout(width='300px')

#create yaml file button
write_button = widgets.Button(description='Create yaml file', button_style='info')
write_button.on_click(on_write_button_clicked)

update_button_variables.on_click(lambda button: on_update_button_clicked_vars(button,  input_boxes_output, variables_yaml, write_button))

#plotting checkbox
plotting=widgets.ToggleButton(value=False, description='Plot response curves', disabled=False,
    button_style='', tooltip='Description', icon='check' )
plotting.layout =Layout(width='300px')
plot_flag=interactive(plotting_func, flag=plotting)

#%%
"""DESIGN OF INTERFACE"""

#1.  SPECIES SELECTION
heading = HTML(value="<h2> Selecting variables</h2>")
description = HTML(value= "<p3>Select an available specie to create its habitat suitability map:<p3>")
# Display the combined widget
display( VBox([heading, description, s, update_button_specie]))

#2. LAYER SELECTION
description = HTML(value="<p3>Select the depth layer where the physical properties are measured:<p3>")
display(VBox([description, layer]))

#3. D-EcoImpact FILES

#input file
heading = HTML(value="<h2>D-EcoImpact required files</h2>")
description = HTML(value="<p>Write the file path to the input netCDF dataset.</p>")
display(VBox([heading, description, input_file]))

#output file
description = HTML(value="<p>Write the file path to the output netCDF dataset.</p>")
display(VBox([description, output_file]))

#yaml file
description=HTML(value="<p>Write the chosen name of the yaml file necessary to run D-EcoImpact.</p>")
display(VBox([description, yaml_file]))

#4. DEFINE VARIABLE NAMES IN DATASET
description = HTML(value="<p><br> Write the name of each variable as defined in the input Dataset and its units.</p> "+"<i>If salinity units are in PSU, results will be converted to chloride concentration in g(Cl)/L.</i>")
display(VBox([update_button_variables, input_boxes_output]))

#5. PLOTTING
display(plot_flag)

# %%
