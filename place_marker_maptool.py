# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlaceMarkerMapTool
                                 A QGIS plugin
 Place Marker offers a convenient way of setting placemarks in a vector layer
                             -------------------
        begin                : 2015-10-27
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

from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
from qgis.PyQt.Qt import Qt


class PlaceMarkerMapTool(QgsMapToolEmitPoint):
    '''
    classdocs
    '''

    def __init__(self, canvas):
        '''
        Constructor
        '''
        self.canvas = canvas
        super(PlaceMarkerMapTool, self).__init__(self.canvas)
        self.marker = QgsVertexMarker(self.canvas)
        self.marker.setColor(Qt.red)
        self.marker.setIconSize(8)
        self.marker.setIconType(QgsVertexMarker.ICON_X)
        self.marker.setPenWidth(2)
        self.reset()

    def reset(self):
        self.marker.hide()

    def canvasReleaseEvent(self, e):
        self.marker.setCenter(e.mapPoint())
        self.marker.show()

    def deactivate(self):
        self.reset()
        super(PlaceMarkerMapTool, self).deactivate()
