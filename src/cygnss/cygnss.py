import xarray as xr
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import shutil
import math
from scipy import stats
import warnings
import rasterio


warnings.filterwarnings("ignore")


def sort_files_by_date(source_dir):  
    """  
    Sorts .nc files in the specified directory by date and moves them into folders named with the dates.  

    Parameters:  
    - source_dir: The path to the source directory containing the .nc files.  
    """  
    # Iterate through all files and folders in the source directory  
    for filename in os.listdir(source_dir):  
        
        if filename.endswith('.nc'):  
            
            start_date_str = filename[12:20]   

            # Create the target directory (if it doesn't exist)  
            target_dir = os.path.join(source_dir, start_date_str)  
            if not os.path.exists(target_dir):  
                os.makedirs(target_dir)  

            
            source_path = os.path.join(source_dir, filename)  
            target_path = os.path.join(target_dir, filename)  

            
            shutil.move(source_path, target_path)  

    print(f"Files in the source directory {source_dir} have been sorted and moved into folders by date.")  


def read_data(f_list: str):

    """  
    Read multiple NetCDF files into a single xarray Dataset.   

    Parameters:  
    - f_list: Files path pointing to the NetCDF files to be read.  

    Returns:  
    - ds (xarray.Dataset): A single xarray Dataset containing the concatenated data from  
    the input files.  
    """  
    # print('The input parameter is the data path: ~\path\*.nc')
    
    ds = xr.open_mfdataset(f_list, concat_dim="sample", combine="nested",
                data_vars='minimal', coords='minimal', compat='override')
    
    return ds



def extract_obs(ds: xr.Dataset, obs_list: list) -> pd.DataFrame:  
    """  
    Extract and flatten specified variables from an xarray.Dataset into a pandas.DataFrame.  

    Parameters:  
    - ds (xarray.Dataset): The xarray Dataset containing the variables to be extracted.  
    - obs_list (List[str]): A list of strings specifying the names of the variables to extract.  

    Returns:  
    - pd.DataFrame: A pandas DataFrame where each column corresponds to a variable from obs_list,  
                    and the data is flattened (converted to a 1D array) from the original shape.   
    """  
    
    if not obs_list or not all(isinstance(obs, str) for obs in obs_list):  
        raise ValueError("obs_list must be a non-empty list of strings")


    df = pd.DataFrame()  


    for obs in obs_list:  
        if obs in ds:  
            # Check the dimensions of the variable  
            dims = ds[obs].dims  

            if 'delay' in dims and 'doppler' in dims:  
                # Perform max reduction over 'delay' and 'doppler'  
                flattened_data = ds[obs].max(('delay', 'doppler')).values.flatten()  
                print(f"Info: Variable '{obs}' applies a maximum reduction along the 'delay' and 'doppler' dimensions.")  
            else:  
                # For variables without 'delay' and 'doppler', just flatten  
                flattened_data = ds[obs].values.flatten()     

            df[obs] = flattened_data  
        
        else:  
            print(f"Warning: Variable '{obs}' not found in the Dataset.")  

    if df.empty:  
        print("No valid data extracted from the Dataset.")  

    return df 
    


def check_binary_land(quality_flag):  
    
    binary_str = format(int(quality_flag), '031b')  
    
    specific_bits = binary_str[-2] + binary_str[-4] + binary_str[-5] + binary_str[-8] + binary_str[-11] + binary_str[-16] + binary_str[-17]  
    
    return specific_bits != '0000100'



def quality_control_default(df_original: pd.DataFrame,ds: xr.Dataset) -> pd.DataFrame:  
    
    df = df_original.copy()
    
    output_info = """The quality control criteria adopted for this function are as follows: 
                    1. quality_flags: s_band_powered_up, large_sc_attitude_err, black_body_ddm, ddm_is_test_pattern,  
                    direct_signal_in_ddm, low_confidence_gps_eirp_estimate, and sp_over_land 
                    2. sp_inc_angle: less than 65 degrees   
                    3. sp_rx_gain: greater than or equal to 0 
                    4. ddm_snr: greater than or equal to 2  
                    5. brcs_ddm_peak_bin_delay_row: between 4 and 15th """
    print(output_info)

    original_columns = df.columns.tolist()
    

    required_columns = ['quality_flags', 'sp_inc_angle', 'sp_rx_gain', 'ddm_snr', 'brcs_ddm_peak_bin_delay_row']  

    missing_columns = set(required_columns) - set(df.columns)  

    if missing_columns:  
            
        for col in missing_columns:  
            if col in ds:  
                df[col] = ds[col].values.flatten() 
        
            else:  
                raise ValueError(f"Dataset {ds} does not contain the required column: {col}")  
    

    df_filtered = df[  
        
        df.apply(lambda row: not check_binary_land(row['quality_flags']), axis=1) &  
        
        (df['sp_inc_angle'] <= 65) &  
        
        (df['sp_rx_gain'] >= 0) &  
        
        (df['ddm_snr'] >= 2) &  

        (df['brcs_ddm_peak_bin_delay_row'] >= 4) & (df['brcs_ddm_peak_bin_delay_row'] <= 15)  
    ]  
    
    
    
    df_final = df_filtered[original_columns]
    
    return df_final 


def quality_control_custom():
    pass



def cal_sr( df_original: pd.DataFrame, ds: xr.Dataset, quality_control: bool = False) -> pd.DataFrame:  
    
    df = df_original.copy() 

    original_columns = df.columns.tolist() 
    required_columns = ['power_analog', 'brcs','gps_eirp', 'sp_rx_gain', 'rx_to_sp_range', 'tx_to_sp_range', 'sp_lon', 'sp_lat'] 
    new_columns = ['sr', 'sp_lat', 'sp_lon']


    missing_columns = [col for col in required_columns if col not in df.columns]  
    
    
    if missing_columns:  
        
        for col in missing_columns:  
            if col in ['power_analog', 'brcs']:

                df[col] = ds[col].max(('delay', 'doppler')).values.flatten()  
            
            else:  
                    
                df[col] = ds[col].values.flatten()  

        
    sr = 10*np.log10(df['power_analog'])-10*np.log10(df['gps_eirp'])-10*np.log10(df['sp_rx_gain'])-20*np.log10(0.1904)+20*np.log10(df['rx_to_sp_range']+df['tx_to_sp_range'])+20*np.log10(4*math.pi)

    df['sr'] = sr  

    df.loc[df['sp_lon'] > 180, 'sp_lon'] -= 360  

    final_columns = [col for col in original_columns if col not in new_columns] + new_columns  
    df = df[final_columns]


    if quality_control: 
            
        df = quality_control_default(df,ds)
    
    
    return df




def filter_data_by_lonlat(df_original: pd.DataFrame, region: list) -> pd.DataFrame:  
    """  
    Filters a DataFrame based on a given longitude and latitude range.  

    Args:  
        df (pd.DataFrame): The DataFrame to be filtered.  
        region (list): A list containing four elements representing the minimum longitude, maximum longitude,  
                    minimum latitude, and maximum latitude respectively, in the order: [lon_min, lon_max, lat_min, lat_max].  

    Returns:  
        pd.DataFrame: The filtered DataFrame containing only the rows that fall within the specified region.  
    """  
    
    if 'sp_lon' not in df_original.columns or 'sp_lat' not in df_original.columns:  
        raise ValueError("DataFrame must contain 'sp_lon' and 'sp_lat' columns.")  

    
    if len(region) != 4:  
        raise ValueError("Region list must contain exactly 4 elements: [lon_min, lon_max, lat_min, lat_max].")  

    
    lon_min, lon_max, lat_min, lat_max = region  


    if lon_min > lon_max or lat_min > lat_max:  
        raise ValueError("Longitude and latitude ranges must be specified in ascending order.")  
    
    
    df = df_original.copy() 

    df_region = df[(df['sp_lon'] >= lon_min) & (df['sp_lon'] <= lon_max) &  
                    (df['sp_lat'] >= lat_min) & (df['sp_lat'] <= lat_max)]  
        
    return  df_region 



def filter_data_by_shp(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:  
    pass




def filter_data_by_watermask(tif_path,df_original: pd.DataFrame) -> pd.DataFrame:

    df = df_original.copy()
    
    if 'sp_lon' not in df.columns or 'sp_lat' not in df.columns:  
        raise ValueError("DataFrame must contain 'sp_lon' and 'sp_lat' columns.")  


    if not os.path.exists(tif_path):  
        raise FileNotFoundError(f"The file {tif_path} does not exist.")  

        
    coords = [(x, y) for x, y in zip(df.sp_lon, df.sp_lat)]  

    ds = rasterio.open(tif_path)
    
    
    df['water_id'] = [x[0] for x in ds.sample(coords)]
    
    df = df[~(df['water_id'] >= 1) & (df['water_id'] <= 12)]
    
    df = df.drop('water_id',axis = 1)

    return df 
    


def grid_36km_cyg(df: pd.DataFrame, obs:str):
    """  
    Grid and compute the mean of gnss-r observations..    

    Notes:  
    - It is important that the `lats` and `lons` arrays are sorted in ascending order,  
    as `binned_statistic_2d` expects the bin edges to be in increasing order.  
    """  
        
    lats_filepath = 'EASE2_M36km.lats.964x406x1.double'  
    lons_filepath = 'EASE2_M36km.lons.964x406x1.double'  


    for filepath in [lats_filepath, lons_filepath]:  
        if not os.path.exists(filepath):  
            raise FileNotFoundError(f"EASE-GRID file {filepath} does not exist in the current working path. \n"  
                                    f"You can download it from [https://code.mpimet.mpg.de/boards/1/topics/9593?r=9596#message-9596].")  

    required_columns = ['sp_lat', 'sp_lon', obs]  
    missing_columns = [col for col in required_columns if col not in df.columns]  
    if missing_columns:  
        raise ValueError(f"The DataFrame is missing the following required columns: {', '.join(missing_columns)}")  

    lats = np.fromfile(lats_filepath, dtype=np.float64).reshape((406, 964))  
    lons = np.fromfile(lons_filepath, dtype=np.float64).reshape((406, 964))  

    statistic, xedges, yedges, binnumber = stats.binned_statistic_2d(
    df['sp_lat'], df['sp_lon'], values=df[obs], statistic='mean', 
    bins=[lats[:,0][::-1], lons[0,:]])
    
    grid_obs = np.flipud(statistic)

    return grid_obs


def plot_obs(df: pd.DataFrame):
    pass



