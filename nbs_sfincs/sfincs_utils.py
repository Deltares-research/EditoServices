from hydromt_sfincs import SfincsModel

def sfincs_mod_read_h(dir_sfincs_model, hmin=0.05, apply_hmin=False):
    mod = SfincsModel(dir_sfincs_model, mode="r")
    mod.read_results(chunksize=10)
    da_h = mod.results["h"]
    if apply_hmin:
        da_h = da_h.where(da_h > hmin)
    da_h.attrs.update(long_name="flood depth", unit="m")
    return da_h

def load_hmax_noveg(dir_noveg, dir_veg, hmin=0.05):
    da_h_noveg = sfincs_mod_read_h(dir_noveg, hmin)
    da_h_veg   = sfincs_mod_read_h(dir_veg, hmin)
    da_dif = da_h_veg - da_h_noveg
    mod = SfincsModel(dir_noveg, mode="r")
    return da_dif, da_h_noveg, mod

def load_h_his(dir_noveg, dir_veg, station_id=0):
    mod_noveg = SfincsModel(dir_noveg, mode="r")
    mod_veg   = SfincsModel(dir_veg, mode="r")
    h_noveg = mod_noveg.results['point_h'].isel(stations=station_id)
    h_veg   = mod_veg.results['point_h'].isel(stations=station_id)
    return h_noveg, h_veg
