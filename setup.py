import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gnssr",
    version="0.0.5",
    author="Qinyu Guo",
    url='https://github.com/QinyuGuo-Pot/gnssr',
    author_email="qinyuguo@chd.edu.cn",
    description="GNSS-R Data Processing Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        'xarray == 2024.7.0',
        'numpy == 1.26.4',
        'pandas == 2.2.2',
        'netcdf4 == 1.7.1',
        'scipy == 1.13.1',
        'rasterio == 1.3.10',
        'matplotlib == 3.9.2',
        'jupyter == 1.0.0',
        'dask == 2024.8.1'
    ],
    python_requires=">=3.6",
)
