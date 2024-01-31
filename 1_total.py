#coding=UTF-8
# aim:transform raster to shapefile and calculate area
# run:type-0-4
import arcpy
from arcpy import env
from arcpy.sa import *
import os

arcpy.CheckOutExtension("3D") # Obtain a license for the ArcGIS 3D Analyst extension
arcpy.env.overwriteOutput = True
base_dir = 'D:/evaluate/model_576_240121'
version = 'iew100'
print(version)
predicted_image_dir = os.path.join(base_dir,version +'/tif')
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
print('finish step 1')
evaluation_path = os.path.join(base_dir,'label')
label_polygons = os.path.join(evaluation_path, 'test_polygons.shp')
label_polygons_l = 'label_polygons_l'
arcpy.MakeFeatureLayer_management(label_polygons, label_polygons_l)

predicted_polygons_l = 'predicted_polygons_l'
arcpy.MakeFeatureLayer_management(predicted_polygons,predicted_polygons_l)

prediction_intersect_label = os.path.join(predicted_polygon_dir , "prediction_intersect_label.shp")
if not os.path.exists(prediction_intersect_label):
    print('start interact')
    inFeatures = [label_polygons_l, predicted_polygons_l]
    arcpy.Intersect_analysis(inFeatures, prediction_intersect_label,"ALL", "", "")
    print('finish prediction_intersect_label')
    arcpy.AddField_management(prediction_intersect_label, 'area', "Double")
    arcpy.CalculateField_management(prediction_intersect_label, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

omissive_polygons = os.path.join(predicted_polygon_dir , "omissive_polygons.shp")
if not os.path.exists(omissive_polygons):
    print('start calculate omission')
    arcpy.analysis.Erase(label_polygons, prediction_intersect_label, omissive_polygons)
    print('finish calculate omission')
    arcpy.AddField_management(omissive_polygons, 'area', "Double")
    arcpy.CalculateField_management(omissive_polygons, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

commission_polygons = os.path.join(predicted_polygon_dir , "commission_polygons.shp")
if not os.path.exists(commission_polygons):
    print('start calculate commission')
    arcpy.analysis.Erase(predicted_polygons, prediction_intersect_label, commission_polygons)
    print('finish calculate commission')
    arcpy.AddField_management(commission_polygons, 'area', "Double")
    arcpy.CalculateField_management(commission_polygons, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

print('finish step 2')

############## calculate commission
predicted_polygons =os.path.join(predicted_polygon_dir,'predicted_polygons.shp')
predicted_polygons_l = 'predicted_polygons_l'
arcpy.MakeFeatureLayer_management(predicted_polygons, predicted_polygons_l)

commission_polygons=os.path.join(predicted_polygon_dir,'commission_polygons.shp')
commission_polygons_l = 'commission_polygons_l'
arcpy.MakeFeatureLayer_management(commission_polygons, commission_polygons_l)

#spatial join
print('start join predicted polygons with commision polygons')
prediction_with_commission=os.path.join(predicted_polygon_dir,'prediction_with_commission.shp')
arcpy.analysis.SpatialJoin(predicted_polygons_l,commission_polygons_l,prediction_with_commission,'JOIN_ONE_TO_ONE',match_option='CONTAINS')
arcpy.AddField_management(prediction_with_commission, 'commission', "Double")
arcpy.CalculateField_management(prediction_with_commission, 'commission',"!area_1!/!area!","PYTHON_9.3")

############## calculate omission
label_polygons =os.path.join(evaluation_path,'test_polygons.shp')
label_polygons_l = 'label_polygons_l'
arcpy.MakeFeatureLayer_management(label_polygons, label_polygons_l)

omissive_polygons=os.path.join(predicted_polygon_dir,'omissive_polygons.shp')
omissive_polygons_l = 'omissive_polygons_l'
arcpy.MakeFeatureLayer_management(omissive_polygons, omissive_polygons_l)

#spatial join
print('start join label polygons with omissive polygons')
label_with_omission=os.path.join(predicted_polygon_dir,'label_with_omission.shp')
arcpy.analysis.SpatialJoin(label_polygons_l,omissive_polygons_l,label_with_omission,'JOIN_ONE_TO_ONE',match_option='CONTAINS')
arcpy.AddField_management(label_with_omission, 'omission', "Double")
arcpy.CalculateField_management(label_with_omission, 'omission',"!area_1!/!area!","PYTHON_9.3")
print('finish step 3')

arcpy.env.workspace = label_polygons
cursor =arcpy.da.SearchCursor(label_polygons, ["area"])
area_label=0
for row in cursor:
    area_label=area_label+row[0]#sum area

#calculate area of prediction
predicted_polygon_dir =os.path.join(base_dir,version)
prediction_polygons = os.path.join(predicted_polygon_dir , 'predicted_polygons.shp')

arcpy.env.workspace = prediction_polygons
cursor =arcpy.da.SearchCursor(prediction_polygons, ["area"])
area_prediction=0
for row in cursor:
    area_prediction=area_prediction+row[0]#sum area

#calculate area of intersection
polygons_intersection = os.path.join(predicted_polygon_dir,"prediction_intersect_label.shp")

arcpy.env.workspace = polygons_intersection
cursor =arcpy.da.SearchCursor(polygons_intersection, ["area"])
area_intersection=0
for row in cursor:
    area_intersection=area_intersection+row[0]#sum area

test_regions = os.path.join(evaluation_path, 'test_regions.shp')

arcpy.env.workspace = test_regions
cursor =arcpy.da.SearchCursor(test_regions, ["area"])
patch_area=0
for row in cursor:
    patch_area=patch_area+row[0]#sum area

overall=(patch_area-(area_label+area_prediction-2*area_intersection))/patch_area

print('\nversion          : {}'.format(version))
print('label area       : {:.4f}'.format(area_label))
print('patch_area       : {:.4f}'.format(patch_area))
print('prediction area  : {:.4f}'.format(area_prediction))
print('intersection area: {:.4f}'.format(area_intersection))
recall=area_intersection/area_label
precision=area_intersection/area_prediction
F1s=2*recall*precision/(recall+precision)
print('\nrecall           : {:.4f}'.format(recall))
print('precision        : {:.4f}'.format(precision))
print('F1 score         : {:.4f}'.format(F1s))

iou_1=area_intersection/(area_label+area_prediction-area_intersection)
print('iou              : {:.4f}'.format(iou_1))
# iou_2=(patch_area-(area_label+area_prediction-area_intersection))/(patch_area-area_intersection)
# print('iou_2            : {:.4f}'.format(iou_2))
# miou=(iou_1+iou_2)/2
# print('miou             : {:.4f}'.format(miou))

overall=(patch_area-(area_label+area_prediction-2*area_intersection))/patch_area
print('OverallAcurracy  : {:.4f}'.format(overall))
