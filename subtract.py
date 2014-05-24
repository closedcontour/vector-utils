try:
    from osgeo import ogr
except ImportError:
    import ogr

import sys, os

def difference(sourceFile, maskFile):
    outputFileName = 'difference'
    
    driver = ogr.GetDriverByName("ESRI Shapefile")

    source = driver.Open(sourceFile,0)
    sourceLayer = source.GetLayer()

    if source is None:
        print "Could not open file ", source
        sys.exit(1)

    mask = driver.Open(maskFile,0)
    maskLayer = mask.GetLayer()
    maskFeature = maskLayer.GetNextFeature()

    if mask is None:
        print "Could not open file ", mask

    ### Create output file ###
    if os.path.exists(outputFileName):
        os.remove(outputFileName)
    try:
        output = driver.CreateDataSource(outputFileName)
    except:
        print 'Could not create output datasource ', outputFileName
        sys.exit(1)

    newLayer = output.CreateLayer('difference',geom_type=ogr.wkbPolygon,srs=sourceLayer.GetSpatialRef())

    prototypeFeature = sourceLayer.GetFeature(0)
    for i in range(prototypeFeature.GetFieldCount()):
        newLayer.CreateField(prototypeFeature.GetFieldDefnRef(i))
    prototypeFeature.Destroy()

    if newLayer is None:
        print "Could not create output layer"
        sys.exit(1)

    newLayerDef = newLayer.GetLayerDefn()
    ##############################

    featureID = 0


    total = sourceLayer.GetFeatureCount()

    # This only works with one mask feature, need to invert nested loops
    while maskFeature:

        maskGeom = maskFeature.GetGeometryRef()
        sourceLayer.ResetReading()
        sourceFeature = sourceLayer.GetNextFeature()

        while sourceFeature:
            sourceGeom = sourceFeature.GetGeometryRef()
            
            newGeom = None
            if sourceGeom.Intersects(maskGeom) == 1:
                newGeom = sourceGeom.Difference(maskGeom)
                # if newGeom.GetArea() > 0:
                #     newFeature = ogr.Feature(newLayerDef)
                #     # newFeature = maskGeom.Clone()
                #     newFeature.SetGeometry(newGeom)
                #     newFeature.SetFID(featureID)
                #     newLayer.CreateFeature(newFeature)
                #     featureID += 1
                #     newFeature.Destroy()
            
            else:
                newGeom = sourceGeom
                # newFeature2 = ogr.Feature(newLayerDef)
                # newFeature2.SetGeometry(sourceGeom)
                # newFeature2.SetFID(featureID)
                # newLayer.CreateFeature(newFeature2)
                # featureID += 1
            
                # newFeature1.Destroy()
                # newFeature2.Destroy()

            if newGeom.GetArea() > 0:
                newFeature = ogr.Feature(newLayerDef)
                newFeature.SetGeometry(newGeom)
                newFeature.SetFID(featureID)
                for i in range(sourceFeature.GetFieldCount()):
                    newFeature.SetField(i, sourceFeature.GetField(i))
                # newFeature.SetField('id', inFeature.GetField('id'))
                newLayer.CreateFeature(newFeature)
                featureID += 1
                newFeature.Destroy()


            sourceFeature.Destroy()
            sourceFeature = sourceLayer.GetNextFeature()
            print "%d / %d" % (featureID, total)
        
        maskFeature.Destroy()
        maskFeature = maskLayer.GetNextFeature()
        
    source.Destroy()
    mask.Destroy()

if __name__ == "__main__":
    difference('calveg_wgs84.shp', '../../park_boundary/processed/yose_park_boundary_wgs84.shp')
