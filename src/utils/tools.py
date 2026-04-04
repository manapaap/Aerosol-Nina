# -*- coding: utf-8 -*-
"""
Small Utility Functions to be Shared
"""


import cartopy.crs as ccrs
import numpy as np
from matplotlib.colors import TwoSlopeNorm, Normalize
import matplotlib.pyplot as plt
from pathlib import Path
import os

# Some boxes for plotting data
pac_domain = [-80, 140, -60, 40]  # [lon_min, lon_max, lat_min, lat_max]


def get_project_root():
    return Path(__file__).resolve().parents[2]



def plot_scalar_field(data, title='', cbar_lab='',
                      levels=4, to='', lims=pac_domain):
    """
    Contour plot of a scalar field by providing the data directly.
    Can save plot directly if provided a path in to=''
    """
    era5 = data.fillna(0).copy()
    proj = ccrs.Robinson(central_longitude=180)

    lon = era5.lon.values
    lat = era5.lat.values
    lon2d, lat2d = np.meshgrid(lon, lat)

    vmin, vmax = np.nanpercentile(era5.values, [0.5, 99.5])

    # TwoSlopeNorm requires vmin < vcenter < vmax strictly
    if vmin >= 0:
        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap = 'Reds'
    elif vmax <= 0:
        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap = 'Blues_r'
    else:
        norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        cmap = 'RdBu_r'

    fig, ax = plt.subplots(figsize=(10, 5), dpi=600,
                           subplot_kw={'projection': proj})
    ax.set_global()
    ax.set_title(title)

    # FIX 1: transform must be PlateCarree (the CRS your data is in)
    pcm = ax.pcolormesh(lon2d, lat2d, era5,
                        transform=ccrs.PlateCarree(),
                        shading='nearest', cmap=cmap, norm=norm)

    # FIX 2: use contour on the regular grid (not tricontour on flat arrays)
    contour_levels = np.linspace(vmin, vmax, levels)
    contour = ax.contour(lon2d, lat2d, era5,
                         levels=contour_levels,
                         colors='black', linewidths=0.8,
                         transform=ccrs.PlateCarree())
    ax.clabel(contour, inline=True, fontsize=8)

    ax.coastlines()
    gl = ax.gridlines(draw_labels=True, dms=True)
    gl.top_labels = False
    gl.left_labels = False

    cbar = plt.colorbar(pcm, ax=ax, orientation='vertical',
                        pad=0.05, shrink=0.65, format='%.2f')
    cbar.set_label(cbar_lab)

    # FIX 3: use set_extent for geographic bounds
    if lims is not None:
        ax.set_extent(lims, crs=ccrs.PlateCarree())  # [lon_min, lon_max, lat_min, lat_max]

    if to:
        # FIX 4: os.path.join handles separators cross-platform
        fig.savefig(os.path.join('figures', 'saves', f'{to}.png'),
                    dpi=600, bbox_inches='tight', pad_inches=0)

    plt.show()
    
