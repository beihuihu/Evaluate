import arcpy
import os
arcpy.env.overwriteOutput = True

base_dir = 'D:/evaluate'
version = 'model_576_230111'
evaluation_dir = os.path.join(base_dir,'label')
predicted_polygon_dir=os.path.join(base_dir,version)
cal_area=False

split_field="area"
area_size_list=[[0,0.001],[0.001,0.005],[0.005,0.01],[0.01,0.1],[0.1,1],[1,50]]#

for area in area_size_list:
    print('----area size: ({:^5},{:^5}]----\n'.format(area[0],area[1]))
    suffix=str(area[1]).replace('.','_')

    #calculate total area of selected label polygon
    selected_label_polygons =os.path.join(evaluation_dir,'test_polygons_lte{}.shp'.format(suffix))
    selected_label_polygons_l = 'selected_label_polygons_l'
    arcpy.MakeFeatureLayer_management(selected_label_polygons, selected_label_polygons_l)

    selected_omissive_polygons=os.path.join(predicted_polygon_dir,'omissive_predictions_lte{}.shp'.format(suffix))
    selected_omissive_polygons_l = 'selected_omissive_polygons_l'
    arcpy.MakeFeatureLayer_management(selected_omissive_polygons, selected_omissive_polygons_l)
    
    out_feature_class=os.path.join(predicted_polygon_dir,'label_polygons_lte{}.shp'.format(suffix))
    #spatial join
    # print('start join')
    # arcpy.analysis.SpatialJoin(selected_label_polygons_l,selected_omissive_polygons_l,out_feature_class,'JOIN_ONE_TO_ONE',match_option='CONTAINS')
    
    arcpy.AddField_management(out_feature_class, 'omission', "Double")
    arcpy.CalculateField_management(out_feature_class, 'omission',"!area_1!/!area!","PYTHON_9.3")
    print('finish: label_polygons_lte{}.shp'.format(suffix))