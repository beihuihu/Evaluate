#coding=UTF-8
#aim：get the intersect of prediction (has been transformed into shp and clipped by region) and label


import arcpy
from arcpy import env
import os
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput = True
base_dir = 'D:/evaluate/model_576_240118'
version = 'iew100'
print(version)
predicted_image_dir = os.path.join(base_dir,version +'/tif')

evaluation_path = os.path.join(base_dir,'label')
label_polygons = os.path.join(evaluation_path, 'test_polygons.shp')
label_polygons_l = 'label_polygons_l'
arcpy.MakeFeatureLayer_management(label_polygons, label_polygons_l)

predicted_polygon_dir =os.path.join(base_dir,version)
prediction_polygons =  os.path.join(predicted_polygon_dir , 'predicted_polygons.shp')
prediction_polygons_l = 'prediction_polygons_l'
arcpy.MakeFeatureLayer_management(prediction_polygons,prediction_polygons_l)


prediction_intersect_label = os.path.join(predicted_polygon_dir , "prediction_intersect_label.shp")
if not os.path.exists(prediction_intersect_label):
    print('start interact')
    inFeatures = [label_polygons_l, prediction_polygons_l]
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
    arcpy.analysis.Erase(prediction_polygons, prediction_intersect_label, commission_polygons)
    print('finish calculate commission')
    arcpy.AddField_management(commission_polygons, 'area', "Double")
    arcpy.CalculateField_management(commission_polygons, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

print('finish')
