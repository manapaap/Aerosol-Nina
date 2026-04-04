# -*- coding: utf-8 -*-
"""
Demo of the La Nina composite function and plotting
"""

# importing project library
import utils.tools as tools
import obs.classify_nina as nina
import xarray as xr
from os import chdir


# Obtain root directory and set it as working directory
root = tools.get_project_root()
chdir(root)


def main():
    global ersst_data, ersst_composites
    # shared data folder
    oni_data = nina.read_oni('data/RONI_timeseries.csv')
    # this folder is not on GitHub as it is too large
    ersst_data = xr.open_dataset('reanalysis/ERSST_merged.nc')
    # Returns first year of all la ninas and multi-year la ninas
    ninas, ninas_multi = nina.identify_ninas(oni_data)
    # Obtain composites of ERSST data- exclude 2020 as that is our event year
    # Returns a dictionary with keys "all" and "multi" with xarray datasets as values
    ersst_composites = nina.make_nina_composites(ersst_data, 
                                                 ninas, ninas_multi,
                                                 exclude_2020=True)
    # Plot these data using a helper function
    tools.plot_scalar_field(ersst_composites['all']['ssta'].sel(month_offset=0), 
                            lims=None, cbar_lab='K',
                            title='December before La Nina')
    tools.plot_scalar_field(ersst_composites['multi']['ssta'].sel(month_offset=0), 
                            lims=None, cbar_lab='K',
                            title='December before Multi-Year La Nina')
    tools.plot_scalar_field(ersst_data['ssta'].sel(time="2019-12").sum('time'), 
                            lims=None, cbar_lab='K',
                            title='December before 2020 La Nina')
    # Multi-year El Ninos are preceeded by a stronger El Nino
    # Iwakira and Watanabe (2021)


if __name__ == "__main__":
    main()
    