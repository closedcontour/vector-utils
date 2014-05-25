try:
    from osgeo import ogr
except ImportError:
    import ogr

import sys, os

def intersection(sourceFile, maskFile):
    outputFileName = 'intersection'
    
    driver = ogr.GetDriverByName("ESRI Shapefile")

    source = driver.Open(sourceFile,0)
    sourceLayer = source.GetLayer()

    if source is None:
        print "Could not open file ", sourceFile
        sys.exit(1)

    mask = driver.Open(maskFile,0)
    maskLayer = mask.GetLayer()

    if mask is None:
        print "Could not open file ", maskFile

    ### Create output file ###
    if os.path.exists(outputFileName):
        os.remove(outputFileName)
    try:
        output = driver.CreateDataSource(outputFileName)
    except:
        print 'Could not create output datasource ', outputFileName
        sys.exit(1)

    # newLayer = output.CreateLayer('difference',geom_type=ogr.wkbPolygon,srs=sourceLayer.GetSpatialRef())
    newLayer = output.CreateLayer('intersection',geom_type=ogr.wkbMultiLineString,srs=sourceLayer.GetSpatialRef())

    prototypeFeature = sourceLayer.GetFeature(0)
    for i in range(prototypeFeature.GetFieldCount()):
        newLayer.CreateField(prototypeFeature.GetFieldDefnRef(i))
    prototypeFeature.Destroy()

    if newLayer is None:
        print "Could not create output layer"
        sys.exit(1)

    newLayerDef = newLayer.GetLayerDefn()
    ##############################

    processedCount = 0
    featureID = 0
    total = sourceLayer.GetFeatureCount()

    sourceFeature = sourceLayer.GetNextFeature()
    while sourceFeature:
        sourceGeom = sourceFeature.GetGeometryRef()

        maskLayer.ResetReading()
        maskLayer.SetSpatialFilter(sourceGeom)
        maskFeature = maskLayer.GetNextFeature()

        while maskFeature:
            maskGeom = maskFeature.GetGeometryRef()
            intersectionGeom = sourceGeom.Intersection(maskGeom)
            maskFeature.Destroy()
            maskFeature = maskLayer.GetNextFeature()

            if intersectionGeom.Length() > 0:
                newFeature = ogr.Feature(newLayerDef)
                newFeature.SetGeometry(intersectionGeom)
                newFeature.SetFID(featureID)
                for i in range(sourceFeature.GetFieldCount()):
                    newFeature.SetField(i, sourceFeature.GetField(i))
                newLayer.CreateFeature(newFeature)
                featureID += 1
                newFeature.Destroy()

        sourceFeature.Destroy()
        sourceFeature = sourceLayer.GetNextFeature()
        processedCount += 1
        print "%d / %d / %d" % (processedCount, featureID, total)
        
    source.Destroy()
    mask.Destroy()

if __name__ == "__main__":
    intersection(sys.argv[1], sys.argv[2])
