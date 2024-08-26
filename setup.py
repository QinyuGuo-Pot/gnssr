import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gnssr",
    version="0.0.6",
    author="Qinyu Guo",
    url='https://github.com/QinyuGuo-Pot/gnssr',
    author_email="qinyuguo@chd.edu.cn",
    description="GNSS-R Data Processing Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        'xarray',
        'numpy',
        'pandas',
        'netcdf4',
        'scipy',
        'rasterio',
        'matplotlib',
        'jupyter',
        'dask',
        'geopandas'
    ],
    python_requires=">=3.6",
)
