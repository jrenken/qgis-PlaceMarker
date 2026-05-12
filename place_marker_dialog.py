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
import re
from qgis.gui import QgsMapTool, QgsMessageBar
from qgis.PyQt.QtCore import (
    Qt,
    QObject,
    pyqtSlot,
    QDateTime,
    QByteArray,
    QSettings,
    QTimer,
    QModelIndex,)
from qgis.core import (
    Qgis,
    QgsPointXY,
    QgsCoordinateTransform,
    QgsMapLayerProxyModel,
    QgsCoordinateReferenceSystem,
    QgsCoordinateFormatter as cf,
    QgsProject)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QAbstractButton,
    QAction,
    QSizePolicy)
from qgis.PyQt.QtGui import QKeySequence
from .layer_dialog import LayerDialog
from .placemark_layer import PlaceMarkLayer
from .ui_place_marker_dialog_base import Ui_PlaceMarkerDialogBase
from .place_marker_maptool import PlaceMarkerMapTool

REFRESH_RATE = 5000


class PlaceMarkerDialog(QDialog, Ui_PlaceMarkerDialogBase):

    DEFAULT_CLASSES = [u'Interesting', u'Danger', u'Stay away']

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(PlaceMarkerDialog, self).__init__(parent)
        self.setupUi(self)
        self.bar = QgsMessageBar(self)
        self.bar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        self.layout().insertRow(self.layout().rowCount() - 1, self.bar)
        self.placeMarkLayer = PlaceMarkLayer()
        self.mMapLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)
        hb = self.button_box.button(QDialogButtonBox.StandardButton.Help)
        if hb:
            hb.setDefault(False)
            hb.setAutoDefault(False)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setDefault(True)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.iface = iface
        QgsProject.instance().layersAdded.connect(self.updateLayerList)
        settings = QSettings()
        try:
            self.restoreGeometry(settings.value(u'/Windows/PlaceMarker/geometry', QByteArray(), type=QByteArray))
            classes = settings.value(u'PlaceMarker/Classes',
                                 defaultValue=self.DEFAULT_CLASSES, type=str)
            self.comboBoxClass.addItems(classes)
        except TypeError:
            self.comboBoxClass.addItems(self.DEFAULT_CLASSES)

        delClassAction = QAction(self.tr(u'Remove current class'), self.comboBoxClass)
        delClassAction.setShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Delete))
        delClassAction.triggered.connect(self.removeClass)
        self.comboBoxClass.addAction(delClassAction)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        self.mapTool = PlaceMarkerMapTool(self.iface.mapCanvas())
        self.mapTool.canvasClicked.connect(self.mouseClicked)
        self.comboBoxClass.model().rowsInserted.connect(self.classChanged)
        self.comboBoxClass.model().rowsRemoved.connect(self.classChanged)
        self.crsXform = QgsCoordinateTransform()
        self.crsXform.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        self.changeCrs()
        self.iface.mapCanvas().destinationCrsChanged.connect(self.changeCrs)
        self.iface.mapCanvas().mapToolSet[QgsMapTool, QgsMapTool].connect(self.mapToolChanged)
        self.pos = None
        self.layerId = None
        self.layerChanged = False
        self.mMapLayerComboBox.layerChanged.connect(self.changeLayer)
        self.repaintTimer = QTimer()
        self.repaintTimer.timeout.connect(self.repaintTrigger)
        self.layerfeatureCount = dict()
        tr = QObject()
        self.hemis = tr.tr('N') + tr.tr('S') + tr.tr('E') + tr.tr('W')
        self.negative = f'{self.hemis[1]}{self.hemis[3]}-'
        self.reDms = re.compile(r'^\s*(?:([-+{0}])\s*)?(\d{{1,3}})(?:[^0-9.]+([0-5]?\d))?[^0-9.]+([0-5]?\d(?:[\.,]\d+)?)[^0-9.{0}]*([{0}])?\s*$'
                             .format(self.hemis))
        self.reDec2 = re.compile(r'([+-]?\d+\.?\d*)°?([{0}])?[\.\,\s]+([+-]?\d+\.?\d*)°?([{1}])?'.format(self.hemis[:2], self.hemis[2:]))
        self.coordFmt = (cf.FormatDegreesMinutes, cf.FlagDegreesUseStringSuffix)
        try:
            self.sep = cf.separator() + ' '
        except AttributeError:
            self.sep = ', '

    def showEvent(self, event):
        self.exceptLayers()
        settings = QSettings()
        self.layerId = settings.value(u'PlaceMarker/LayerId', None)
        layer = QgsProject.instance().mapLayer(self.layerId)
        if layer:
            self.mMapLayerComboBox.setLayer(layer)
        layer = self.mMapLayerComboBox.currentLayer()
        if layer:
            self.placeMarkLayer.setLayer(layer)
        self.iface.mapCanvas().setMapTool(self.mapTool)
        refresh = settings.value(u'PlaceMarker/AutoRefreshLayer', False, type=bool)
        self.comboBoxClass.setCurrentIndex(settings.value(u'PlaceMarker/CurrentClass', 0, type=int))
        self.checkBoxAutoRefresh.setChecked(refresh)
        self.lineEditPosition.setFocus()
        QDialog.showEvent(self, event)

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue(u'/Windows/PlaceMarker/geometry', self.saveGeometry())
        settings.setValue(u'PlaceMarker/CurrentClass', self.comboBoxClass.currentIndex())
        QDialog.closeEvent(self, event)

    def hideEvent(self, event):
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
        self.lineEditPosition.setText(u'')
        self.mapTool.reset()
        QDialog.hideEvent(self, event)

    @pyqtSlot(QgsPointXY, Qt.MouseButton)
    def mouseClicked(self, pos, button):
        if button == Qt.MouseButton.LeftButton:
            self.show()
            self.pos = pos
            self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)
            self.mDateTimeEdit.setDateTime(QDateTime.currentDateTime().toUTC())
            self.geoPos = self.crsXform.transform(self.pos)
            self.lineEditPosition.setText(self.sep.join(
                (cf.formatY(self.geoPos.y(), self.coordFmt[0], 4, self.coordFmt[1]),
                 cf.formatX(self.geoPos.x(), self.coordFmt[0], 4, self.coordFmt[1]))))
            self.lineEditName.setFocus()

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
        dlg.exec()

    @pyqtSlot(name='on_toolButtonApplyStyle_clicked')
    def applyPresetStyle(self):
        self.placeMarkLayer.applyPresetStyle()

    # @pyqtSlot(QgsMapLayer, name='on_mMapLayerComboBox_layerChanged')
    def changeLayer(self, layer):
        self.placeMarkLayer.setLayer(layer)
        self.layerChanged = True

    @pyqtSlot(QgsMapTool, QgsMapTool)
    def mapToolChanged(self, mapToolNew, mapToolOld):
        if mapToolOld == self.mapTool and mapToolNew != self.mapTool:
            self.close()

    @pyqtSlot(QAbstractButton, name='on_button_box_clicked')
    def applyNewPlacemark(self, button):
        if self.button_box.buttonRole(button) == QDialogButtonBox.ButtonRole.ApplyRole:
            if self.pos and self.lineEditName.text():
                res = self.placeMarkLayer.addPlaceMark(self.geoPos,
                                                 self.lineEditName.text(),
                                                 self.lineEditDescription.text(),
                                                 self.comboBoxClass.currentText(),
                                                 self.mDateTimeEdit.dateTime().toString(self.mDateTimeEdit.displayFormat()))
                if res:
                    self.placeMarkLayer.layer.triggerRepaint()
                self.mapTool.reset()
                self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
            if self.layerChanged and self.placeMarkLayer.layer:
                settings = QSettings()
                settings.setValue(u'PlaceMarker/LayerId', self.placeMarkLayer.layer.id())
        elif self.button_box.buttonRole(button) == QDialogButtonBox.ButtonRole.RejectRole:
            self.mapTool.reset()

    def exceptLayers(self):
        excepted = []
        self.mMapLayerComboBox.setExceptedLayerList(excepted)
        for i in range(self.mMapLayerComboBox.count()):
            layer = self.mMapLayerComboBox.layer(i)
            if not self.placeMarkLayer.checkLayer(layer):
                excepted.append(layer)
        self.mMapLayerComboBox.setExceptedLayerList(excepted)

    @pyqtSlot(name='on_repaintTimer_timeout')
    def repaintTrigger(self):
        for i in range(self.mMapLayerComboBox.count()):
            layer = self.mMapLayerComboBox.layer(i)
            ids = layer.allFeatureIds()
            try:
                if self.layerfeatureCount[layer.id()] != len(ids):
                    self.layerfeatureCount[layer.id()] = len(ids)
                    layer.triggerRepaint()
            except KeyError:
                self.layerfeatureCount[layer.id()] = len(ids)

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

    def updateLayerList(self, layers):
        self.exceptLayers()

    @pyqtSlot(name='on_lineEditPosition_editingFinished')
    def positionEditingFinished(self):
        if not self.lineEditPosition.text():
            return
        posText = self.lineEditPosition.text().upper()
        (lat, lon, ok) = self.decimalStringToDoubles(posText.replace(',', '.'))
        if not ok:
            latlon = re.split(r'[,\s]+', posText)
            if len(latlon) > 2:
                latlon = re.split(r'\s+', posText)
            try:
                (lat, ok) = self.dmsStringToDouble(latlon[0].replace(',', '.'))
                if ok:
                    (lon, ok) = self.dmsStringToDouble(latlon[1].replace(',', '.'), 180.0)
            except IndexError:
                ok = False

        if ok:
            self.geoPos = QgsPointXY(lon, lat)
            self.pos = self.crsXform.transform(self.geoPos, QgsCoordinateTransform.ReverseTransform)
            self.mapTool.setMarkerPosition(self.pos)
            self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)
        else:
            self.bar.pushMessage(self.tr("Position"), self.tr("Invalid coordinate format"),
                                level=Qgis.Warning, duration=2)
            self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
            self.mapTool.reset()

    def decimalStringToDoubles(self, sYX):
        x = 0.0
        y = 0.0
        match = self.reDec2.match(sYX)
        # ok = not self.reDec2.indexIn(sYX)
        # if not ok:
        if not match or (match.lastindex < 3):
            return (y, x, False)

        try:
            y = float(match[1])
            x = float(match[3])
        except ValueError:
            return (y, x, False)
        try:
            if match[2] == self.hemis[1]:
                y = -y
            if match[4] == self.hemis[3]:
                x = -x
        except IndexError:
            pass
        if not -90.0 < y <= 90.0 or not -180.0 < x <= 180.0:
            return (y, x, False)
        return (y, x, True)

    def dmsStringToDouble(self, sX, extend=90.0):
        x = 0.0
        match = self.reDms.match(sX)
        if not match:
            return (x, False)
        try:
            dms1 = match[2]
            dms2 = match[3]
            dms3 = match[4]
            x = float(dms3)
            if dms2:
                x = int(dms2) + x / 60.0
            x = int(dms1) + x / 60.0
            sign1 = match[1]
            sign2 = match[5]
            if not sign1:
                if sign2 and sign2 in self.negative:
                    x = -x
            elif not sign2:
                if sign1 and sign1 in self.negative:
                    x = -x
            else:
                return (x, False)
        except (ValueError, IndexError):
            return (0.0, False)

        if not -extend < x <= extend:
            return (x, False)
        return (x, True)
