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
 
 
def get_start_years(nina_df, exclude_2020=False):
    """
    Extracts start years from a La Nina DataFrame, optionally excluding 2020.
    """
    years = nina_df['year'].values.copy()
    if exclude_2020:
        years = years[years != 2020]
    return years
 
 
def extract_windows(ds, years):
    """
    For each start year Y, extracts Dec(Y-1) through Feb(Y+1), giving
    15 months total. Returns a list of Datasets, each with a
    'month_offset' coordinate on the time dimension (0=Dec, 1=Jan, ..., 14=Feb).
    Feb 29 receives the same offset as Feb 28 and is averaged with it.
    """
    windows = []
    time_pd = pd.DatetimeIndex(ds['time'].values)
 
    for year in years:
        start = pd.Timestamp(year - 1, 12, 1)
        end   = pd.Timestamp(year + 1, 2, 28, 23, 59, 59)
 
        mask = (time_pd >= start) & (time_pd <= end)
        if not mask.any():
            print(f"Warning: no data found for La Nina year {year}, skipping.")
            continue
 
        window = ds.isel(time=mask)
        window_time = pd.DatetimeIndex(window['time'].values)
 
        # Map each timestep to a month offset 0-14:
        # Dec(Y-1)=0, Jan(Y)=1, Feb(Y)=2, Mar(Y)=3, ...,
        # Nov(Y)=11, Dec(Y)=12, Jan(Y+1)=13, Feb(Y+1)=14
        def timestamp_to_offset(ts):
            if ts.year == year - 1:   # Dec(Y-1)
                return 0
            elif ts.year == year:     # Jan(Y) through Dec(Y)
                return ts.month       # Jan=1, Feb=2, ..., Dec=12
            else:                     # Jan(Y+1), Feb(Y+1)
                return ts.month + 12  # Jan=13, Feb=14
 
        offsets = np.array([timestamp_to_offset(ts) for ts in window_time])
        window = window.assign_coords(month_offset=("time", offsets))
        windows.append(window)
 
    return windows
 
 
def composite_windows(windows):
    """
    For each month_offset (0-14), averages all timesteps within that month
    across all events. The two-step averaging (within month, then across
    events) handles varying day counts cleanly, including leap years.
    """
    n_offsets = 15
    offset_groups = {i: [] for i in range(n_offsets)}
 
    for w in windows:
        for offset in range(n_offsets):
            sel = w.where(w['month_offset'] == offset, drop=True)
            if sel.sizes['time'] > 0:
                offset_groups[offset].append(sel.mean('time'))
 
    composited = []
    for offset in range(n_offsets):
        slices = offset_groups[offset]
        if not slices:
            continue
        stacked = xr.concat(slices, dim='event')
        mean = stacked.mean('event')
        mean = mean.expand_dims({'month_offset': [offset]})
        composited.append(mean)
 
    return xr.concat(composited, dim='month_offset')
 
 
def make_nina_composites(ds, ninas, ninas_multi, exclude_2020=False):
    """
    Creates composites of a La Nina event year from an xarray Dataset,
    for all La Nina events and multi-year events separately.
 
    The composite window runs from Dec(Y-1) through Feb(Y+1), giving
    15 months with month_offset 0-14:
        0=Dec(Y-1), 1=Jan(Y), 2=Feb(Y), ..., 11=Nov(Y),
        12=Dec(Y), 13=Jan(Y+1), 14=Feb(Y+1)
 
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
    'month_offset' dimension (0-14).
    """
    years_all   = get_start_years(ninas, exclude_2020)
    years_multi = get_start_years(ninas_multi, exclude_2020)
 
    windows_all   = extract_windows(ds, years_all)
    windows_multi = extract_windows(ds, years_multi)
 
    return {
        'all':   composite_windows(windows_all),
        'multi': composite_windows(windows_multi)
    }
 
 
def main():
    # global oni_data, ninas, ninas_multi, ersst_composites
    oni_data = read_oni('data/RONI_timeseries.csv')
    ersst_data = xr.open_dataset('reanalysis/ERSST_merged.nc')
 
    ninas, ninas_multi = identify_ninas(oni_data)
    ersst_composites = make_nina_composites(ersst_data, ninas, ninas_multi,
                                            exclude_2020=False)
 
 
if __name__ == '__main__':
    main()
