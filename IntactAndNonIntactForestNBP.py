"""
Intact and Non Intact forest NBP


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
last update: 09/09/2022

"""
import cdms2 as cdms, os, glob, numpy as N, MV2 as MV


cdms.setNetcdfShuffleFlag(0)
cdms.setNetcdfDeflateFlag(0)
cdms.setNetcdfDeflateLevelFlag(0)

# --------------------
# 1) select dates and do annual mean
# --------------------

# PreProcess data from monthly 1700-2019 to yearly 1990-2019

for var in ['nbppft','landCoverFrac','nbp']:
    for fil in glob.glob("*%s.nc"%var):
      filo='/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/'+fil
      if not os.path.exists(filo):
        os.system("cdo -P 12 yearmean -selyear,1990/2021 %s %s"%(fil,filo))


# --------------------
# 2) merge forest PFTs
# --------------------

# forest pfts       
listepfts={'ORCHIDEE':[1,2,3,4,5,6,7,8],'ORCHIDEE-CNP':[1,2,3,4,5,6,7,8],'JSBACH':[2,3,4,5],'CLASS-CTEM':[0,1,2,3,4],'DLEM':[4,5,6,7,8,9,10,11],
           'LPJ-GUESS':[0,1,2,3,4,5,6,7,8,9],'OCN':[1,2,3,4,5,6,7,8],'CABLE-POP':[0,1,2,3],'ISAM':[0,1,2,3,4,13,14,15,16,17,19,23],
           'ORCHIDEEv3':[1,2,3,4,5,6,7,8],'SDGVM':[6,7,8,9],'JULES-ES-1p0':[0,1,2,3,4],'CLASSIC':[0,1,2,3,4],'CLASSIC-N':[0,1,2,3,4],
           'VISIT':[0,1,2,3,4,5,6,7],'YIBs':[0,1,2],'LPX-Bern':[0,1,2,3,4,5,6,7],'CLM5.0':[1,2,3,4,5,6,7,8],'LPJ':[0,1,2,3,4,5]} 


#'IBIS' we do not have landCoverFrac for this model
# LPX-Bern and 'VISIT': nbppft over forest is missing

for model in ['CLASSIC','YIBs','CABLE-POP','JSBACH']: #'OCN','CLASSIC-N'
  var='nbppft'
  if model=='CLASSIC':var='nbp'
  print model
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/%s_S2_nbppft.nc'%model)
  nbppft=f(var)
  f.close()
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/%s_S2_landCoverFrac.nc'%model)
  pftFrac=f('landCoverFrac',squeeze=1)
  f.close()
  AXIS=nbppft[:,0,:,:].getAxisList()
  nbp,forestFrac=N.zeros(nbppft[:,0,:,:].shape),N.zeros(nbppft[:,0,:,:].shape)
  if len(pftFrac.shape)==3:
   for pft in listepfts[model]:
     for tt in range(nbppft.shape[0]):
       if model =='CABLE-POP':
         nbp[tt,:,:]=nbp[tt,:,:]+MV.where(nbppft[tt,pft,:,:].mask,0,nbppft[tt,pft,:,:])*MV.where(pftFrac[pft,:,:].mask,0,pftFrac[pft,:,:])
         forestFrac[tt,:,:]=forestFrac[tt,:,:]+MV.where(pftFrac[pft,:,:].mask,0,pftFrac[pft,:,:])
       else:
         nbp[tt,:,:]=nbp[tt,:,:]+nbppft[tt,pft,:,:]*pftFrac[pft,:,:]
         forestFrac[tt,:,:]=forestFrac[tt,:,:]+pftFrac[pft,:,:]
  else:
   for pft in listepfts[model]:
    nbp=nbp[:,:,:]+nbppft[:,pft,:,:]*pftFrac[:,pft,:,:]
    forestFrac=forestFrac[:,:,:]+pftFrac[:,pft,:,:]
  nbp=MV.where(forestFrac>0,nbp/forestFrac,0)
  nbp=MV.masked_equal(nbp,0)
  nbp=cdms.createVariable(nbp,fill_value = 1.e+20,dtype='d',axes =AXIS) 
  nbp.units="kg m-2 s-1"
  nbp.long_name = "Carbon Mass Flux out of Atmosphere due to Net Biospheric Production on Forest"
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/%s_NBP_forest_1990_2021.nc'%model,'w')
  f.write(nbp,id='nbp')
  f.close()


# --------------------
# 3)  ISBA-CTRIP model
# --------------------

if False: # False because the data is not yet available, turn it to True when exists 
  # PreProcess data from monthly 1700-2019 to yearly 1990-2021
  for fil in glob.glob("ISBA*.nc"):
    filo='/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/'+fil
    if not os.path.exists(filo):
      os.system("cdo -P 12 yearmean -selyear,1990/2021 %s %s"%(fil,filo))

  print model
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/%s_S2_nppTree.nc'%model)
  nppTree=f('nppTree')
  f.close()
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/%s_S2_rhTree.nc'%model)
  rhTree=f('rhTree')
  f.close()
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/%s_S2_fFire.nc'%model)
  fFire=f('fFire')
  f.close()
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/%s_S2_fCLeach.nc'%model)
  fCleach=f('fCLeach')
  f.close()
  AXIS=nppTree.getAxisList()
  DisturbancesTree=(fCleach+fFire)
  nbpTree=nppTree-rhTree-MV.where(nppTree>-1,DisturbancesTree,0)
  nbpTree=cdms.createVariable(nbpTree,fill_value = 1.e+20,dtype='d',axes =AXIS) 
  nbpTree.units="kg m-2 s-1"
  nbpTree.long_name = "Carbon Mass Flux out of Atmosphere due to Net Biospheric Production on Forest"
  f=cdms.open('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/%s_NBP_forest_1990_2021.nc'%model,'w')
  f.write(nbpTree,id='nbp')
  f.close()

# --------------------
# 4) if low spatial resolution regrid into 0.5x0.5 deg
# 5) The following steps are done in Google Earth Engine (GEE) platform: 
#      - Convert Hansen tree cover (30m spatial resolution) to forest cover. To do this I used the FAO definition of forest
#         (more that 20% tree cover and a minimum continuity of 0.5 ha).
#      - Intact and Non-Intact "Forest" masks came from Popatov except over Canada and Brazil who provide more acurate masks.
#      - Merge the two datasets to get the Intact and Non-Intact forest area per gridcells of around 30m spatial resolution. 
#      - Redrid the data to 0.5 degree spatial resolution. Because of the computational issue, this has been done in two steps.
#        From 30m to 0.01 degree, then from 0.01 to 0.5 degree.
#      - The 0.5 degree Intact and Non-Intact forest area is saved in "IntactAndNonIntactForest_0.5deg.nc" NetCDF file. 
# 6) This NetCDF file is then used to convert forest NBP (kg C/m2/s) into 
# --------------------
os.chdir('/ESS_EarthObs/DATA_PRODUCTS/TRENDY-v9/TRENDY-v11/Workdir/')


for model in ['CLASSIC','YIBs','CABLE-POP','JSBACH']:#'CLASSIC-N','OCN','ISBA-CTRIP']:
   print model
   fil='%s_NBP_forest_1990_2021.nc'%model
   f=cdms.open(fil)
   var='nbp'#f.listvariable()[0]
   v=f[var]
   nlons=v.shape[2]
   f.close()
   if nlons==720:
     filin=fil
   else:
     filin=fil[:-3]+'_05deg.nc'
     os.system('cdo -P 20 remapcon,targetgrid %s %s'%(fil,filin))
   f=cdms.open(filin)
   nbp=f('nbp')*86400.*365    # from kgC/m2/s to kgC/m2/yr
   f.close()
   AXIS=nbp.getAxisList()

   f=cdms.open('IntactAndNonIntactForest_0.5deg.nc')
   Intact=f('IntactForestArea')
   NonIntact=f('NonIntactForestArea')
   f.close()

   ff=cdms.open('%s_Intact_and_NonIntact_forestNBP_1990_2021_05deg.nc' %model,'w')
   Intact=cdms.createVariable(nbp*Intact,fill_value = 1.e+20,dtype='f',axes =AXIS)
   Intact.units="kg/gridcell/yr"
   ff.write(Intact,id='Intact')
   NonIntact=cdms.createVariable(nbp*NonIntact,fill_value = 1.e+20,dtype='f',axes =AXIS)
   NonIntact.units="kg/gridcell/yr"
   ff.write(NonIntact,id='NonIntact')
   ff.close()



