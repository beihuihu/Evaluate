#coding=UTF-8
#aim：get the intersect of prediction (has been transformed into shp and clipped by region) and label


import arcpy
from arcpy import env
import os
import time
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput = True
print('load input features and make layer')
base_dir = 'D:/evaluate'
version = 'model_576_230111'
predicted_image_dir = os.path.join(base_dir,version +'/tif')

evaluation_path = os.path.join(base_dir,'label')
label_polygons = os.path.join(evaluation_path, 'test_polygon.shp')
label_polygons_l = 'label_polygons_l'
arcpy.MakeFeatureLayer_management(label_polygons, label_polygons_l)

predicted_polygon_dir =os.path.join(base_dir,version)
prediction_polygons =  os.path.join(predicted_polygon_dir , 'predicted_polygon.shp')
prediction_polygons_l = 'prediction_polygons_l'
arcpy.MakeFeatureLayer_management(prediction_polygons,prediction_polygons_l)

inFeatures = [label_polygons_l, prediction_polygons_l]
prediction_intersect_label = os.path.join(predicted_polygon_dir , "prediction_intersect_label.shp")
arcpy.Intersect_analysis(inFeatures, prediction_intersect_label,"ALL", "", "")
print('finish prediction_intersect_label')

arcpy.AddField_management(prediction_intersect_label, 'area', "Double")
arcpy.CalculateField_management(prediction_intersect_label, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")
print('finish')
