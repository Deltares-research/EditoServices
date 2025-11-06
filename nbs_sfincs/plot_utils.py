import os
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.img_tiles import GoogleTiles
from matplotlib.ticker import FuncFormatter
from os.path import join
import xarray as xr
import datetime
import matplotlib.dates as mdates

def numfmt(x, pos):
    return f"{x / 1000.0:.0f}"

def plot_h_dif_snapshot(
    da_h_noveg,
    da_h_dif,
    his_noveg,
    t,
    out_dir,
    zoomlevel=10,
    hmin=0.05,
    fs_ticks=9
):
    utm_zone = da_h_dif.raster.crs.to_wkt().split("UTM zone ")[1][:3]
    extent = np.array(da_h_dif.raster.box.buffer(1e2).total_bounds)[[0, 2, 1, 3]]
    crs = ccrs.UTM(int(utm_zone[:2]))
    fig, axs = plt.subplots(1, 2, subplot_kw={'projection': crs}, figsize=(8, 4))

    for ax in axs:
        ax.set_extent(extent, crs=crs)
        ax.add_image(GoogleTiles(style='satellite'), zoomlevel)

    ax1, ax2 = axs

    da_plot1 = da_h_noveg.sel(time=t)
    da_plot1.plot(
        x="xc", y="yc", ax=ax1, vmin=0, vmax=2, cmap=plt.cm.Spectral, alpha=0.8,
        cbar_kwargs={"shrink": 0.8, "orientation": 'horizontal', "label": 'Flood depth [m +MSL]'}
    )

    da_plot2 = da_h_dif.sel(time=t)
    da_plot2.plot(
        x="xc", y="yc", ax=ax2, vmin=-0.5, vmax=0.5, cmap=plt.cm.bwr, alpha=0.8,
        cbar_kwargs={"shrink": 0.8, "orientation": 'horizontal', "label": 'Δ Flood depth [m]'}
    )

    ax1.scatter(his_noveg.station_x.values, his_noveg.station_y.values, color='white', s=5, marker='*', zorder=5)

    datesuffix = str(np.datetime64(t.time.values, 'm')).replace('-', '')
    date_title = datetime.datetime.strptime(datesuffix, "%Y%m%dT%H:%M").strftime("%d-%m-%Y %H:%M")
    utm_suffix = da_h_dif.raster.crs.name.split('/')[1]

    for i, ax in enumerate([ax1, ax2]):
        ax.set_xlabel(f'X-coordinate [km] {utm_suffix}', fontsize=fs_ticks)
        ax.set_ylabel('Y-coordinate [km] ' + utm_suffix if i == 0 else '', fontsize=fs_ticks)
        ax.xaxis.set_major_formatter(FuncFormatter(numfmt))
        ax.yaxis.set_major_formatter(FuncFormatter(numfmt))
        ax.tick_params(axis="both", direction='out', length=3, labelsize=fs_ticks)
        ax.set_title(date_title)

    fig.savefig(join(out_dir, f"{datesuffix}_h_dif.png"), dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_snapshots_every_nth(
    da_h_noveg,
    da_h_dif,
    his_noveg,
    out_dir,
    n=10,
    zoomlevel=10,
    hmin=0.05,
    fs_ticks=9
):
    """
    Plots every n-th time step using plot_h_dif_snapshot and saves PNGs.
    """
    print(f"📸 Plotting snapshots every {n}th timestep...")

    for i, t in enumerate(da_h_dif.time[::n]):
        print(f"  ⏱️  Snapshot {i+1}/{len(da_h_dif.time[::n])}: {str(np.datetime64(t.values, 'm'))}")
        plot_h_dif_snapshot(
            da_h_noveg=da_h_noveg,
            da_h_dif=da_h_dif,
            his_noveg=his_noveg,
            t=t,
            out_dir=out_dir,
            zoomlevel=zoomlevel,
            hmin=hmin,
            fs_ticks=fs_ticks
        )
    
    print("✅ Snapshots saved.")

# Set your global, smaller figure size once
FIGSIZE = (4, 2.5)   # width, height in inches — change as you like (e.g., (4,2.5))

def plot_waterlevel_forcing(input_path, output_path):
    """
    Plot water level forcing at all stations from wl_ts.nc and save as PNG.
    """
    import matplotlib.pyplot as plt
    import xarray as xr
    from IPython.display import display, Image as IPImage
    from os.path import join

    print("📊 Plotting water level forcing...")

    da_wl = xr.open_dataset(join(input_path, 'wl_ts.nc'))
    fig, ax = plt.subplots(1, 1, figsize=FIGSIZE, layout="constrained")

    for idx in da_wl.stations.values:
        da_wl.sel(stations=idx)['waterlevel'].plot(label=idx+1, ax=ax)

    ax.set_title('')
    ax.set_ylabel('Water level [m +MSL]')
    ax.axhline(y=0, color='darkgrey', ls='--')
    ax.legend(ncol=4, fontsize=8)  # smaller legend to match reduced figure

    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"✅ Saved: {output_path}")
    try:
        display(IPImage(output_path))
    except:
        pass


def plot_observed_h_difference(his_noveg, his_veg, output_path):
    """
    Plot h time series with and without vegetation + difference plot.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from IPython.display import display, Image as IPImage

    print("📉 Plotting time series difference...")

    # Same figure size as the other function
    fig, axs = plt.subplots(2, 1, figsize=FIGSIZE, layout="constrained", sharex=True)

    ax = axs[0]
    t = his_noveg['time']
    z = his_noveg.values
    z_veg = his_veg.values
    elapsed_hours = (t.values - t.values[0]) / np.timedelta64(1, 'h')

    ax.plot(elapsed_hours, z, label='noveg')
    ax.plot(elapsed_hours, z_veg, label='veg')
    ax.set_xticklabels([])
    ax.set_ylabel('Water depth [m]')
    ax.legend(fontsize=8)

    ax = axs[1]
    delta = z_veg - z
    ax.plot(elapsed_hours, delta)
    ax.set_xlabel('Hours since start')
    ax.set_ylabel('Water depth\ndifference [m]')
    ax.set_ylim(-0.5, 0.5)
    ax.text(0.55, 0.2, 'reduction due to veg', transform=ax.transAxes, fontsize=8)
    ax.text(0.55, 0.7, 'increase due to veg', transform=ax.transAxes, fontsize=8)
    ax.axhline(0, ls='--', color='black', lw=0.5)

    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"✅ Saved: {output_path}")
    try:
        display(IPImage(output_path))
    except:
        pass

