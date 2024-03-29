#coding=UTF-8
# aim:transform raster to shapefile and calculate area
# run:type-0-4
import arcpy
from arcpy import env
from arcpy.sa import *
import os

arcpy.CheckOutExtension("3D") # Obtain a license for the ArcGIS 3D Analyst extension
arcpy.env.overwriteOutput = True
#base_dir = 'D:/evaluate/model_576_240117'
#version = 'iew100'
#print(version)
predicted_image_dir =r'E:\new_result\sample\tif'# os.path.join(base_dir,version +'/tif')
tif2shp = os.path.join(predicted_image_dir,'tif2shp')
if not os.path.exists(tif2shp):
    os.makedirs(tif2shp)
tif2shp_dn1_path = os.path.join(predicted_image_dir,'tif2shp_dn1')
if not os.path.exists(tif2shp_dn1_path):
    os.makedirs(tif2shp_dn1_path)

env.workspace = predicted_image_dir
tif_list = arcpy.ListRasters("*", 'TIF')
for i, raster in enumerate(tif_list):
    # print(i,raster)
    outReclass = Reclassify(raster, "Value",RemapRange([[0, 0.5, 0], [0.5, 1, 1]]))
    shpfile = raster.split(".")[0] + '_2shp.shp'
    shp_path = os.path.join(tif2shp , shpfile)
    if not os.path.exists(shp_path):
        arcpy.RasterToPolygon_conversion(outReclass, shp_path,"NO_SIMPLIFY", "Value")

        shpfile_gridcode1 = raster.split(".")[0] + '_2shp_dn1.shp'
        toshp_gridcode1_path = os.path.join(tif2shp_dn1_path,shpfile_gridcode1)
        arcpy.Select_analysis(shp_path, toshp_gridcode1_path, '"gridcode" = 1') # select value=1
        print('Finish:', str(i) + '/' + str(len(tif_list)))

print('Finish transforming tif to shp and extracting dn1.shp')


# ######################## merge
arcpy.env.workspace = tif2shp_dn1_path
tif2shp_dn1_merge = os.path.join(tif2shp_dn1_path , 'tif2shp_dn1_merge.shp')
if not os.path.exists(tif2shp_dn1_merge):
    mergeshp = arcpy.ListFeatureClasses()
    print('mergeshp:', len(mergeshp))
    arcpy.Merge_management(mergeshp, tif2shp_dn1_merge ) #merge several shp files
    print('finish merging')
tif2shp_dn1_merge_lyr = "tif2shp_dn1_merge_lyr"
arcpy.MakeFeatureLayer_management(tif2shp_dn1_merge, tif2shp_dn1_merge_lyr)#bound of region

predicted_polygon_dir = os.path.join(base_dir,version)
####################### within bound
predicted_polygons = os.path.join(predicted_polygon_dir , 'predicted_polygons.shp')
if not os.path.exists(predicted_polygons):
    region_path = os.path.join(base_dir , 'label')
    region_bound = os.path.join(region_path , 'test_regions.shp')
    region_bound_lyr = "region_lyr"
    arcpy.MakeFeatureLayer_management(region_bound, region_bound_lyr)#bound of region
    inFeatures = [tif2shp_dn1_merge_lyr, region_bound_lyr]
    arcpy.Intersect_analysis(inFeatures, predicted_polygons,"ALL", "", "")#predict polygons with bound
    print('finish getting predicted polygons')
#######################add area
    arcpy.AddField_management(predicted_polygons, 'area', "Double")
    arcpy.CalculateField_management(predicted_polygons, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")
