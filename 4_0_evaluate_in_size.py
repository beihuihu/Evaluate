import arcpy
import os
arcpy.env.overwriteOutput = True

base_dir = 'D:/evaluate'
version = 'model_576_230111'
evaluation_path = os.path.join(base_dir,'label')

cal_area=False
#split label polygon
label_polygons = os.path.join(evaluation_path , 'test_polygons.shp')
split_field="area"
area_size_list=[[0,0.001],[0.001,0.005],[0.005,0.01],[0.01,0.1],[0.1,1],[1,50]]#

for area in area_size_list:
    suffix=str(area[1]).replace('.','_')
    filename='test_polygons_lte{}.shp'.format(suffix)
    if not os.path.exists(os.path.join(evaluation_path,filename)):
        arcpy.Select_analysis(label_polygons,os.path.join(evaluation_path,filename),"{}>{} and {}<={}".format(split_field,area[0],split_field,area[1]))
        print('finish',filename)

#split predicted polygon
predicted_polygon_dir =os.path.join(base_dir,version)
predicted_polygons =os.path.join(predicted_polygon_dir,'predicted_polygons.shp')

# for area in area_size_list:
#     suffix=str(area[1]).replace('.','_')
#     filename='test_polygon_lte{}.shp'.format(suffix)
#     selected_label_polygons =os.path.join(evaluation_path,filename)
#     output_file=os.path.join(predicted_polygon_dir,filename.replace('test','predicted'))
#     arcpy.MakeFeatureLayer_management(predicted_polygons, 'predicted_polygons')

#     print("--------begin select--------")
#     #select predicted polygons which not interect with label polygons and area satisfy the requirement
#     arcpy.SelectLayerByLocation_management('predicted_polygons', 'INTERSECT', label_polygons,invert_spatial_relationship=True)
#     arcpy.SelectLayerByAttribute_management('predicted_polygons',"SUBSET_SELECTION","{}>{} and {}<={}".format(split_field,area[0],split_field,area[1]))
#     #add predicted polygons which interect with selected label polygons
#     arcpy.SelectLayerByLocation_management('predicted_polygons', 'INTERSECT', selected_label_polygons,selection_type='ADD_TO_SELECTION')
#     arcpy.CopyFeatures_management('predicted_polygons', output_file)
#     print("finish:"+filename)

print('version             : {}'.format(version))
omissive_polygons=os.path.join(predicted_polygon_dir,'omissive_polygons.shp')
arcpy.MakeFeatureLayer_management(omissive_polygons, 'omissive_polygons')
for area in area_size_list:
    print('\n----area size: ({:^5},{:^5}]----\n'.format(area[0],area[1]))
    suffix=str(area[1]).replace('.','_')
    filename='test_polygons_lte{}.shp'.format(suffix)

    #calculate total area of selected label polygon
    selected_label_polygons =os.path.join(evaluation_path,filename)
    cursor =arcpy.da.SearchCursor(selected_label_polygons, ["area"])
    label_area=0
    for row in cursor:
        label_area=label_area+row[0]#sum area

    selected_omissive_polygons=os.path.join(predicted_polygon_dir,'omissive_predictions_lte{}.shp'.format(suffix))
    if not os.path.exists(selected_omissive_polygons):  
        print("--------begin select--------")
        arcpy.SelectLayerByLocation_management('omissive_polygons', 'WITHIN', selected_label_polygons)
        arcpy.CopyFeatures_management('omissive_polygons', selected_omissive_polygons)
        print("finish:"+filename)
    #calculate total area of selected omissive polygons
    cursor =arcpy.da.SearchCursor(selected_omissive_polygons, ["area"])
    omission_area=0
    for row in cursor:
        omission_area=omission_area+row[0]#sum area
    print('label area          : {:.4f}'.format(label_area))
    print('omissive area       : {:.4f}'.format(omission_area))
    print('omission error      : {:.4f}'.format(omission_area/label_area))