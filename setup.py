from os import path

from setuptools import setup, find_packages

version = None
exec(open('hmc/version.py').read())

with open(path.join(path.abspath(path.dirname(__file__)), 'README.rst')) as f:
    long_description = f.read()

setup(name='hmc',
      version=version,
      description='Manager of Hydrological Model Continuum (HMC)',
      long_description=long_description,
      author='Fabio Delogu',
      author_email='fabio.delogu@cimafoundation.org',
      url="https://hmc.readthedocs.io/en/latest/",
      license='MIT',
      keywords='hmc config generate generator science hydrology forecast',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Hydrology'
      ],
      install_requires=[
          'pandas', 'rasterio', 'xarray', 'numpy', 'scipy', 'netCDF4', 'dask'
      ],
      packages=find_packages(exclude='tests'),
      entry_points={
          'console_scripts':
              ['hmc = hmc.cli:main']
      },
      python_requires='>=3.6',
      zip_safe=False)
