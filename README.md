# gnssr v0.0.4

## Introduction
GNSS-R Data Processing Package

This package provides a comprehensive set of tools and functions for processing and analyzing Global Navigation Satellite System Reflectometry (GNSS-R) data. GNSS-R is an emerging remote sensing technique that leverages the signals transmitted by navigation satellites (such as GPS, GLONASS, Galileo, and BDS) to observe the Earth's surface and atmosphere through reflections from the Earth's surface or other natural scatterers.

The package is designed to facilitate the entire GNSS-R data processing pipeline, from raw signal simulation and processing, to advanced data analysis and visualization. It includes algorithms for:

1. CYGNSS L1 processing
   - Data reading
   - Variable extraction
   - Quality control
   - Gridding
   - Surface reflectivity calculation
2. Under development...


## Installation
To avoid version conflicts between packages, it is recommended to create a virtual environment for gnssr
```python
conda create -n gnssr_env python=3.12.4
```
Activate the virtual environment
```python
conda activate gnssr_env
```
Install gnssr using pip
```python
pip install gnssr
```
Or, download and install from GitHub
```python
git clone https://github.com/QinyuGuo-Pot/gnssr
cd gnssr
pip install -e .
```

## Usage Overview
### Import Module
```python
# import gnssr
from gnssr import cygnss as cyg
```

### Data File Sorting
`sort_files_by_date()` organizes data files by day based on the date information in the CYGNSS L1 data file names. Files from the same day are automatically sorted into the same folder named yyyymm
```python
# source_dir: Directory where the data files are located
cyg.sort_files_by_date('source_dir')
```

### Read Data
`read_data()` calls xarray.open_mfdataset() to read single/multiple netcdf files and merge them into a single xarray.Dataset object.
```python
ds = cyg.read_data('~/path/*.nc')
```

### Variable Extraction
`extract_obs()` extracts variables from the dataset `ds` based on the input list of variables. The extracted variables will be reshaped into a 1D array stored in a dataframe and returned. If the original dimension of the extracted variable contains 'delay' and 'doppler', the peak value will be calculated along these two axes.
```python
# obs_list: List of variables to be extracted, must match the variable names in the netcdf file
obs_list = ['sp_lar','ddm_snr','brcs']
df_obs = cyg.extract_obs(ds, obs_list)
```

### Quality Control
`quality_control_default()` performs quality control on the extracted variables using the following criteria:
1. quality_flags: s_band_powered_up, large_sc_attitude_err, black_body_ddm, ddm_is_test_pattern, direct_signal_in_ddm, low_confidence_gps_eirp_estimate, and **sp_over_land**
2. sp_inc_angle: less than 65 degrees
3. sp_rx_gain: greater than or equal to 0
4. ddm_snr: greater than or equal to 2
5. brcs_ddm_peak_bin_delay_row: between 4 and 15th
```python
# Pass in the dataframe and dataset as parameters
df_qc = cyg.quality_control_default(df_obs,ds) # df is the dataframe returned by extract_obs()
```
`quality_control_custom()` allows users to customize the quality control criteria, under development...


### Surface Reflectivity Calculation
`cal_sr()` calculates surface reflectivity in dB form, returns a dataframe. Parameters: dataframe, dataset, boolean value (whether to perform quality control) ; the dataframe can be the dataframe returned by extract_obs() or an empty dataframe, in which case the function will return`'sr'`,`'sp_lat'` and`'sp_lon'`variables. If True is passed, the function will use the default criteria for quality control.
```python
# df = pd.DataFrame()
df = df_obs.copy()
df_sr = cyg.cal_sr(df,ds,True) 
```


### Filter Data by location
`filter_data_by_lonlat()` filters data based on longitude and latitude range, returns a dataframe. Parameters: dataframe, longitude and latitude range; the dataframe must contain`'sp_lat'` and`'sp_lon'` variables, the longitude and latitude range format is [lon_min,lon_max,lat_min,lat_max]
```python
lonlat_range = [lon_min,lon_max,lat_min,lat_max]
df_region = cyg.filter_data_by_lonlat(df,lonlat_range)
```
`filter_data_by_shp()` filters data based on shp file, under development...


### Exclude GNSS-R Observations in Open Water
`filter_data_by_watermask()` excludes GNSS-R observations in open water, returns a dataframe. Parameters: GSW data file path, dataframe; the dataframe must contain`'sp_lat'` and`'sp_lon'` variables; the algorithm for exclusion is to match GNSS-R observation coordinates (`'sp_lat'`,`'sp_lon'`) with GSW data's coordinates, and exclude observations that fall within the water surface. Currently, the algorithm only supports GSW's seasonal products.
```python
gsw_file = '~/path/gsw_file.tif'
df_no_water = cyg.filter_data_by_watermask(gsw_file,df)
```


### Grid Data
`grid_36km()` grids GNSS-R observations using EASE-Grid 36km grid file, returns a 2D numpy.ndarray. Parameters: dataframe, variable (string) ; the dataframe must contain`'sp_lat'` and`'sp_lon'` and the variable to be gridded ; the algorithm for gridding is to split GNSS-R observation coordinates (`'sp_lat'`,`'sp_lon'`) into 36km grid cells, and calculate the mean value of the variable within each cell. The current working directory must have the EASE-Grid 36km grid file, [download link](https://code.mpimet.mpg.de/boards/1/topics/9593?r=9596#message-9596)
```python
grid_obs = cyg.grid_36km(df_no_water,'sr')
```
Other gridding algorithms are under development...

## Version History
v0.0.4
 - Add documentation

## Concat
 - Email：<qinyuguo@chd.edu.cn>

---
## 介绍
GNSS-R 数据处理包

gnssr提供了一系列用于处理和分析全球导航卫星系统反射(GNSS-R) 数据的工具和函数。GNSS-R 是一种新型的遥感技术，利用导航卫星（如 GPS、GLONASS、Galileo、BDS 等）的反射信号进行对地观测。

该包旨在为 GNSS-R 数据处理提供一个全面的工具，从原始信号仿真和处理，到高级数据分析和可视化。它包含了以下算法：

1. CYGNSS L1 处理
   - 数据读取
   - 变量提取
   - 质量控制
   - 网格化
   - 地表反射率计算
2. 正在开发中...


## 安装

为了避免包之间的版本冲突，建议为 gnssr 创建一个虚拟环境
```python
conda create -n gnssr_env python=3.12.4
```
激活虚拟环境
```python
conda activate gnssr_env
```
pip 安装 gnssr
```python
pip install gnssr
```
或从 GitHub 下载安装
```python
git clone https://github.com/QinyuGuo-Pot/gnssr
cd gnssr
pip install -e .
```

## 使用概览
### 导入模块
```python
# import gnssr
from gnssr import cygnss as cyg
```
### 数据文件整理
`sort_files_by_date()`根据CYGNSS L1数据文件名中的日期信息，对数据文件按天分类整理，同一天的数据会被自动分类至同一个文件夹中，文件夹命名:yyyymm
```python
# source_dir: 数据文件所在目录
cyg.sort_files_by_date('source_dir')
```
### 读取数据
`read_data()`调用xarray.open_mfdataset()，读取单个/多个netcdf文件，并自动合并成一个xarray.Dataset对象
```python
ds = cyg.read_data('~/path/*.nc')
```
### 变量提取
`extract_obs()`根据传入的变量列表对数据集ds进行变量提取，所提取的变量会被重塑为一维数组存储在dataframe中返回，如果提取的变量原始维度中包含'delay'和'doppler',会沿这两个轴求取峰值。
```python
# obs_list: 要提取的变量列表，需与netcdf文件中的变量名一致
obs_list = ['sp_lar','ddm_snr','brcs']
df_obs = cyg.extract_obs(ds, obs_list)
```
### 质量控制
`quality_control_default()`对所提取的变量进行质量控制，默认使用了以下准则：
1. quality_flags: s_band_powered_up, large_sc_attitude_err, black_body_ddm, ddm_is_test_pattern,  
direct_signal_in_ddm, low_confidence_gps_eirp_estimate, and **sp_over_land** 
2. sp_inc_angle: less than 65 degrees   
3. sp_rx_gain: greater than or equal to 0 
4. ddm_snr: greater than or equal to 2  
5. brcs_ddm_peak_bin_delay_row: between 4 and 15th 
```python
# 传入参数：dataframe, 数据集ds
df_qc = cyg.quality_control_default(df_obs,ds) # df为extract_obs()返回的dataframe
```
`quality_control_custom()`允许用户自定义质量控制准则，正在开发中...

### 地表反射率计算
`cal_sr()`计算dB形式的地表反射率，返回dataframe，传入参数：dataframe, 数据集ds，布尔值（是否要进行质量控制）；传入的dataframe可以是`extract_obs()`返回的dataframe，也可以是空的dataframe，传入空的dataframe最后会返回'sr','sp_lat'和'sp_lon'三个变量；如果传入True，则会采用默认准则进行质量控制
```python
# df = pd.DataFrame()
df = df_obs.copy()
df_sr = cyg.cal_sr(df,ds,True) 
```

### 根据位置筛选数据
`filter_data_by_lonlat()`根据经纬度范围筛选数据，返回dataframe，传入参数：dataframe, 经纬度范围；dataframe中需包含'sp_lat'和'sp_lon'变量,经纬度范围格式为[lon_min,lon_max,lat_min,lat_max]
```python
lonlat_range = [lon_min,lon_max,lat_min,lat_max]
df_region = cyg.filter_data_by_lonlat(df,lonlat_range)
```
`filter_data_by_shp()`根据shp文件筛选数据，正在开发中...

### 剔除开放水域内的观测量
`filter_data_by_watermask()`剔除开放水域内的GNSS-R观测量，返回dataframe，传入参数：GSW数据文件路径，dataframe；dataframe中需包含'sp_lat'和'sp_lon'变量；水体剔除的算法是将GNSS-R观测量坐标（'sp_lat','sp_lon'）与GSW数据文件中水体的坐标进行匹配，剔除落在水体内的观测量；目前算法仅支持GSW数据的季节性产品
```python
gsw_file = '~/path/gsw_file.tif'
df_no_water = cyg.filter_data_by_watermask(gsw_file,df)
```

### 网格化
`grid_36km()`采用EASE-Grid 36km的格网文件对GNSS-R观测量进行网格化，返回numpy.ndarray，传入参数：dataframe, 变量（字符串）；dataframe中需包含'sp_lat'和'sp_lon'以及待网格化的变量；网格化的算法是将GNSS-R观测量坐标（'sp_lat','sp_lon'）进行分割并计算均值；当前工作路径下需要有EASE-Grid 36km的格网文件，[下载地址](https://code.mpimet.mpg.de/boards/1/topics/9593?r=9596#message-9596)
```python
grid_obs = cyg.grid_36km(df_no_water,'sr')
```
其他分辨率的网格化算法正在开发中...

## 版本历史
v0.0.4
 - 添加说明文档

## 联系方式
 - 邮箱：<qinyuguo@chd.edu.cn>
