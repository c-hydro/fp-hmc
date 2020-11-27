=========
Changelog
=========

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
