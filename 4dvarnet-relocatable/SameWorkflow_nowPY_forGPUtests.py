# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 13:28:25 2025

@author: beyaard
"""
#%%
import testing as ts 
import FunctionFile as ff
import os
import xarray as xr

##%for me, removed later
import numpy as np
import matplotlib.pyplot as plt

username = 'lbeyaard'
password = 'Deltares@Copernicus24'

print('Everything loaded correctly')

#%%
#define minimum and maximum spatial domain 
#SMALL DOMAIN TEST! 
min_lat, max_lat= 52.9 , 53.42   #minimum and maximum latitude 
min_lon, max_lon= 4.58, 6.51     #minimum and maximum longitude

#FOR ME! WHEN TESTING LARGER DOMAIN THAT NEEDS SLICING  => REMOVE LATER
min_lat, max_lat= 45.0 , 53.42
min_lon, max_lon= -10.58, 5.51   

#define first and last day of timeframe, and timestep (W=weekly, D=daily). Daily is higher computational costs and lower accuracy 
start_day='2024-01-01'  #yyyy-mm-dd
end_day= '2024-02-01'   #yyyy-mm-dd 
timestep='W' #or 'D', higher computational costs and lower accuracy 

#retrieve cmems satellite data 
data=ff.opencmemsdataset(username, password,start_day, end_day, min_lat, max_lat, min_lon, max_lon, timestep) 

print(data)
plt.pcolormesh(data['SPM'][1])
#the time will automatically be 5 weeks/days earlier and later than what you have given. This is so that the algorithm has enough data at the dates of interest.

#%%
#check the spatial extend of the data 
extent_lon=306
extent_lat=406

#normalize the data
if len(data.latitude) > extent_lat or len(data.longitude) > extent_lon:
    print("Warning: Dataset dimensions exceed maximum size, it will be sliced!")
    norm_data=ff.compute_slices(data,extent_lon,extent_lat)

else: 
    norm_data=ff.normalizedata(data)

#%%
#generate the land mask 
mask=ff.compute_mask(username, password,start_day, end_day, min_lat, max_lat, min_lon, max_lon, timestep)

#%%
#retrieve the nr of slices 
folder_path = r'../../../../05-Models/WP6/4DVarNet/JupyterNotebook/output/'  # ← Replace with edito catalog path or smth?

slicenr = sum(
    1 for entry in os.scandir(folder_path)
    if entry.is_file() and entry.name.startswith('mask') and entry.name.endswith('.nc')
)
print(f'Gap-filling {slicenr} slice(s)')

#run these slices through the testing script
## curent only works on a gpu with cuda thingss  
gap_filled=ts.testing_4dvarnet(folder_path,r'../../../../05-Models/WP6/4DVarNet/JupyterNotebook/pre_trained_model.pt',slicenr) 

#%%
#load the mask 
mask=xr.open_dataset(folder_path+'mask.nc')
print('Mask specifics: 'mask)

#%%merge the data back together 
filled=ff.load_overlap(folder_path,slicenr)
#de-normalize the data 
filled['SPM'] = (10 ** filled['SPM'])*mask['flags'].data

print('Gap-filled specifics: 'filled)


#%%
# find cbar limits
vmin = np.nanmin([data['SPM'][0].min(), filled['SPM'][0].min()])
vmax = np.nanmax([data['SPM'][0].max(), filled['SPM'][0].max()])

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

# Left plot: Satellite data
mesh0 = axes[0].pcolormesh(
    data['longitude'],
    data['latitude'],
    data['SPM'][0],
    shading='auto',
    vmin=vmin,
    vmax=vmax
)
axes[0].set_title('CMEMS Observation')
axes[0].set_xlabel('lon')
axes[0].set_ylabel('lat')
fig.colorbar(mesh0, ax=axes[0], label='SPM [mg/l]')

# Right plot: Filled data
mesh1 = axes[1].pcolormesh(
    filled['lon'],
    filled['lat'],
    filled['SPM'][0],
    shading='auto',
    vmin=vmin,
    vmax=vmax
)
axes[1].set_title("Gap-Filled Dataset")
axes[1].set_xlabel('lon')
axes[1].set_ylabel('lat')
fig.colorbar(mesh1, ax=axes[1], label='SPM [mg/l]')
plt.suptitle(str(filled['time'][0].data)[:10])
plt.tight_layout()
plt.show()

#%%
filled.to_netcdf(r'p:\11210528-foccus\05-Models\WP6\4DVarNet\JupyterNotebook\output\CMEMS_gapfilled.nc')