# Land Carbon Budget Intact and Non-Intact Forest
------------------------------------
  Intact and Non Intact forest NBP
-------------------------------------

Models that produce nbp at pft level
1) From monthly to yearly over  1990-2021 
2) Mean forest NBP: average all forest PFTs

3) process ISBA-CTRIP model 
   nbpTree=nppTree-rhTree-DisturbancesTree
   where:DisturbancesTree=fCleach+fFire
   We assume most of fFire and fCleach originates from forest, if forest exists in the gridcell 


4) if low spatial resolution regrid into 0.5x0.5 deg
5) Since the unit of forest NBP is kg/m2/s 
   we multiply it by Intact and NonIntact forest area 
   Intact and NonIntact "Forest" area came from a combination of Hansen "Tree" cover and Popatov Intat forest mask
   This exircice was done in Google Earth Engine platform 
   We used FAO difenition of forest to convert tree cover to forest cover: (minimum of 20% of tree cover per gridcell and half ha connection)  

Contact: ram.alkama@hotmail.fr
last update: 08/09/2022
