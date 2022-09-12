*/
Contact: ram.alkama@hotmail.fr
last update: 09/09/2022
/*
var treeCoverVisParam = {
  bands: ['treecover2000'],
  min: 0,
  max: 100,
  palette: ['white','yellow', 'green','black']
};


var gfc2021=ee.Image("UMD/hansen/global_forest_change_2021_v1_9");

var treecover2000 = gfc2021.select(['treecover2000']);

Map.addLayer(treecover2000, treeCoverVisParam, 'tree cover 2000');

var gain = gfc2021.select(['gain']).multiply(100).unmask();

var treeLoss = gfc2021.select(['lossyear']).unmask();

var tree1=treeLoss.remap([1],[0],1).unmask();
var tree2=treeLoss.remap([2],[0],1).unmask();
var tree3=treeLoss.remap([3],[0],1).unmask();
var tree4=treeLoss.remap([4],[0],1).unmask();
var tree5=treeLoss.remap([5],[0],1).unmask();
var tree6=treeLoss.remap([6],[0],1).unmask();
var tree7=treeLoss.remap([7],[0],1).unmask();
var tree8=treeLoss.remap([8],[0],1).unmask();
var tree9=treeLoss.remap([9],[0],1).unmask();
var tree10=treeLoss.remap([10],[0],1).unmask();


var treecover2010net = treecover2000.multiply(tree1).multiply(tree2).multiply(tree3).multiply(tree4).multiply(tree5)
                                    .multiply(tree6).multiply(tree7).multiply(tree8).multiply(tree9).multiply(tree10)
                                    .add(gain);
                             
var canopyCover = treecover2010net.where(treecover2010net.gt(100),100);
print (canopyCover);
Map.addLayer(canopyCover, treeCoverVisParam, 'tree cover 2012');


print('Projection, crs, and crs_transform:', treecover2000.projection());
print('Scale in meters:', treecover2000.projection().nominalScale());

// ---------------
// Canopy cover percentage (e.g. 20%).
var cc = ee.Number(20);
// Minimum forest area in pixels (e.g. 6 pixels, ~ 0.5 ha in this example).
var pixels = ee.Number(6);

var canopyCover20 = canopyCover.gte(cc).selfMask();
// Use connectedPixelCount() to get contiguous area.
var contArea = canopyCover20.connectedPixelCount();
// Apply the minimum area requirement.
var minArea = contArea.gte(pixels).selfMask();

var prj = gfc2021.projection();
var scale = prj.nominalScale();


// Calculate the tree cover area (m2). Use pixelArea() to get the value of each pixel in square metres, 

var forestArea = minArea.multiply(ee.Image.pixelArea());

var IntFor=ee.FeatureCollection('projects/planet-guido/assets/IntactForest2020');
// var Amazon=ee.FeatureCollection('users/ramdanealkama/Brazil/managedForest');
// var Canada=ee.FeatureCollection('users/ramdanealkama/Canada/managedForest').filter(ee.Filter.eq('ManagedFor','Non Managed Forest'));
// var IntFor = Canada.merge(Amazon);

//var TreeCov2000= TreeCov2000.clip(IntFor);
var forestAreaNoIntact= forestArea.subtract(forestArea.clip(IntFor).unmask());
var forestAreaIntact  = forestArea.clip(IntFor).unmask();


var forest2010_at_1km = forestAreaIntact//.unmask()
  .reduceResolution(ee.Reducer.sum().unweighted(), false, 2000) 
  .reproject(ee.Projection('EPSG:4326').scale(0.01, 0.01)).updateMask(1);

Export.image.toAsset({
  image: forest2010_at_1km.toFloat(),
//description: 'ForestAreaCanadaAmazonIntact_at_1km_20p', 
description: 'ForestArea2010ntact_at_1km_20p', 
// folder: 'EE_Images',
  crs: 'EPSG:4326',
  // crsTransform: '[0.25,0,-180,0,-0.25,90]',
  region: ee.Geometry.Polygon([-180, 90, 0, 90, 180, 90, 180, -90, 0, -90, -180, -90], null, false),
  maxPixels: 1e13,
  scale:'1113.19490793'
  }); 



// file saved in your assets
//var Forest = ee.Image("users/ramdanealkama/ForestArea2010Intact_at_1km_20p");
var Forest = ee.Image("users/ramdanealkama/ForestAreaCanadaAmazonIntact_at_1km_20p");
// color palette
var palette = [ 'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
               '004C00', '023B01', '012E01', '011D01', '011301'];
var Viz = {min: 0, max: 1000000, palette: palette};//['00FFFF', '0000FF']};
               
Map.addLayer(Forest, Viz,'Intact forest')


// reduce resolution to 0.5 degrees
var Forest_at_50km = Forest//.unmask()
  .reduceResolution(ee.Reducer.sum().unweighted(), false, 10000) 
  .reproject(ee.Projection('EPSG:4326').scale(0.5, 0.5)).updateMask(1);


  // export

Export.image.toDrive({
image: Forest_at_50km.toFloat(),
//description: 'Forest2012_NoIntact_at_50km_20p',
description: 'ForestCanadaBrazil_Intact_at_50km_20p', 
folder: 'GEE_ForestCover',
  crs: 'EPSG:4326',
  region: ee.Geometry.Polygon([-180, 90, 0, 90, 180, 90, 180, -90, 0, -90, -180, -90], null, false),
  maxPixels: 1e13,
  scale:'55659.74539663678' 
  }); 


