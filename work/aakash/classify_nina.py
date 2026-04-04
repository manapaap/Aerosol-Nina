# -*- coding: utf-8 -*-
"""
Function to create ONI 
"""

import numpy as np
import xarray as xr
from os import chdir
import pandas as pd


chdir('C:/Users/aakas/Documents/Aerosol-Nina')


def read_oni(fpath):
    """
    Reads in the ONI data stored at fpath
    """
    oni_data = pd.read_csv(fpath)
    oni_data['date'] = pd.to_datetime(oni_data['date'])
    return oni_data


def identify_ninas(oni_data):
    """
    Identifies La Nina years via ONI criteria- that being ONI < -0.5 
    for five months or more
    
    Returns two arrays- an array of start years for 
    single-year la ninas and start years for multi-year la ninas
    """
    cold_data = oni_data[oni_data['RONI'] <= -0.5]
    # Need to get the 5-month continuity from december
    is_cts = np.diff(cold_data.index)
    is_cts = np.concatenate(([1], is_cts))
    is_cts = is_cts == 1
    # isolate these years
    cold_data = cold_data[is_cts]
    # decembers identified by this criteria are La Ninas!
    cold_dec = cold_data[cold_data['season'] == 'NDJ']
    cold_dec.reset_index(inplace=True, drop=True)
    # We now need to filter for the START year of multi-year la Ninas
    is_cts_year = np.diff(cold_dec.year)
    is_cts_year = np.concatenate(([10], is_cts_year))
    is_cts_year = is_cts_year == 1
    # This includes all first years of a la nina
    ninas = cold_dec[is_cts_year != 1]
    # Now I want the same for multi-year events
    is_cts_year = np.diff(cold_dec.year)
    is_cts_year = np.concatenate((is_cts_year, [10]))
    is_cts_year = is_cts_year == 1
    # Need to edit this to just get start years
    ninas_multi = cold_dec[is_cts_year]
    # Inner join to select only start years
    ninas_multi = ninas.merge(ninas_multi[['date']], on='date')
    return ninas.reset_index(drop=True), ninas_multi


def get_start_years(nina_df, exclude_2020):
    years = nina_df['year'].values.copy()
    if exclude_2020:
        years = years[years != 2020]
    return years


def extract_windows(ds, years):
    """
    For each start year Y, extract Dec(Y-1) through Nov(Y).
    Returns a list of datasets, each with a 'month_offset' coordinate
    on the time dimension (0=Dec, 1=Jan, ..., 11=Nov).
    """
    windows = []
    time_pd = pd.DatetimeIndex(ds['time'].values)

    for year in years:
        start = pd.Timestamp(year - 1, 12, 1)
        end   = pd.Timestamp(year, 11, 30, 23, 59, 59)

        mask = (time_pd >= start) & (time_pd <= end)
        if not mask.any():
            print(f"Warning: no data found for La Nina year {year}, skipping.")
            continue

        window = ds.isel(time=mask)
        window_time = pd.DatetimeIndex(window['time'].values)

        # Dec -> 0, Jan -> 1, ..., Nov -> 11
        # Feb 29 gets offset 2 same as Feb 28, so they are averaged together
        offsets = np.array([(m - 12) % 12 for m in window_time.month])
        window = window.assign_coords(month_offset=("time", offsets))
        windows.append(window)

    return windows


def composite_windows(windows):
    """
    For each month_offset (0-11), average all timesteps across all events.
    This handles varying day counts across years (e.g. leap years) by
    grouping within month before averaging across events.
    """
    offset_groups = {i: [] for i in range(12)}

    for w in windows:
        for offset in range(12):
            sel = w.where(w['month_offset'] == offset, drop=True)
            if sel.sizes['time'] > 0:
                # Mean over time within this month for this event
                offset_groups[offset].append(sel.mean('time'))

    composited = []
    for offset in range(12):
        slices = offset_groups[offset]
        if not slices:
            continue
        # Average across events
        stacked = xr.concat(slices, dim='event')
        mean = stacked.mean('event')
        mean = mean.expand_dims({'month_offset': [offset]})
        composited.append(mean)

    return xr.concat(composited, dim='month_offset')


def make_nina_composites(ds, ninas, ninas_multi, exclude_2020=True):
    """
    Creates composites of a La Nina event year (Dec of year Y-1 through Nov
    of year Y) from an xarray Dataset, for all La Nina events and multi-year
    events separately.
 
    Parameters
    ----------
    ds : xr.Dataset
        Input dataset with a 'time' dimension of dtype datetime64.
        Works with monthly, daily, or sub-daily data.
    ninas : pd.DataFrame
        All La Nina start years, as returned by identify_ninas().
        Must contain a 'year' column.
    ninas_multi : pd.DataFrame
        Multi-year La Nina start years, same format.
    exclude_2020 : bool, optional
        If True, excludes the 2020 La Nina event from both composites.
        Default is False.
 
    Returns
    -------
    dict with keys 'all' and 'multi', each an xr.Dataset with a
    'month_offset' dimension (0=Dec, 1=Jan, ..., 11=Nov). For sub-monthly
    data, each month_offset slice is the mean over all timesteps within
    that month, averaged across all events.
    """
    years_all   = get_start_years(ninas, exclude_2020)
    years_multi = get_start_years(ninas_multi, exclude_2020)
 
    windows_all   = extract_windows(ds, years_all)
    windows_multi = extract_windows(ds, years_multi)
 
    composite_all   = composite_windows(windows_all)
    composite_multi = composite_windows(windows_multi)
 
    return {'all': composite_all, 'multi': composite_multi}
 
 
def main():
    global oni_data, ninas, ninas_multi, ersst_composites
    oni_data = read_oni('CSVs/RONI_timeseries.csv')
    ersst_data = xr.open_dataset('reanalysis/ERSST_merged.nc')
 
    ninas, ninas_multi = identify_ninas(oni_data)
    ersst_composites = make_nina_composites(ersst_data, ninas, ninas_multi,
                                            exclude_2020=False)
 

if __name__ == '__main__':
    main()
    
