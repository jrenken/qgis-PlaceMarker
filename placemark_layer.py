# -*- coding: utf-8 -*-
'''
Created on 01.11.2015

@author: jrenken
'''

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
        if self.checkLayer(layer):
            self.layer = layer;
        else:
            self.layer = None

    def checkLayer(self, layer):
        ''' Check if the layer geometry is point and if the 
            required attributes are available or can be added
        :param layer: vector layer where to add the placemarks
        :type layer: QgsVectorLayer
        '''
        return True

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
        pass
        