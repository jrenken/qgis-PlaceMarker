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
from qgis.gui import QgsMapToolEmitPoint, QgsMapTool
from PyQt4.QtCore import Qt, pyqtSignal, pyqtSlot, QDateTime, QByteArray,\
    QSettings, QTimer, QModelIndex, QPoint
from qgis.core import QgsPoint, QgsCoordinateTransform, \
    QgsCoordinateReferenceSystem, QgsMapLayer
from layer_dialog import LayerDialog
from placemark_layer import PlaceMarkLayer
from qgis.core import QgsMapLayerRegistry
from PyQt4.QtGui import QDialogButtonBox, QAbstractButton, QAction, QKeySequence
from ui_place_marker_dialog_base import Ui_PlaceMarkerDialogBase

REFRESH_RATE = 5000

class PlaceMarkerDialog(QtGui.QDialog, Ui_PlaceMarkerDialogBase):

    mouseClicked = pyqtSignal(QgsPoint, Qt.MouseButton)
    
    DEFAULT_CLASSES = [u'Interesting', u'Danger', u'Stay away']

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(PlaceMarkerDialog, self).__init__(parent)
        self.setupUi(self)
        hb = self.button_box.button(QDialogButtonBox.Help)
        if hb:
            hb.setDefault(False)
            hb.setAutoDefault(False)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.iface = iface
        settings = QSettings()
        try:
            self.restoreGeometry(settings.value(u'/Windows/PlaceMarker/geometry', QByteArray(), type=QByteArray))
            classes = settings.value(u'PlaceMarker/Classes', 
                                 defaultValue=self.DEFAULT_CLASSES, type=str)
            self.comboBoxClass.addItems(classes)
        except TypeError:
            self.comboBoxClass.addItems(self.DEFAULT_CLASSES)

        delClassAction = QAction(self.tr(u'Remove current class'), self.comboBoxClass)
        delClassAction.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Delete))
        delClassAction.triggered.connect(self.removeClass)
        self.comboBoxClass.addAction(delClassAction)
        self.button_box.button(QDialogButtonBox.Apply).setEnabled(False)
        self.mapTool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self.mapTool.canvasClicked.connect(self.mouseClicked)
        self.comboBoxClass.model().rowsInserted.connect(self.classChanged)
        self.comboBoxClass.model().rowsRemoved.connect(self.classChanged)
        self.crsXform = QgsCoordinateTransform()
        self.crsXform.setDestCRS(QgsCoordinateReferenceSystem(4326))
        self.changeCrs()
        self.iface.mapCanvas().destinationCrsChanged.connect(self.changeCrs)
        self.iface.mapCanvas().mapToolSet[QgsMapTool, QgsMapTool].connect(self.mapToolChanged)
        self.pos = None
        self.layerId = None
        self.layerChanged = False
        self.placeMarkLayer = PlaceMarkLayer()
        self.repaintTimer = QTimer()
        self.repaintTimer.timeout.connect(self.repaintTrigger)
        self.layerfeatureCount = dict()

        

    def showEvent(self, event):
        self.exceptLayers()
        settings = QSettings()
        self.layerId = settings.value(u'PlaceMarker/LayerId', None)
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
        settings.setValue(u'/Windows/PlaceMarker/geometry', self.saveGeometry());
        QtGui.QDialog.closeEvent(self, event)
        self.button_box.button(QDialogButtonBox.Apply).setEnabled(False)
        self.lineEditPosition.setText(u'')

    @pyqtSlot(QgsPoint, Qt.MouseButton)
    def mouseClicked(self, pos, button):
        if button == Qt.LeftButton:
            self.show()
            self.pos = pos
            self.button_box.button(QDialogButtonBox.Apply).setEnabled(True)
            self.mDateTimeEdit.setDateTime(QDateTime.currentDateTime().toUTC())
            self.geoPos = self.crsXform.transform(self.pos)
            self.lineEditPosition.setText(', '.join(self.geoPos.toDegreesMinutes(5, True, True).rsplit(',')[::-1]))

#     @pyqtSlot()
#     def accept(self):
#         QtGui.QDialog.reject(self)
# 
#     @pyqtSlot()
#     def reject(self):
#         QtGui.QDialog.reject(self)

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
        self.placeMarkLayer.setLayer(layer)
        self.layerChanged = True

    @pyqtSlot(QgsMapTool, QgsMapTool)
    def mapToolChanged(self, mapToolNew, mapToolOld):
        if mapToolOld == self.mapTool and mapToolNew != self.mapTool:
            self.close()

    @pyqtSlot(QAbstractButton, name='on_button_box_clicked')
    def applyNewPlacemark(self, button):
        if self.button_box.buttonRole(button) == QDialogButtonBox.ApplyRole:
            if self.pos and self.lineEditName.text():
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

    @pyqtSlot(name='on_button_box_helpRequested')
    def showHelp(self):
        url = 'file://' + os.path.join(os.path.dirname(__file__), 'help', 'index.html')
        self.iface.openURL(url, False)

    @pyqtSlot(QModelIndex, int, int)
    def classChanged(self, idx, start, end):
        settings = QSettings()
        sl = []
        for i in range(self.comboBoxClass.count()):
            sl.append(self.comboBoxClass.itemText(i))
        settings.setValue(u'PlaceMarker/Classes', sl)

    @pyqtSlot()
    def removeClass(self):
        if self.comboBoxClass.hasFocus():
            i = self.comboBoxClass.currentIndex()
            if i > -1:
                self.comboBoxClass.removeItem(i)
