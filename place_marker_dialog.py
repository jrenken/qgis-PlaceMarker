# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlaceMarkerDialog
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

import os

from PyQt4 import QtGui, uic
from qgis.gui import QgsMapToolEmitPoint
from PyQt4.QtCore import Qt, pyqtSignal, pyqtSlot, QDateTime, QByteArray,\
    QSettings
from qgis.core import QgsPoint, QgsCoordinateTransform, QgsCoordinateReferenceSystem
from layer_dialog import LayerDialog
from placemark_layer import PlaceMarkLayer
from qgis._core import QgsMapLayerRegistry

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'place_marker_dialog_base.ui'))


class PlaceMarkerDialog(QtGui.QDialog, FORM_CLASS):
    
    mouseClicked = pyqtSignal(QgsPoint, Qt.MouseButton)
    
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(PlaceMarkerDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.mapTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.mapTool.canvasClicked.connect(self.mouseClicked)
        self.crsXform = QgsCoordinateTransform()
        self.crsXform.setDestCRS(QgsCoordinateReferenceSystem(4326))
        self.changeCrs()
        self.iface.mapCanvas().destinationCrsChanged.connect(self.changeCrs)
        settings = QSettings()
        geom = settings.value('/Windows/PlaceMarker/geometry', QByteArray())
        print geom.isEmpty()
        if not geom.isEmpty():
            self.restoreGeometry(settings.value('/Windows/PlaceMarker/geometry', QByteArray()))
        self.lastGeometry = geom
        self.layerId = settings.value(u'PlaceMarker/LayerId', None)
        try:
            layer = QgsMapLayerRegistry.instance().mapLayer(self.layerId)
        except KeyError:
            self.changeLayer()
        self.placeMarkLayer = PlaceMarkLayer(layer)
#
    def showEvent(self, event):
        self.iface.mapCanvas().setMapTool(self.mapTool)
        self.restoreGeometry(self.lastGeometry)
        QtGui.QDialog.showEvent(self, event)


    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue('/Windows/PlaceMarker/geometry', self.saveGeometry());
        QtGui.QDialog.closeEvent(self, event)

    @pyqtSlot(QgsPoint, Qt.MouseButton)
    def mouseClicked(self, pos, button):
        if button == Qt.LeftButton:
            print 'click'
            self.show()
            self.mDateTimeEdit.setDateTime(QDateTime.currentDateTime().toUTC());
            geoPos = self.crsXform.transform(pos)
            self.lineEditPosition.setText(', '.join(geoPos.toDegreesMinutes(5, True, True).rsplit(',')[::-1]))
            self.checkLayer()

    @pyqtSlot()
    def accept(self):
        self.lastGeometry = self.saveGeometry()
        print 'accept', self.pos
        QtGui.QDialog.reject(self)

    @pyqtSlot()
    def reject(self):
        print 'reject'
        QtGui.QDialog.reject(self)

    @pyqtSlot()
    def changeCrs(self):
        '''
        SLot called when the mapcanvas CRS is changed
        '''
        crsSrc = self.iface.mapCanvas().mapSettings().destinationCrs()
        self.crsXform.setSourceCrs(crsSrc)

    @pyqtSlot(name='on_toolButtonChangeLayer_clicked')
    def changeLayer(self):
        dlg = LayerDialog(self)
        dlg.show()
        result = dlg.exec_()
        if result:
            layer = dlg.currentLayer()
            print layer.id()
            self.mMapLayerComboBox.setLayer(layer)
            settings = QSettings()
            settings.setValue(u'PlaceMarker/LayerId', layer.id())

    def checkLayer(self):
        pass
