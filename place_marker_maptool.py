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

from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand
from PyQt4.Qt import Qt
from qgis.core import QgsPoint, QGis


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
        self.rubberBand = QgsRubberBand(self.canvas, QGis.Polygon)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)
        self.reset()

    def reset(self):
        self.rubberBand.reset(QGis.Polygon)

    def canvasReleaseEvent(self, e):
        p1 = self.canvas.getCoordinateTransform().toMapCoordinates(e.x() - 2, e.y() - 2)
        p2 = self.canvas.getCoordinateTransform().toMapCoordinates(e.x() + 2, e.y() - 2)
        p3 = self.canvas.getCoordinateTransform().toMapCoordinates(e.x() + 2, e.y() + 2)
        p4 = self.canvas.getCoordinateTransform().toMapCoordinates(e.x() - 2, e.y() + 2)
        self.reset()

        self.rubberBand.addPoint(p1, False)
        self.rubberBand.addPoint(p2, False)
        self.rubberBand.addPoint(p3, False)
        self.rubberBand.addPoint(p4, True)
        self.rubberBand.show()

    def deactivate(self):
        self.reset()
        super(PlaceMarkerMapTool, self).deactivate()
