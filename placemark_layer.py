# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlaceMarkerLayer
                                 A QGIS plugin
 Place Marker offers a convenient way of setting placemarks in a vector layer
                              -------------------
        begin                : 2015-11-01
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Jens Renken (Marum/University of Bremen)
        email                : renken@marum.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from builtins import object
from qgis.PyQt.QtCore import QVariant
from qgis._core import QgsVectorDataProvider, QgsField, QgsGeometry, QgsFeature


class PlaceMarkLayer(object):
    '''
    classdocs
    '''

    REQUIRED_FIELDS = [['pkuid', QVariant.Int],
                       ['name', QVariant.String],
                       ['description', QVariant.String],
                       ['class', QVariant.String],
                       ['timestamp', QVariant.String]]

    def __init__(self, layer=None):
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
        layerOk = self.checkLayer(layer)
        if layerOk:
            self.layer = layer
            self.hasLayer = True

    def addPlaceMark(self, pos, name, description, category, timestamp):
        ''' adds a point to the layer

        :param pos: lat/lon position of the placemark
        :type pos: QgsPointXY

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
            feat = QgsFeature(self.layer.fields())
            feat.setAttribute('name', name)
            feat.setAttribute('description', description)
            feat.setAttribute('class', category)
            feat.setAttribute('timestamp', timestamp)
            feat.setGeometry(QgsGeometry.fromPointXY(pos))
            (res, _) = self.layer.dataProvider().addFeatures([feat])
            if res:
                self.layer.updateExtents()
            return res
        return False

    def addMissingFields(self, layer, missingFields):
        if not missingFields:
            return True
        if layer.dataProvider().capabilities() & QgsVectorDataProvider.AddAttributes:
            res = layer.dataProvider().addAttributes(missingFields)
            if res:
                layer.updateFields()
        return res

    def checkLayer(self, layer):
        ''' Check if the layer geometry is point and if the
            required attributes are available or can be added
        :param layer: vector layer where to add the placemarks
        :type layer: QgsVectorLayer
        '''
        if layer is None:
            return False
        missingFields = []
        for fieldspec in self.REQUIRED_FIELDS:
            try:
                layer.fields().field(fieldspec[0])
            except KeyError:
                missingFields.append(QgsField(fieldspec[0], fieldspec[1]))
        if missingFields:
            return False

        caps = layer.dataProvider().capabilities()
        reqCaps = (QgsVectorDataProvider.AddFeatures | QgsVectorDataProvider.DeleteFeatures)
        if (caps & reqCaps) == reqCaps:
            return True
        return False

    def applyPresetStyle(self):
        try:
            self.layer.loadNamedStyle(':/plugins/PlaceMarker/Styles/default_style.qml')
            self.layer.triggerRepaint()
        except Exception:
            pass
