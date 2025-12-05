# -*- coding: utf-8 -*-
"""
@author: beyaard
"""
import xarray as xr 
import numpy as np 
import math
import copernicusmarine
from datetime import datetime, timedelta
import os


def normalizedata(data):
    """
    Apply log10 normalization to a dataset and save the result to NetCDF.

    Parameters:
        data (xarray.Dataset or xarray.DataArray): Input data to normalize.
    """
    
    
    normalized=np.log10(data)
    normalized.to_netcdf(r'p:\11210528-foccus\05-Models\WP6\4DVarNet\JupyterNotebook\output\4DVar_toFill.nc')
    
    return ('Normalized data is stored in your catalog!')

def get_tile_slices(dim_len, chunk_size, overlap):
    """
    Compute slicing indices for a dimension to split into overlapping tiles 
    of (even-sized) chunks.

    Parameters:
        dim_len (int): Length of the dimension to slice.
        chunk_size (int): Size of each tile (without overlap).
        overlap (int): Overlap size on each side.

    Returns:
        list of tuple: List of (start, end) index pairs.
    """
    step = chunk_size - overlap
    slices = []
    for start in range(0, dim_len, step):
        end = start + chunk_size
        if end > dim_len:
            end = dim_len
            start = max(end - chunk_size, 0)

        # Add overlap
        start = max(start - overlap, 0)
        end = min(end + overlap, dim_len)

        # Ensure even length
        if (end - start) % 2 != 0:
            if end < dim_len:
                end += 1
            elif start > 0:
                start -= 1
        slices.append((start, end))

        # Stop if the end
        if end == dim_len:
            break
        
        
    return slices

def compute_slices(data,extent_lon,extent_lat,overlap=6):
    """
    Normalize and split dataset into overlapping spatial tiles,
    then save each tile to NetCDF.

    Parameters:
        data (xarray.Dataset): The input dataset.
        extent_lon (int): Width of each tile in longitude.
        extent_lat (int): Height of each tile in latitude.
        overlap (int): Number of overlapping cells (default is 6).
    """
    data=np.log10(data)
    lon_len = data.sizes['longitude']
    lat_len = data.sizes['latitude']
    
    lon_slices = get_tile_slices(lon_len, extent_lon, overlap)
    lat_slices = get_tile_slices(lat_len, extent_lat, overlap)
    
    # tiles = []
    p=0
    for i, (lon_start, lon_end) in enumerate(lon_slices):
        for j, (lat_start, lat_end) in enumerate(lat_slices):
            tile = data.isel(
                longitude=slice(lon_start, lon_end),
                latitude=slice(lat_start, lat_end)
            )
            p=p+1
            tile.to_netcdf(fr'p:\11210528-foccus\05-Models\WP6\4DVarNet\JupyterNotebook\output\CMEMS_{p}.nc')
        
    return('Tiles have been saved in your Catalog!')

#%%GETCMEMSDATASET

def opencmemsdataset(username,password,start_date,end_date,min_lat,max_lat, min_lon, max_lon, timestep,earlierweeknr=5):
    """
    Dowloads SPM data from start to end date, automatically adding nr of earlierweeks before 
    and after the desired start and end date. 
    
    - username: copernicusmarine username
    - password: copernicusmarine password 
    - start_date:(datetime64 or string) yyyy-mm-dd
        Start data dowload. 
    - end_date: (datetime64 or string) yyyy-mm-dd
        End date for data dowload.
    - timestep: 
       'W'= weekly, usual timestep with highest accuracy. 
       'D'= daily, more frequent timestep with lower accuracy. 
    - earlierweeknr: int
        nr of weeks to do before desired start date (so that the at time of interest, 4dvarnet can
        look nr of images ahead)
    
    """
    given_date = datetime.strptime(start_date, '%Y-%m-%d')
    if timestep=='W': 
            earlier_date=given_date - timedelta(weeks=earlierweeknr) #add 5 weeks to the start date
    else:
            earlier_date=given_date - timedelta(days=earlierweeknr) #add 5 days to the start date

    given_date = datetime.strptime(end_date, '%Y-%m-%d')
    if timestep=='W': 
            later_date=given_date + timedelta(weeks=earlierweeknr) #add 5 weeks to the end date
    else: 
            later_date=given_date + timedelta(days=earlierweeknr) #add 5 days to the end date
    
#load dataset of time and area that you want 
    testing= copernicusmarine.open_dataset(username=username,password=password,
        dataset_id = "cmems_obs-oc_atl_bgc-transp_my_l3-multi-1km_P1D",
        minimum_longitude=min_lon,
        maximum_longitude=max_lon,
        minimum_latitude=min_lat,
        maximum_latitude=max_lat,
        start_datetime = earlier_date,
        end_datetime = later_date,
        variables = ['SPM'] 
    )
    if timestep=='W':
        testing = testing.resample(time="1W").mean()
    
    return testing

#%%% compute mask based on CMEMS flags. 

def compute_mask(username, password,start_date, end_date, min_lat, max_lat, min_lon, max_lon, timestep,earlierweeknr=5):
    import copernicusmarine
    given_date = datetime.strptime(start_date, '%Y-%m-%d')
    if timestep=='W': 
            earlier_date=given_date - timedelta(weeks=earlierweeknr) #add 5 weeks to the start date
    else:
            earlier_date=given_date - timedelta(days=earlierweeknr) #add 5 days to the start date

    given_date = datetime.strptime(end_date, '%Y-%m-%d')
    if timestep=='W': 
            later_date=given_date + timedelta(weeks=earlierweeknr) #add 5 weeks to the end date
    else: 
            later_date=given_date + timedelta(days=earlierweeknr) #add 5 days to the end date
    
#load dataset of time and area that you want 
    testing= copernicusmarine.open_dataset(username=username,password=password,
        dataset_id = "cmems_obs-oc_atl_bgc-transp_my_l3-multi-1km_P1D",
        minimum_longitude=min_lon,
        maximum_longitude=max_lon,
        minimum_latitude=min_lat,
        maximum_latitude=max_lat,
        start_datetime = earlier_date,
        end_datetime = later_date,
        variables = ['flags'] 
    )
    testing=(testing['flags'] != 1).any(dim='time') 
    testing = xr.where(testing != 0, testing, np.nan)
    testing.to_netcdf(r'p:\11210528-foccus\05-Models\WP6\4DVarNet\JupyterNotebook\output\mask.nc')
    return ('Mask has been saved to your Catalog!')

def infer_grid(n_tiles):
    """Find (rows, cols) close to square given total number of tiles."""
    factors = []
    for i in range(1, int(math.sqrt(n_tiles)) + 1):
        if n_tiles % i == 0:
            factors.append((i, n_tiles // i))
    # Pick the pair with minimal difference (closest to square)
    rows, cols = min(factors, key=lambda x: abs(x[0] - x[1]))
    return rows, cols

def load_overlap(datapath, total_slices, overlap=4, time_chunks=25):
    """
    Load overlapping tiled datasets and merge with averaging,
    automatically inferring grid shape from total number of slices.
    
    Parameters:
        datapath (str): folder path with tiles
        prefix (str): filename prefix
        suffix (str): filename suffix (e.g. '.nc')
        total_slices (int): total number of tiles
        overlap (int): number of overlapping cells on each side
        time_chunks (int): chunk size for time dimension
        
    Returns:
        xarray.Dataset: merged averaged dataset
    """
    n_rows, n_cols = infer_grid(total_slices)
    print(f"Inferred grid shape: {n_rows} rows x {n_cols} cols")

    file_list = [
        os.path.join(datapath, f'CMEMS_{i}_filled.nc') for i in range(1,total_slices+1)
    ]

    slices = []
    for row in range(n_rows):
        for col in range(n_cols):
            if row == 0:
                yslice = slice(None, -overlap)
            elif row == n_rows - 1:
                yslice = slice(overlap, None)
            else:
                yslice = slice(overlap, -overlap)

            if col == 0:
                xslice = slice(None, -overlap)
            elif col == n_cols - 1:
                xslice = slice(overlap, None)
            else:
                xslice = slice(overlap, -overlap)

            slices.append((yslice, xslice))

    # Check in case total_slices for rounding issues lol
    if len(file_list) != len(slices):
        raise ValueError(f"Mismatch: {len(file_list)} files but {len(slices)} slices")

    datasets = [
        xr.open_dataset(f, chunks={'time': time_chunks}).isel(lat=ys, lon=xs)
        for f, (ys, xs) in zip(file_list, slices)
    ]

    stacked = xr.concat(datasets, dim="tile", join="outer")
    merged = stacked.mean(dim="tile", skipna=True)

    # Rename to SPM instead of something generic
    if isinstance(merged, xr.DataArray):
        merged = merged.rename("__xarray_dataarray_variable__")
        merged = merged.to_dataset(name="SPM")
    else:
        merged = merged.rename({list(merged.data_vars)[0]: "SPM"})

    #Remove the first and last 5 timesteps, which were only to improve performance of the timeframe of interest. These steps perform bad. 
    merged=merged.isel(time=slice(5, -5))
    return merged