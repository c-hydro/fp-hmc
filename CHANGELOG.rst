=========
Changelog
=========

Version 3.1.5 (20221130)
========================
- Codes and package based on HMC Fortran codes version 3.1.5;
- Add the writers for discharges, dams volume and dams level in json format; 
- Add the condition for the section code in the section points file in character format;
- Add the possibility of providing to the model time series of observed socket/release systems;
- Add the choice of constant baseflow for each sections (adding a column in the sections shapefile) [experimental];
- Add the selection of the sections using the "hmc_file_filter" dictionary in the datasets configuration file;
- Add the condition to create a tmp folder for the analysis tool (keep/delete tmp files);
- Add the check to control the datasets (mandatory or not mandatory) before running the model;
- Add the tool for merging datasets of different domains into a unique domain;
- Extend the hmc tool for converting time-series adding the dam volume datasets;
- Extend the hmc tool for merging gridded sources (continuum, qt and s3m datasets) and the expected data format for input (netcdf, tiff) and output (netcdf, tiff);
- Extend the hmc tool for preprocessing gridded sources adding the restart datasets in binary format;
- Fix bugs in the hmc manager in managing the point static datasets of dams, joints, lakes, intakes and sections;
- Fix bugs in the hmc manager in managing the compatibility for sections file in shp or ascii format, also with 3 levels of warning;
- Fix bugs in the hmc manager in adding observed time-series [discharge, dam volume and dam level] to the json and summary data structure;
- Fix bugs in the hmc manager in adding dam unavailable datasets in summary data structure;
- Fix bugs in the hmc manager for supporting concentration time equal to 0;
- Fix bugs in the hmc tool for making ensemble time-series;
- Fix bugs in the hmc tool for merging gridded output also in presence of clipped lon-lat matrices;
- Refactoring of the tools section.

Version 3.1.4 (20210308)
========================
- Codes and package based on HMC Fortran codes version 3.1.4;
- Add the reader for the geotiff datasets in the forcing part;
- Add the reader for the ascii file of the lakes in the static part; 
- Add the routines to compute the latitude, longitude and cell area ascii grid to avoid the blocking of the run; 
- Add the routines to compute the catchments mask;
- Add the routines to compute the average time-series over the catchments mask;
- Add the controls to avoid not allowed dimensions and undefined values in the forcing datasets in netcdf format: 
- Add tool to convert source datasets to continuum netcdf file format;
- Add bash launcher script to configure different configuration of model run; 
- Fix bugs in managing/reading/saving the updating datasets;
- Fix bugs in interpolating methods in case of not equal dimensions between terrain and forcing datasets;
- Fix bugs in reading the section and the intake info static files;
- Fix bugs in computing the average time-series for the outcome datasets;
- Fix bugs in defining the frequency of the datasets;
- Fix bugs in computing the time slices to organize the run and the collections of the source and destination datasets;
- Fix bugs in case of the lacking of static information (dam/joint/intake/lakes). 

Version 3.1.3 (20201028)
========================

- Codes and package based on HMC Fortran codes version 3.1.3;
- Add the shapefile reading to get the section information; the "{domain}.info_sections.txt" is saved by the procedure using the shapefile points;
- Fix bugs in managing the forcing gridded netcdf;
- Fix bugs in managing the analysis time-series netcdf;
- Fix bugs in managing the dimensions of gridded netcdf;
- Fix bugs in managing the variables defined as (t,y,x) or (y,x,t) to correctly find the time dimension;
- Fix bugs in managing the orientation of gridded netcdf variables;
- Fix bugs in saving file attributes of "x_ll_corner" and "y_ll_corner";
- Add tool to convert binary datasets to netcdf file;
- Add tool to merge discharges in a probabilistic json output;
- Add tool to convert json output in ascii dewetra format. 

Version 3.1.2 (20200819)
========================

- Codes and package based on HMC Fortran codes version 3.1.2

Version 1.8.5 (20200207)
========================

- Fix bugs in managing time-series
- Fix bugs in writing time-series

Version 1.8.4 (20200120)
========================

- Fix bugs in probabilistic mode
- Insert package documentation
- Insert model documentation
- Update configuration files in json format

Version 1.8.0 (20180521)
========================

- Codes and package refactoring based on HMC Fortran codes version 2.0.7.
- Python 3 refactoring. 

Version 1.7.0 (20161114)
========================

- Codes and package refactoring based on HMC Fortran codes version 2.0.6.

Version 1.6.0 (20150928)
========================

- Update code style and other stuff.
- Update data and algorithm structures.
- Update functions and names.

Version 1.5.0 (20150707)
========================

- Release based on Regione Marche operative hydrologic chain.
- Update Continuum Codes to modern Fortran code style.

Version 1.0.0 (20140401)
========================

- Initial version with methods and classes migrated from research projects (DRIHM and DRIHM2US)
  based on DRiFt and Continuum Codes old versions.
