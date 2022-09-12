# Land Carbon Budget Intact and Non-Intact Forest
------------------------------------
  Intact and Non Intact forest NBP
            TRENDY_v11
-------------------------------------

Models that produce nbp at pft level (see attached python file IntactAndNonIntactForestNBP.py)
1) From monthly to yearly over  1990-2021.
2) Mean forest NBP: average all forest PFTs.

3) process ISBA-CTRIP model 
   nbpTree=nppTree-rhTree-DisturbancesTree
   where:DisturbancesTree=fCleach+fFire
   We assume most of fFire and fCleach originates from forest, if forest exists in the gridcell 

4) If low spatial resolution regrid into 0.5x0.5 deg


5) The following steps are done in Google Earth Engine (GEE) platform: 
      - Convert Hansen tree cover (30m spatial resolution) to forest cover. To do this I used the FAO definition of forest
         (more that 20% tree cover and a minimum continuity of 0.5 ha).
      - Intact and Non-Intact "Forest" masks came from Popatov except over Canada and Brazil who provide more acurate masks.
      - Merge the two datasets to get the Intact and Non-Intact forest area per gridcells of around 30m spatial resolution. 
      - Redrid the data to 0.5 degree spatial resolution. Because of the computational issue, this has been done in two steps.
        From 30m to 0.01 degree, then from 0.01 to 0.5 degree.
      - The 0.5 degree Intact and Non-Intact forest area is saved in "IntactAndNonIntactForest_0.5deg.nc" NetCDF file. 
        The javascript code "IntactAndNonIntactForest_0.5deg.js" that is used to generate this file is included here.
        The NetCDF is availble via request to ram.alkama[at]hotmail.fr
6) This NetCDF file is then used to convert forest NBP (kg C/m2/s) into (kgC/gridcell/yr) for both Intact and NonIntact forest.

 
last update: 08/09/2022
