import arcpy
import os
arcpy.env.overwriteOutput = True

print('load input features and make layer')
base_dir = 'D:/evaluate'
version = 'model_576_230111'
evaluation_path = os.path.join(base_dir,'label')

cal_area=False

#calculate area of label
label_polygons = os.path.join(evaluation_path , 'test_polygon.shp')
if cal_area:
    arcpy.AddField_management(label_polygons, 'area', "Double")
    arcpy.CalculateulateField_management(label_polygons, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

arcpy.env.workspace = label_polygons
cursor =arcpy.da.SearchCursor(label_polygons, ["area"])
area_label=0
for row in cursor:
    area_label=area_label+row[0]#sum area

#calculate area of prediction
predicted_polygon_dir =os.path.join(base_dir,version)
prediction_polygons = os.path.join(predicted_polygon_dir , 'predicted_polygon.shp')
if cal_area:
    arcpy.AddField_management(prediction_polygons, 'area', "Double")
    arcpy.CalculateField_management(prediction_polygons, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

arcpy.env.workspace = prediction_polygons
cursor =arcpy.da.SearchCursor(prediction_polygons, ["area"])
area_prediction=0
for row in cursor:
    area_prediction=area_prediction+row[0]#sum area

#calculate area of intersection
polygons_intersection = os.path.join(predicted_polygon_dir,"prediction_intersect_label.shp")
if cal_area:
    arcpy.AddField_management(polygons_intersection, 'area', "Double")
    arcpy.CalculateField_management(polygons_intersection, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

arcpy.env.workspace = polygons_intersection
cursor =arcpy.da.SearchCursor(polygons_intersection, ["area"])
area_intersection=0
for row in cursor:
    area_intersection=area_intersection+row[0]#sum area

test_region = os.path.join(evaluation_path, 'test_region.shp')
if cal_area:
    arcpy.AddField_management(test_region, 'area', "Double")
    arcpy.CalculateField_management(test_region, "area",  "!shape.geodesicArea@SQUAREKILOMETERS!", "PYTHON_9.3")

arcpy.env.workspace = test_region
cursor =arcpy.da.SearchCursor(test_region, ["area"])
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
