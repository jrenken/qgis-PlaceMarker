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

from PyQt4 import QtGui, uic
from qgis.gui import QgsMapToolEmitPoint, QgsMapTool
from PyQt4.QtCore import Qt, pyqtSignal, pyqtSlot, QDateTime, QByteArray,\
    QSettings, QTimer
from qgis.core import QgsPoint, QgsCoordinateTransform, \
    QgsCoordinateReferenceSystem, QgsMapLayer
from layer_dialog import LayerDialog
from placemark_layer import PlaceMarkLayer
from qgis.core import QgsMapLayerRegistry
from PyQt4.QtGui import QDialogButtonBox, QAbstractButton
from ui_place_marker_dialog_base import Ui_PlaceMarkerDialogBase

REFRESH_RATE = 5000

class PlaceMarkerDialog(QtGui.QDialog, Ui_PlaceMarkerDialogBase):

    mouseClicked = pyqtSignal(QgsPoint, Qt.MouseButton)

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(PlaceMarkerDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.iface = iface
        self.button_box.button(QDialogButtonBox.Apply).setEnabled(False)
        self.mapTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.mapTool.canvasClicked.connect(self.mouseClicked)
        self.crsXform = QgsCoordinateTransform()
        self.crsXform.setDestCRS(QgsCoordinateReferenceSystem(4326))
        self.changeCrs()
        self.iface.mapCanvas().destinationCrsChanged.connect(self.changeCrs)
        self.iface.mapCanvas().mapToolSet[QgsMapTool, QgsMapTool].connect(self.mapToolChanged)
        self.pos = None
        self.geom = None
        self.layerId = None
        self.layerChanged = False
        self.placeMarkLayer = PlaceMarkLayer()
        self.repaintTimer = QTimer()
        self.repaintTimer.timeout.connect(self.repaintTrigger)
        self.layerfeatureCount = dict()

    def showEvent(self, event):
        self.exceptLayers()
        settings = QSettings()
        if self.geom:
            self.restoreGeometry(self.geom)
        else:
            self.restoreGeometry(settings.value('/Windows/PlaceMarker/geometry', QByteArray()))
        self.layerId = settings.value(u'PlaceMarker/LayerId', None)
#         print "Hallo PlaceMark", self.layerId
        layer = QgsMapLayerRegistry.instance().mapLayer(self.layerId)
        if layer:
            self.mMapLayerComboBox.setLayer(layer)
        layer = self.mMapLayerComboBox.currentLayer()
        if layer:
            self.placeMarkLayer.setLayer(layer)
        self.iface.mapCanvas().setMapTool(self.mapTool)
        refresh = settings.value(u'PlaceMarker/AutoRefreshLayer', False, type=bool)
        self.checkBoxAutoRefresh.setChecked(refresh)
        QtGui.QDialog.showEvent(self, event)

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue('/Windows/PlaceMarker/geometry', self.saveGeometry());
        QtGui.QDialog.closeEvent(self, event)
        self.button_box.button(QDialogButtonBox.Apply).setEnabled(False)
        self.lineEditPosition.setText(u'')
#         print 'close'

    @pyqtSlot(QgsPoint, Qt.MouseButton)
    def mouseClicked(self, pos, button):
        if button == Qt.LeftButton:
            self.show()
            self.pos = pos
            self.button_box.button(QDialogButtonBox.Apply).setEnabled(True)
            self.mDateTimeEdit.setDateTime(QDateTime.currentDateTime().toUTC())
            self.geoPos = self.crsXform.transform(self.pos)
            self.lineEditPosition.setText(', '.join(self.geoPos.toDegreesMinutes(5, True, True).rsplit(',')[::-1]))

    @pyqtSlot()
    def accept(self):
        QtGui.QDialog.reject(self)

    @pyqtSlot()
    def reject(self):
        self.geom = self.saveGeometry()
        QtGui.QDialog.reject(self)

    @pyqtSlot()
    def changeCrs(self):
        '''
        SLot called when the mapcanvas CRS is changed
        '''
        crsSrc = self.iface.mapCanvas().mapSettings().destinationCrs()
        self.crsXform.setSourceCrs(crsSrc)

    @pyqtSlot(name='on_toolButtonNewLayer_clicked')
    def newLayer(self):
        dlg = LayerDialog(self.iface, self)
        dlg.show()
        dlg.exec_()

    @pyqtSlot(QgsMapLayer, name='on_mMapLayerComboBox_layerChanged')
    def changeLayer(self, layer):
#         print "change Layer", layer.name()
        self.placeMarkLayer.setLayer(layer)
        self.layerChanged = True

    @pyqtSlot(QgsMapTool, QgsMapTool)
    def mapToolChanged(self, mapToolNew, mapToolOld):
        if mapToolOld == self.mapTool and mapToolNew != self.mapTool:
#             print 'mapToolChanged'
            self.close()

    @pyqtSlot(QAbstractButton, name='on_button_box_clicked')
    def applyNewPlacemark(self, button):
        if self.button_box.buttonRole(button) == QDialogButtonBox.ApplyRole:
            if self.pos is not None:
                res = self.placeMarkLayer.addPlaceMark(self.geoPos,
                                                 self.lineEditName.text(),
                                                 self.lineEditDescription.text(),
                                                 self.comboBoxClass.currentText(),
                                                 self.mDateTimeEdit.dateTime().toString(self.mDateTimeEdit.displayFormat()))
                if res:
                    self.placeMarkLayer.layer.triggerRepaint()
            if self.layerChanged and self.placeMarkLayer.layer:
                settings = QSettings()
                settings.setValue(u'PlaceMarker/LayerId', self.placeMarkLayer.layer.id())
            self.button_box.button(QDialogButtonBox.Apply).setEnabled(False)

    def exceptLayers(self):
#         print 'exceptLayers'
        excepted = []
        for i in range(self.mMapLayerComboBox.count()):
            l = self.mMapLayerComboBox.layer(i)
            if not self.placeMarkLayer.checkLayer(l):
                excepted.append(l)
        self.mMapLayerComboBox.setExceptedLayerList(self.mMapLayerComboBox.exceptedLayerList() + excepted)

    @pyqtSlot(name='on_repaintTimer_timeout')
    def repaintTrigger(self):
        for i in range(self.mMapLayerComboBox.count()):
            l = self.mMapLayerComboBox.layer(i)
            ids = l.allFeatureIds()
            try:
                if self.layerfeatureCount[l.id()] != len(ids):
                    self.layerfeatureCount[l.id()] = len(ids)
                    l.triggerRepaint()
#                     print 'Repaint', l.name()
            except KeyError:
                self.layerfeatureCount[l.id()] = len(ids)

    @pyqtSlot(bool, name='on_checkBoxAutoRefresh_toggled')
    def toggleAutoRefresh(self, checked):
        if checked:
            self.repaintTimer.start(REFRESH_RATE)
        else:
            self.repaintTimer.stop()
        settings = QSettings()
        settings.setValue(u'PlaceMarker/AutoRefreshLayer', checked)
