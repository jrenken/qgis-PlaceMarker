# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerDialog
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
from PyQt4.QtCore import pyqtSlot, QSettings, QFileInfo
from PyQt4.QtGui import QDialogButtonBox, QFileDialog, QSizePolicy
from qgis._core import QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry
from pyspatialite import dbapi2 as sqlite
from qgis._gui import QgsMessageBar

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer_dialog_base.ui'))


class LayerDialog(QtGui.QDialog, FORM_CLASS):
    '''
    classdocs
    '''


    def __init__(self, iface, parent=None):
        '''
        Constructor
        '''
        super(LayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.bar = QgsMessageBar(self)
        self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.layout().addWidget(self.bar)
        self.iface = iface
        settings = QSettings()
        settings.beginGroup( '/SpatiaLite/connections' )
        self.mDatabaseComboBox.clear()
        for k in settings.childGroups():
            text = settings.value(k + '/sqlitepath', '###unknown###')
            self.mDatabaseComboBox.addItem(text)
        settings.endGroup()
        self.mOkButton = self.buttonBox.button(QDialogButtonBox.Ok)

    @pyqtSlot(name='on_toolButtonNewDatabase_clicked')
    def newDataBase(self):
        fileName = QFileDialog.getSaveFileName(self, self.tr('New SpatiaLite Database File'), '.', 
                                               self.tr('SpatiaLite') + '(*.sqlite *.db)')
        if not fileName:
            return;

        if not fileName.lower().endswith('.sqlite') and not fileName.lower().endswith('.db'):
            fileName += ".sqlite";

        if self.createDb(fileName):
            self.mDatabaseComboBox.insertItem(0, fileName)
            self.mDatabaseComboBox.setCurrentIndex(0)

    def createDb(self, fileName):
        '''
        '''
        print 'create db', fileName
        db = sqlite.connect(fileName)
        cur = db.cursor()
        
        try:
            db.enable_load_extension(True)
        except:
            print "SQLITE Load_extension off"

        cur.execute("Select initspatialmetadata(1)")
        db.commit()
        db.close

        fi = QFileInfo(fileName)
        if not fi.exists():
            return False

        key = u'/SpatiaLite/connections/' + fi.fileName() + u'/sqlitepath'

        settings = QSettings()
        if not settings.contains(key):
            settings.setValue('/SpatiaLite/connections/selected', fi.fileName() + self.tr('@') + fi.canonicalFilePath())
            settings.setValue(key, fi.canonicalFilePath())
            self.bar.pushMessage(self.tr("SpatiaLite Database"), self.tr( "Registered new database!" ),
                                 level=QgsMessageBar.INFO)
        return True;

    def createLayer(self):
        '''
        '''
        sql = u'create table ' + self.quotedIdentifier(self.leLayerName.text()) + '('
        sql += u'pkuid integer primary key autoincrement,'
        sql += u'name text,description text,class text, timestamp text)'
        print sql

        sqlGeom = u'select AddGeometryColumn(%s,%s,%d,%s,2)' % (self.quotedValue(self.leLayerName.text()),
                                                                self.quotedValue('Geometry'), 
                                                                4326, 
                                                                self.quotedValue('POINT'))
        print sqlGeom

        sqlIndex = u'select CreateSpatialIndex(%s,%s)' % (self.quotedValue(self.leLayerName.text()),
                                                         self.quotedValue('Geometry'))
        print sqlIndex

        db = sqlite.connect(self.mDatabaseComboBox.currentText())
        cur = db.cursor()
        cur.execute(sql)
        cur.execute(sqlGeom)
        cur.execute(sqlIndex)
        
        uri = QgsDataSourceURI()
        uri.setDatabase(self.mDatabaseComboBox.currentText())
        schema = ''
        table = self.leLayerName.text()
        geom_column = 'Geometry'
        uri.setDataSource(schema, table, geom_column)
        display_name = self.leLayerName.text()
        layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
        
        if layer.isValid():
            print 'Layer valid'
            QgsMapLayerRegistry.instance().addMapLayer(layer)
        db.close()

    def quotedIdentifier(self, id):
        id = id.replace('\"', '\"\"')
        return '\"' + id + '\"'
        
    def quotedValue(self, value):
        value = value.replace('\'', '\'\'')
        return '\'' + value + '\''
    
    @pyqtSlot(name='on_pushButtonNewLayer_clicked')
    def newLayer(self):
        self.iface.newLayerMenu().popup(self.pos())

    @pyqtSlot()
    def accept(self):
        if not self.leLayerName.text():
            self.bar.pushMessage(self.tr("SpatiaLite Database"), self.tr("Need a layer name"),
                                 level=QgsMessageBar.WARNING)
        else:
            self.createLayer()
            QtGui.QDialog.accept(self)