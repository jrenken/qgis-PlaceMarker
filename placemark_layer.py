# -*- coding: utf-8 -*-
'''
Created on 01.11.2015

@author: jrenken
'''
from PyQt4.QtCore import pyqtSlot, QVariant
from qgis._core import QgsVectorDataProvider, QgsField, QgsGeometry, QgsFeature


REQUIRED_FIELDS = [['name', QVariant.String],
                   ['descr', QVariant.String],
                   ['class', QVariant.String],
                   ['timestamp', QVariant.String],
                   ['lat', QVariant.Double],
                   ['lon', QVariant.Double]]


class PlaceMarkLayer:
    '''
    classdocs
    '''

    def __init__(self, layer):
        '''
        Constructor

        :param layer: vector layer where to add the placemarks
        :type layer: QgsVectorLayer
        '''
        self.setLayer(layer)

    def setLayer(self, layer):
        ''' assign a layer. Before check if the requirements are fulffilled
        :param layer: a vector layer
        '''
        self.layer = None
        self.hasLayer = False
        layerOk, missing = checkLayer(layer)
        if layerOk:
            print "Layer ok:", layer.name()
            if missing:
                if not self.addMissingFields(layer, missing):
                    return 
            self.layer = layer;
            layer.layerDeleted.connect(self.layerDeleted)
            self.hasLayer = True
                

    def addPlaceMark(self, pos, name, description, category, timestamp):
        ''' adds a point to the layer

        :param pos: lat/lon position of the placemark
        :type pos: QgsPoint

        :param name: name of the placemark
        :type name: string

        :param description: extended text for the placemark
        :type description: string

        :param category: category to define the 
        :type category: string

        :param timestamp: creation time of the placemark
        :type timestamp: string
        '''
        if self.hasLayer:
            feat = QgsFeature(self.layer.pendingFields())
            feat.setAttribute('name', name)
            feat.setAttribute('descr', description)
            lat, lon = "{:.6f}".format(pos.y()), "{:.6f}".format(pos.x())
            feat.setAttribute('lat', lat)
            feat.setAttribute('lon', lon)
            feat.setAttribute('class', category)
            feat.setAttribute('timestamp', timestamp)
            feat.setGeometry(QgsGeometry.fromPoint(pos))
            (res, outFeats) = self.layer.dataProvider().addFeatures([feat])
            print res, outFeats
            return res
        return False
            
    @pyqtSlot()
    def layerDeleted(self):
        self.layer = None
        self.hasLayer = False
 
    def addMissingFields(self, layer, missingFields):
        if not missingFields:
            return True
        if layer.dataProvider().capabilities() & QgsVectorDataProvider.AddAttributes: 
            res = layer.dataProvider().addAttributes(missingFields)
            if res:
                layer.updateFields()
        print "addMissingFields", missingFields,res
        for f in missingFields:
            print f.name()
        return res

def checkLayer(layer):
    ''' Check if the layer geometry is point and if the 
        required attributes are available or can be added
    :param layer: vector layer where to add the placemarks
    :type layer: QgsVectorLayer
    '''
    if layer is None:
        return False, None
    missingFields = []
    for fieldspec in REQUIRED_FIELDS:
        try:
            layer.fields().field(fieldspec[0])
        except KeyError:
            missingFields.append(QgsField (fieldspec[0], fieldspec[1]))
    if not missingFields:
        return True, []
    
    caps = layer.dataProvider().capabilities()
    reqCaps = (QgsVectorDataProvider.AddFeatures | QgsVectorDataProvider.DeleteFeatures | QgsVectorDataProvider.AddAttributes) 
    if (caps & reqCaps) == reqCaps:
        return True, missingFields
    return False, missingFields
