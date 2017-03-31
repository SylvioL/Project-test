# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 10:35:23 2016

@author: laventure
"""

import os, re, sys, glob, time
from math import *
try:
    import ogr
except:
    from osgeo import ogr

def extract_ref(path_ref, code_ref, field_ref, out_path, out_file_ref):
    """
    Function to extract interesting classes from the references (RPG or CLC). In
    output file, there will be a shapefile per class.
    
    :param path_ref: Path of the input reference
    :type path_ref: str
    :param code_ref: Reference classes
    :type code_ref: list
    :param field_ref: Reference classes field in the shapefile
    :type field_ref: str
    :param out_path: Path of the output folder (Folder in which will be saved output shapefiles)
    :type out_path: str
    :param out_file_ref: list in which will be writeen the path of the output shapefiles
    :type out_file_ref: list of str
    
    :returns: list of str -- variable **out_file_ref**
    """    
    
    for code in code_ref:
        # Start to write a portion of ogr expression
        exp_sql = "\"" # To choose classes with SQL exression
        exp_out_name = "_" # To write the name of the out shapefile
        
        if type(code) == list:
            # If there is several classes for one final class
            for under_c in code:
                if re.search('%', str(under_c)):
                    # To classes beginning by ..
                    exp_sql = exp_sql + field_ref + " LIKE \'" + str(under_c) + "\' OR "
                    exp_out_name = exp_out_name + str(under_c).replace('%', "") + "_"
                else:
                    exp_sql = exp_sql + field_ref + " = \'" + str(under_c) + "\' OR "
                    exp_out_name = exp_out_name + str(under_c) + "_"
            
            exp_sql = exp_sql[:-4] + "\""
            exp_out_name = exp_out_name[:-1]
                
        else:
            if re.search('%', str(code)):
                exp_sql = exp_sql + field_ref + " LIKE \'" + str(code) + "\'\""
                exp_out_name = exp_out_name + str(code).replace('%', "")
            else:
                exp_sql = exp_sql + field_ref + " = \'" + str(code) + "\'\""
                exp_out_name = exp_out_name + str(code)
        
        out_file = out_path + "/" + os.path.basename(path_ref)[:-4] + "_class" + \
            exp_out_name + ".shp"
        out_file_ref.append(out_file)
        
        process = "ogr2ogr -overwrite -where " + exp_sql + " " + out_file + " " + \
            path_ref
        
        print process
        os.system(process)
        
    return out_file_ref

def corresp_code(in_val, tab1, tab2):
    """
    Function to find again classes from the created shapefiles.
    
    :param in_val: Values to correspond
    :type in_val: list of number
    :param tab1: Old reference classes
    :type tab1: list of number
    :param tab2: New reference classes
    :type tab2: list of number
    
    :returns: int -- variable **out_val** : value corresponding to the shapefile class
    """  
    
    # Loop on the reference code list to identify the class
    i = 0        
    while i < len(tab1):
        c = tab1[i]
        index_code = tab1.index(c)
        # if the code is a list then to take the first class
        if type(c) == list:
            c = c[0]
            
        c = str(c).replace("%","") # Replace "%" from sql expression
        # If shpfile code is good (the first value is enough)            
        if in_val[0] == c:
            out_val = tab2[index_code]
            i = len(tab1)
        i = i + 1
    
    return out_val

def create_grid(base_shp, out_grid, distance_line):
    """
    Function to build a grid with the same extend that input shapefile (base_shp)
    
    :param base_shp: Reference shapefile
    :type base_shp: str
    :param out_grid: Path of the output grid
    :type out_grid: str
    :param distance_line: Distance between every line in meter
    :type distance_line: int
    """
    
    # import ogr variable
    data_source = ogr.GetDriverByName('ESRI Shapefile').Open(base_shp, 0)
        
    if data_source is None:
        print('Could not open file')
        sys.exit(1)
        
    shp_ogr = data_source.GetLayer()
    
    # Extract extent
    extent_shp = shp_ogr.GetExtent()
    # Coordinate to build a set of line in a list
    nb_x = int(ceil((extent_shp[1] - extent_shp[0])/distance_line))
    nb_y = int(ceil((extent_shp[3] - extent_shp[2])/distance_line))    
    
    # Projection
    # Import input shapefile projection
    srsObj = shp_ogr.GetSpatialRef()
    # Conversion to syntax ESRI
    srsObj.MorphToESRI() 
           
    ## Remove the output shapefile if it exists
    if os.path.exists(out_grid):
        data_source.GetDriver().DeleteDataSource(out_grid)
    out_ds = data_source.GetDriver().CreateDataSource(out_grid)
    
    if out_ds is None:
        print('Could not create file')
        sys.exit(1)
        
    #  Specific output layer
    out_layer = out_ds.CreateLayer(str(out_grid), srsObj, geom_type=ogr.wkbLineString)
        
    # Add a integer field (ID)
    new_field = ogr.FieldDefn("ID", 0)
    out_layer.CreateField(new_field)
    # Feature for the ouput shapefile
    featureDefn = out_layer.GetLayerDefn()
    
    # Loop on the number of line nb_x next nb_y   
    cnt = 0
    for l in range(nb_x):

        # Define line string
        line = ogr.Geometry(ogr.wkbLineString)
        
        # Add a line
        line.AddPoint(extent_shp[0] + l*distance_line, extent_shp[3])
        line.AddPoint(extent_shp[0] + l*distance_line, extent_shp[2])
        
        # Create a new polygon
        out_feature = ogr.Feature(featureDefn)
        # Set the polygon geometry and attribute
        out_feature.SetGeometry(line)
        out_feature.SetField("ID", int(cnt))
        cnt = cnt + 1
            
        # Append polygon to the output shapefile
        out_layer.CreateFeature(out_feature)

        # Destroy polygons
        out_feature.Destroy() 
    
    for l in range(nb_y):

        # Define line string
        line = ogr.Geometry(ogr.wkbLineString)
        
        # Add a line
        line.AddPoint(extent_shp[0], extent_shp[3] - l*distance_line)
        line.AddPoint(extent_shp[1], extent_shp[3] - l*distance_line)
        
        # Create a new polygon
        out_feature = ogr.Feature(featureDefn)
        # Set the polygon geometry and attribute
        out_feature.SetGeometry(line)
        out_feature.SetField("ID", int(cnt))
        cnt = cnt + 1
            
        # Append polygon to the output shapefile
        out_layer.CreateFeature(out_feature)

        # Destroy polygons
        out_feature.Destroy()   
        
    # Close data
    out_ds.Destroy()  
    
    return 0
    
if __name__=='__main__':
    
    # Start the processus
    startTime = time.time()
    
    path_rpg = "/media/laventure/DATA/OCC_SOL_974/RPG_974/MONO_ILOTS_ANONYMES_974_20150828.shp"
    out_name_rpg = "RPG"
    path_clc = "/media/laventure/DATA/OCC_SOL_974/CLC12_D974_UTM/CLC12_D974_UTM.shp"
    out_name_clc = "CLC"
    out_path_ref = "/media/laventure/DATA/OCC_SOL_974/Results_ref"
    out_name_ref = "REFERENCE_OCSOL"
    csv_nomenclature = "/media/laventure/DATA/OCC_SOL_974/Nomenclature_lareunion.csv"
    
    # Create a grid to cut the biggest polygons
    grid_shp = "/media/laventure/DATA/OCC_SOL_974/Emprise/GRID_CLC_974_1km.shp"
    create_grid(path_clc, grid_shp, 1000)
    # Apply a buffer 0.5 on the grid shapefile
    process = "python BufferOgr.py " + grid_shp + " " + grid_shp[:-4] + "_BUFF05.shp 0.5"
    os.system(process)
      
    ref_file = [] # To stock reference files
    field_name = "OCSOL_CODE" # Field name in which output class names are write  
      
    # 1-2 )
    # To extract intersting classes
    # RPG
    code_rpg = [26, 25, 20, 27, 16, 2, [13, 24, 28], 17, 18, 19]
    field_rpg = "CODE_GROUP"
    code_ocsol_rpg = [11, 12, 13, 14, 15, 16, 17, 21, 22, 23]
    ocsol_rpg_string = ['Canne_a_sucre', 'Maraichage', 'Vergers', 'Arboriculture', 'Fourrage', 'Mais', \
                        'Autres_cultures', 'Landes', 'Prairies_permanentes', 'Prairies_temporaires']
    # CLC
    code_clc = [['31%', 3240], 3320, 3330, '11%', '12%', '14%', ['51%', '52%']]
    field_clc = "CODE_12"
    code_ocsol_clc = [24, 25, 26, 31, 32, 33, 41]
    ocsol_clc_string = ['Forets', 'Roche_nue', 'Vegetation_sparse', 'Zones_urbanisees', \
                        'Autres_zones_artificialisees', 'Espaces_verts_artificialises', 'Surfaces_en_eau']
      
    ref_file = extract_ref(path_rpg, code_rpg, field_rpg, out_path_ref, ref_file)
    ref_file = extract_ref(path_clc, code_clc, field_clc, out_path_ref, ref_file)
      
    for shp in ref_file:
        # 3 )        
        # Buffer erosion
        out_buff = shp[:-4] + "_BUFF_m30.shp"
        process = "python BufferOgr.py " + shp + " " + out_buff + " -30"
        os.system(process)
          
        # 4 ) 
        #  Clip big polygons with the input grid on the clc shapefile only
        if re.search(os.path.basename(path_clc[:-4]), shp):
            # Cut by the grid 1km
            shp_overlap = os.path.basename(out_buff[:-4]) + "_overlay"
            process = "python shapeDifference.py " + out_buff + " " + grid_shp[:-4] + \
                "_BUFF05.shp " + out_path_ref + "/" + shp_overlap + ".shp"
            os.system(process)
            out_buff = out_path_ref + "/" + shp_overlap + ".shp"
        # Separate multi-polygon
        out_multipol = shp[:-4] + "_MULTIPOL.shp"
        process = "python MultiPolyToPoly.py " + out_buff + " " + out_multipol
        os.system(process)
        # 5 )
        # Add a ID
        process = "python AddFieldID.py " + out_multipol
        os.system(process)
        # Add area in a area field in pxl
        process = "python AddFieldArea.py " + out_multipol + " ID 900"
        os.system(process)
        # Select polygons are bigger than a Landsat pixel
        process = "python SelectBySize.py " + out_multipol + " Area 1"
        os.system(process)
              
    # 6 )
    # Settings of the output shapefile fields
    # Search with glob module output shapefile from the SelectBySize function
    infile_px = glob.glob(out_path_ref + "/*_class_*px.shp")
    rpg_shp = ""
    clc_shp = ""
    for in_px in infile_px:
        # Extract class names from the shapefile because of the shapefile name.
        # In output, this is a list.
        value_infile = re.search("_class_(.*)_MULTIPOL", in_px).group(1).split("_")
        # Concatenate reference code
        code = code_rpg + code_clc
        code_ocsol = code_ocsol_rpg + code_ocsol_clc
          
        value = corresp_code(value_infile, code, code_ocsol)
              
        process = "python AddFieldUnique.py " + in_px + " " + field_name + \
            " " + str(value)
          
        os.system(process)
        # Stock sahepfiles from the same database for the 7th step
        if re.search(os.path.basename(path_rpg[:-4]), in_px):        
            rpg_shp = rpg_shp + in_px + " "
        else:
            clc_shp = clc_shp + in_px + " "
          
    # 7 )
    # Merge files from the same database
    # Beginning by the same name
    process = "python MergeFiles.py " + out_name_rpg + " " + out_path_ref + \
        " " + rpg_shp[:-1]
    os.system(process)
          
    process = "python MergeFiles.py " + out_name_clc + " " + out_path_ref + \
        " " + clc_shp[:-1]
    os.system(process)
      
    # 8 )
    # Remove overlap between RPG and CLC classes 
    out_name_overlap = out_name_clc + "_overlap"
    process = "python shapeDifference.py " + out_path_ref + "/" + out_name_clc + \
        ".shp " + out_path_ref + "/" + out_name_rpg + ".shp " + out_path_ref + \
        "/" + out_name_overlap + ".shp"
    os.system(process)
      
    # 9 )
    # Merge whole of the references
    process = "python MergeFiles.py " + out_name_ref + " " + out_path_ref + \
        " " + out_path_ref + "/" + out_name_overlap + ".shp " + out_path_ref + \
        "/" + out_name_rpg + ".shp"
    os.system(process)
      
    # 10 )
    # Separate multi-polygon
    ref_multipol = out_path_ref + "/" + out_name_ref + "_MULTIPOL.shp"
    process = "python MultiPolyToPoly.py " + out_path_ref + "/" + out_name_ref + ".shp " + \
        ref_multipol
    os.system(process)
    # Add a ID, area in a area field in pxl and select polygons are bigger than a Landsat pixel
    process = "python ModifyFieldID.py " + ref_multipol + " ID"
    os.system(process)
    process = "python DeleteField.py " + ref_multipol + " FID"
    os.system(process)
    process = "python DeleteField.py " + ref_multipol + " Area"
    os.system(process)
    process = "python AddFieldArea.py " + ref_multipol + " ID 900"
    os.system(process)
    process = "python SelectBySize.py " + ref_multipol + " Area 1"
    os.system(process)
      
    # Verify geometry polygons
    process = "python vector_functions.py " + ref_multipol[:-4] + "_gt1px.shp -v"
    os.system(process)
    
    # Remove all the shapefiles
    rm_shp = glob.glob(out_path_ref + "/*")
    print("Remove all the intermediate shapefiles !")
    for rm in rm_shp:
        if not re.search(ref_multipol[:-4] + "_gt1px.", rm):
            os.remove(rm)
    
    # Create a nomenclature file for iota2 chain
    ocsol_string = ocsol_rpg_string + ocsol_clc_string
    f = open(csv_nomenclature, "wb") 
    for n in range(len(ocsol_string)):
        
        f.write(ocsol_string[n] + ":" + str(code_ocsol[n]) + "\n")

    f.close()
        
    # End of the processus
    endTime = time.time() # Tps : Terminé
    print '...........' + ' Outputted to File in ' + str(endTime - startTime) + ' secondes'
    nb_day_processing = int(time.strftime('%d', time.gmtime(endTime - startTime))) - 1
    print "That is, " + str(nb_day_processing) + ' day(s) ' + time.strftime('%Hh %Mmin%S', time.gmtime(endTime - startTime))
