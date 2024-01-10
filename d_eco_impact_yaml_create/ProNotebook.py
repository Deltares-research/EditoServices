#%%

import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt
from IPython.display import display
from ipywidgets import interactive, VBox, HTML, interactive, Layout
import yaml

#%%
time_operations={ 'AVERAGE': 1, 'ADD': 2, 'MEDIAN': 3, 'MIN': 4, 'MAX': 5, 'None': 6 }

specie_dictionary={}
#%%
def check_extra_properties(variable):
    
    if variable.lower()=='salinity':
        #create checkbox to allow salinity units conversion
        a=widgets.Checkbox(value=False, description='Convert salinity in PSU units to chloride content in g(Cl)/L',
    disabled=False, indent=False)
        a.layout =Layout(width='400px')  # Set the width to your desired value
        
        display(a)
        return a

    elif variable.lower()=='inundation time':
        explanatory_text = HTML(value="<p3> Choose depth threshold to consider grid cell dry:" )

        #allow to introduce depth threshold to define inundation time
        b= widgets.BoundedFloatText(value=1, min=0, max=5.0,
    step=0.1, description='Depth threshold:', style={'description_width': '200px'}, disabled=False)
        b.layout =Layout(width='400px') 
        display(explanatory_text, b)
        return b
    else:
        return 0


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

def check_dimension(dims):
        
    if dims=='3D':
        description = HTML(value="<p3>Select the depth layer where the physical properties are measured:<p3>")
        display(description)

        layer_widget=widgets.Dropdown(options=[('Bottom', 1), ('Other', 2)],
        value=1, description='Select layer:')
        layer=interactive(get_layer, selected_layer=layer_widget)
        display(layer)

    else:
        #toy function to keep same structure
        def toy(layer):
            lay=widgets.IntText( value=0, description='Any:', disabled=False)
            return lay
        layer_toy= widgets.IntSlider(value=0)
        layer=interactive(toy, layer=layer_toy)

    return layer

def curve(specie, variable, x, y, color='blue', lw=2, grid=True):
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    plt.plot(x, y, lw=lw, color=color)
    ax.grid(grid)
    plt.ylabel('HSI')
    plt.xlabel(variable)
    plt.title('Response curve of the ' + specie+ ' to '+ variable)
    plt.show()  # Display the plot


def on_plot_button_clicked(button, output):
    with output:
        output.clear_output() 
        curve(specie.value, variable_plot.value, x_points.value, y_points.value)

def create_output_dict(variable_plot, variable_name, layer, time_def, time_scale, extra, x_points, y_points):
    if extra.result!=0:
        extra_info=extra.result.value
    else:
        extra_info=None
    
    specie_dictionary[variable_plot]={'model_name': variable_name, 
                                      'layer': layer,
                                      'time_operation':time_def,
                                      'time_scale': time_scale,
                                      'x_values': x_points,
                                      'y_values': y_points, 'extras': extra_info}

def on_write_button_clicked(button):
    with output:
        output.clear_output()  
        create_output_dict(variable_plot.value, variable_name.value,
                            layer.result.result.value, time_def.value, time_scale.value, extra, x_points.value, y_points.value)

def create_yaml_dictionary(input_file, specie_dict, output_file, yaml_file):
    data={'input-data': [{
        'dataset': {
            'filename': input_file, 
            'variable_mapping': 
                 { specie_dict[elem]['model_name']: elem for elem in specie_dict} 
                 } 
                 } ],

        'output-data': {'filename': output_file},

        'rules':  [{ }] }
    
    output_variables=[]
    for elem in specie_dict:
        if specie_dict[elem]['layer']!=0: #3d case
            out1=str(elem)+'_2D'
            new_rule={ 'layer_filter_rule':
                      {
                    'name': 'select layer',
                    'description': 'select layer at which measurement is done',
                    'layer_number': specie_dict[elem]['layer'],
                    'input_variable': elem,
                    'output_variable': out1
                      }}
            data['rules'].append(new_rule)
        else:
            out1=str(elem)+'_2D'
        
        if elem.lower()=='inundation time':
            state=str(out1)+'_State'
            new_rule={ 'formula_rule': {
                'name': specie_dict[elem],
                'description': 'amount of time grid is inundated',
                'formula': f'0 if({out1}<{specie_dict[elem]["extras"]}) else 1',
                'input_variable': out1,
                'output_variable': state}}
            
            data['rules'].append(new_rule)
            out1=state
        
        i=specie_dict[elem]['time_operation']
        for operation, value in time_operations.items():
            if value == i:
                op = operation
                break
            
        if op is not None:
            out2= str(out1)+'_t'
            new_rule={ 'time_aggregation_rule': {
                'name': 'time operation ' + str(elem),
                'description': 'time op',
                'operation': op, 
                'time_scale': specie_dict[elem]['time_scale'],
                'input_variable': out1,
                'output_variable': out2}}
            data['rules'].append(new_rule)
        else:
            out2= str(out1)+'_t'
        
        if elem.lower()=='salinity' and specie_dict[elem]['extras']==True:
            new_rule={ 'formula_rule': {
                'name': str(elem)+' to Chloride',
                'description': ' Converts salinity (psu) to chloride (CL- g/l) for fresh water environments',
                'formula': f'{out2}/0.0018066/1000',
                'input_variable': out2,
                'output_variable':'Chloride'}}
            out2='Chloride'
            data['rules'].append(new_rule)
        
        out3=str(out2)+'_HSI'
        response_rule= {'response_curve_rule': {
             'name': 'HSI' + str(elem),
                'description': 'Mapping to HSI',
                'input_values': specie_dict[elem]['x_values'],
                'output_values': specie_dict[elem]['y_values'],
                'input_variable': out2,
                'output_variable':out3
        }}
        data['rules'].append(response_rule)
        data['rules'].pop(0)
        output_variables.append(out3)

    result = f"100*({'*'.join(str(x) for x in output_variables)})**(1/{len(output_variables)})"
    total= {'response_curve_rule': {
             'name': 'HSI_total',
                'description': 'Mapping total HSI',
                'formula': result, 
                'input_variables': output_variables,
                'output_variable':'Total_HSI'
        }}
    data['rules'].append(total)
    
    classes= {'step_function_rule': {'name': 'HSI classes',
      'description': 'Transforming HSI results into classes',
      'limit_response_table':    
           [ [ 'limit' , 'response'], [-999.0 , 0.00], [   0.0 ,     1.00],
            [  25.0 ,    2.00], [  50.0 ,    3.00], [  75.0 ,    4.00],
            [ 999.0 ,     0.00] ] ,
      'input_variable': 'Total_HSI',
      'output_variable': 'HSI_Classes'
    }}
    data['rules'].append(classes)

    yaml.safe_dump(data, open(yaml_file, 'w'), indent=4)

def on_write_yaml_button_clicked(button):
    with output:
        output.clear_output()  # Clear previous output
        create_yaml_dictionary(input_file.value, specie_dictionary, output_file.value, yaml_file.value)
        
#%%
#Buttons

#specie text box
specie=widgets.Text(value='Pacific Oyster', placeholder='Type something',disabled=False )
specie.layout=Layout(width='200px') 

#variable physical name  text box
variable_plot = widgets.Text( value='Water depth', description='Variable name:', style={'description_width': '200px'} )
variable_plot.layout =Layout(width='400px') 

#variable name in model text box
variable_name = widgets.Text(value='mesh2d_s1', description='Variable ID in Dataset file:', style={'description_width': '200px'} )
variable_name.layout =Layout(width='400px') 

#variable units text box
variable_units = widgets.Text(value='m', description='Variable units:', style={'description_width': '200px'} )
variable_units.layout =Layout(width='400px') 

#show extra widgets for variable properties
extra=interactive(check_extra_properties, variable=variable_plot)

#dimensions button
dimensions=widgets.ToggleButtons(options=['2D', '3D'], description='Variable dimension:', disabled=False)
layer=interactive(check_dimension, dims=dimensions)

#time operations
options = [(operation.capitalize(), value) for operation, value in time_operations.items()]
time_def=widgets.Dropdown(options=options, value=1, description='Select time operation:', style={'description_width': '200px'} )
time_def.layout=Layout(width='400px') 
time_scale=widgets.ToggleButtons(options=['year', 'month'],description='Time-scale of operation to be perfomed:',
    disabled=False, button_style='')


# specify x and y values
x_points = widgets.FloatsInput(description='x', tag_style='info', format = '.2f')
y_points = widgets.FloatsInput(tag_style='success', format = '.2f', description='y')

#trigger the plot
output = widgets.Output()
plot_button = widgets.Button(description='Plot', button_style='success')
plot_button.on_click(lambda button: on_plot_button_clicked(button, output))

#write yaml file button
write_button = widgets.Button(description='Write variable file', button_style='info')
write_button.on_click(on_write_button_clicked)

#Input file text box
input_file=widgets.Text(value='/path/input.nc',placeholder='Type something',description='File:', disabled=False)

#output file text box
output_file=widgets.Text( value='/path/output.nc', placeholder='Type something', description='File:', disabled=False   )

#yaml file text box
yaml_file=widgets.Text(value='rules.yaml', placeholder='Type something', description='File:', disabled=False   )

#create final yaml file
yaml_button = widgets.Button(description='Create final yaml file', button_style='danger')
yaml_button.on_click(on_write_yaml_button_clicked)
#%%
#NOTEBOOK LAYOUT DESIGN

#select specie
heading = HTML( value="<h2>Selecting specie</h2>")
explanatory_text = HTML(value="<p>Write the name of the specie for which you will draw a habitat suitability map.</p>")
display(VBox([heading, explanatory_text, specie]))

#INTRODUCE VARIABLE INFORMATION
heading = HTML(value="<h2>Create response curves</h2>")
explanatory_text = HTML( value="<p3> Choose variable to create response the response curve for the selected specie:" )
display(VBox([heading, explanatory_text, extra, variable_name, variable_units]))

#variable dimension
display(layer)

#variable time operation
display(VBox([time_def, time_scale]))

#specify response curve
explanatory_text = HTML(  value="<br><p>Write x and y coordinates to define the response curves of the specie for the selected variable.</p>"+
'<i> Clicking on [enter] will submit the coordinate ')
x = HTML(value="<p>Values of x <p>")
y = HTML(value="<p>Values of y <p>")

display(VBox([explanatory_text, x, x_points, y, y_points, plot_button, output]))

#write file 
display(write_button)

#D-EcoImpact FILES

#input file
heading = HTML(value="<h2>D-EcoImpact required files</h2>")
description = HTML(value="<p>Write the file path to the input netCDF dataset.</p>")
display(VBox([heading, description, input_file]))

#output file
description = HTML(value="<p>Write the file path to the output netCDF dataset.</p>")
display(VBox([description, output_file]))

#yaml file name
description=HTML(value="<p>Write the chosen name of the yaml file necessary to run D-EcoImpact.</p>")
display(VBox([description, yaml_file]))

#final yaml file 
display(yaml_button)
