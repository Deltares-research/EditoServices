# -*- coding: utf-8 -*-
"""
This script tests the 4DVarNet-dLSTM model on patch/clouded data. 

Adapted from Mistrangelo, F (2024), see https://essay.utwente.nl/104608/. 

@author: L. Beyaard, Deltares, 2025 

"""
import sys
print(sys.executable)

import xarray as xr
import numpy as np
import torch
import torch.utils.data
import functools as ft
from tqdm import tqdm
import torch.nn.functional as F
import torch.optim as optim
import time
import datamodule as dmod
from datamodule import compute_rmse, compute_re
from model_AE_Bilin3D import model_AE as model_AE_3D
from iter_solver2 import Model_4DVarNN_GradFP


def testing_4dvarnet(datapath,modelpath, slicenr, savename='_filled'):
    '''
    Tests pre-tained 4dVarNet model on high resolution data, in 25 slices. 
    
    
    Parameters
    ----------
    datapath : str
        path to folder where .nc files of cld data are stored.
    startname : str
        Consistent name of cld files before the nr identifyer. 
    endname : str
        Consistent name of cld files after the nr identifyer.
    slicenr : int
        Number of slices 
    modelpath : str
        Directory to save the gap-filled outcome
    savename : str
        Name of filled .nc after nr identifyer. 

    Returns
    -------
    .nc
    gapfilled netcdf, with 10log(SPM), not masked. 

    '''

    for i in range(1,slicenr+1):
        torch.cuda.empty_cache()
        data_surf = xr.open_dataset(datapath+'CMEMS_'+str(i)+'.nc').rename({'latitude': 'lat', 'longitude': 'lon'})       
    
        batch_size=2 #batch size 
        nr=10
        DimAE = 64
        downsamp = 2
        DimState = [96,96] #
        num_epochs  = 50
        
        input_da = dmod.load_bbp_data(GT=data_surf, patch=data_surf)
        times=data_surf.time.data
        
        # Configuration parameters from base.yaml  
        config = {
            'input_da': input_da,
            'domains': {                    ## The only important parameter is the test dataset period
                'train': {'time': times},   ## but the time train and validation datasets period need to be in the 
                'val': {'time': times},     ## range of the dataset
                'test': {'time': times}   
            },
            'xrds_kw': {
                'patch_dims': {'time': nr, 'lat': len(data_surf.lat.data), 'lon': len(data_surf.lon.data)},
                'strides': {'nr': 1, 'lat': len(data_surf.lat.data), 'lon': len(data_surf.lon.data)}
            },
            'dl_kw': {'batch_size': batch_size, 'num_workers': 1},
            'aug_factor': 1,
            'aug_only': True
        }
        
        # Instantiate the DataModule with the configuration
        data_module = dmod.BaseDataModule(**config)
        
        ## Hyperparamters for the AE
        dim_in = config['xrds_kw']['patch_dims']['time']
        bilin_quad = False
        total_RAM = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        ## Load the AE model
        ModelAE = model_AE_3D(dim_in = 1, DimAE = DimAE, downsamp = downsamp, bilin_quad = bilin_quad)
        
        ## Saving the hyperparameters values
        hyperparam = f"time window: {dim_in} \nhidden layer dimension: {DimAE} \ndownsampling: {downsamp} \nbatch size: {config['dl_kw']['batch_size']} \nRAM memory: {total_RAM} GB"
        
        #with open("output_test.txt", "w") as file:
         #   file.write(hyperparam)
          #  file.write(f"\nbilin quad: {bilin_quad}")
        
        ## number of parameters
        model_AE_param = f"\nnumber of parameters of the AE model: {sum(p.numel() for p in ModelAE.parameters() if p.requires_grad)}"
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        ModelAE = ModelAE.to(device)
        dev = "GPU" if torch.cuda.is_available() else "CPU"
        dev_used = f"\nDevice used: {dev}"
        
      #  with open("output_test.txt", "a") as file:
       #     file.write(model_AE_param)
        #    file.write(dev_used)
        
        ##############################################################################################
        #setup the data module
        data_module.setup()
        
        meanTr, stdTr = data_module.norm_stats()
        
        # Create the Dataloaders
        test_dataloader = data_module.test_dataloader()
        
        # Accessing the datasets
        test_ds  = data_module.masked_test_ds()
        
        ## create the dataloader
        dataloaders = {
            'test': test_dataloader
        }
        
        
        
        ##############################################################################################
        
        ## MODEL LEARNING
        
        UsePriodicBoundary = True 
        InterpFlag         = False
        
        tr_loss_list =[]
        val_loss_list = []
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        patch_size = dim_in
        batch_size = config['dl_kw']['batch_size']
        lat = data_surf['lat']
        lon = data_surf['lon']
        shapeData = np.array((batch_size, patch_size, len(lat), len(lon)))
        DimState = DimState
        
        alpha          = np.array([1.,0.1])
        
        IterUpdate     = [0,100,200,500,2000,1000,1200]
        NbProjection   = [0,0,0,0,0,0,0]
        NbGradIter     = [15,15]
        lrUpdate       = [1e-3,1e-4,1e-4,1e-5,1e-5,1e-4,1e-5,1e-6,1e-7]
        
        NBGradCurrent   = NbGradIter[0]
        NBProjCurrent   = NbProjection[0]
        lrCurrent       = lrUpdate[0]
        
        model           = Model_4DVarNN_GradFP(ModelAE,shapeData,DimState,NBProjCurrent,NBGradCurrent,UsePriodicBoundary)
        model.load_state_dict(torch.load(modelpath))    ## Loading the pretrain model (put the correct path to the model)
        model           = model.to(device)
        
        
        full_model_param = f"\n4DVar model: Number of trainable parameters = {(sum(p.numel() for p in model.parameters() if p.requires_grad))}"
        
        #with open("output_test.txt", "a") as file:
         #   file.write(f"\nnumber of gradient iterations: {NbGradIter[0]} \nhidden layer dimension: {model.model_Grad.DimState} " )
          #  file.write(full_model_param)
           # file.write("\n")
        
        
        
        #### MAIN LOOP
        alpha4DVar = np.array([0.01,0.99])
        y_eval = [] 
        y_test  = [] 
        
        for phase in ['test']:
          since = time.time()
        
          model.eval()
        
          running_loss         = 0.
          running_loss_All     = 0.
          running_loss_AE      = 0.
          running_KL_loss_all  = 0.
          num_loss             = 0
          RMSE = 0.
          RE = 0.
        #   kl_loss = torch.nn.KLDivLoss(reduction="batchmean", log_target=True)
        
          for state, target in tqdm(dataloaders[phase]):
              masks  = torch.isnan(state).float()
              state  = torch.nan_to_num(state)
              target = torch.nan_to_num(target)
        
              state      = state.to(device)
              masks      = masks.to(device)
              target     = target.to(device)
        
        
              with torch.set_grad_enabled(True):
                state = torch.autograd.Variable(state, requires_grad = True)
        
                outputs, hidden_new, new, _ = model(device, state, target, (1. - masks), None, None)
                if phase == 'eval':
                  y_eval.append(outputs.cpu().detach().numpy().squeeze()*stdTr + meanTr)
                else:
                  y_test.append(outputs.cpu().detach().numpy()*stdTr + meanTr)
              
              del state, outputs, masks, target, hidden_new, new
        
              torch.cuda.empty_cache() ## clear the memory
              
        
        time_elapsed = time.time() - since
        
       # with open("output_test.txt", "a") as file:
        #    file.write( '\nTesting complete in {:.0f}m {:.0f}s'.format(time_elapsed // 60, time_elapsed % 60) )
        
        y_test_sat = np.concatenate(y_test, axis = 0)
        
        test_pred = test_ds.reconstruct(y_test_sat)          ## Converting the dataset from the patches
        
        test_pred.to_netcdf(datapath+'CMEMS_'+ str(i)+savename+'.nc') ## Saving the resonstructed dataset in your path
        (print(f'Gap-filled on slice nr {i}'))