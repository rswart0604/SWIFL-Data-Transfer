hello!

to do autobem -> wrf, you need to run:
1) wrf\_to\_epw.py
2) make\_shp.py
3) add\_tmy\_info.sh

this is, after you have obtained wrf data.
each of these scripts have a few variables at the top
that you need to change based on your wrf data. so please do so!
(ie, in add\_tmy\_info.sh, you need to change the date)

each of these scripts can take advantage of multiple cores
(not too many, about 2-4)


the output of those scripts will be an epw file
for each wrf grid cell and a shapefile defining the grid
for each cell. these will then be fed into autobem
to produce results

