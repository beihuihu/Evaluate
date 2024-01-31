import arcpy
import os
arcpy.env.overwriteOutput = True

base_dir = 'D:/evaluate/model_576_240118'
version = 'iew100'
evaluation_dir = os.path.join(base_dir,'label')
predicted_polygon_dir=os.path.join(base_dir,version)
cal_area=False

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
label_polygons =os.path.join(evaluation_dir,'test_polygons.shp')
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
print('finish')
