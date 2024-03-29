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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSlot, QSettings, QFileInfo, QVariant
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QSizePolicy
from qgis.core import Qgis, QgsDataSourceUri, QgsVectorLayer, QgsProject, QgsField
from qgis.utils import spatialite_connect
from qgis.gui import QgsMessageBar
from sqlite3 import OperationalError
import psycopg2
from qgis._core import QgsCredentials

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer_dialog_base.ui'))


class LayerDialog(QDialog, FORM_CLASS):
    '''
    Dialogue for creating a new spatialite vector layer.
    If needed a new database file can also be created.
    '''

    def __init__(self, iface, parent=None):
        '''
        Constructor
        '''
        super(LayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.bar = QgsMessageBar(self)
        self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout().addWidget(self.bar)
        self.iface = iface
        settings = QSettings()
        settings.beginGroup('/SpatiaLite/connections')
        self.mDatabaseComboBox.clear()
        for k in settings.childGroups():
            text = settings.value(k + '/sqlitepath', '###unknown###')
            self.mDatabaseComboBox.addItem(text)
        settings.endGroup()
        settings.beginGroup('PostgreSQL/connections')
        for k in settings.childGroups():
            text = 'postgres://{}@{}'.format(settings.value(k + '/database', '###unknown###'),
                                               settings.value(k + '/host', '###unknown###'))

            self.mDatabaseComboBox.addItem(text)
        settings.endGroup()
        self.mDatabaseComboBox.addItem(self.tr("Temporary Scratch Layer"))
        self.mOkButton = self.buttonBox.button(QDialogButtonBox.Ok)

    @pyqtSlot(name='on_toolButtonNewDatabase_clicked')
    def newDataBase(self):
        fileName, __ = QFileDialog.getSaveFileName(self, self.tr('New SpatiaLite Database File'), '.',
                                               self.tr('SpatiaLite') + '(*.sqlite *.db)')
        if not fileName:
            return

        if not fileName.lower().endswith('.sqlite') and not fileName.lower().endswith('.db'):
            fileName += ".sqlite"

        if self.createDb(fileName):
            self.mDatabaseComboBox.insertItem(0, fileName)
            self.mDatabaseComboBox.setCurrentIndex(0)

    def createDb(self, fileName):
        '''Create a new spatialite database file
        :param fileName: the filename of the database file
        :returns: True if the file could be created
        :rtype: bool
        '''
        try:
            db = spatialite_connect(fileName)
            cur = db.cursor()
        except OperationalError:
            self.bar.pushMessage(self.tr("SpatiaLite Database"), self.tr("Unable to create database file!"),
                                 level=Qgis.Critical)
            return False

        try:
            db.enable_load_extension(True)
        except OperationalError:
            self.bar.pushMessage(self.tr("SpatiaLite Database"), self.tr("SQLITE Load_extension off!"),
                                 level=Qgis.Info)

        cur.execute("Select initspatialmetadata(1);")
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
            self.bar.pushMessage(self.tr("SpatiaLite Database"), self.tr("Registered new database!"),
                                 level=Qgis.Success)
        return True

    def createLayer(self):
        '''
        Create a layer with the required attributes and add the layer to the canvas.
        The database is taken from database combobox. The database needs to be registered.
        '''

        sqlGeom = u'select AddGeometryColumn(%s,%s,%d,%s,2)' % (self.quotedValue(self.leLayerName.text()),
                                                                self.quotedValue('Geometry'),
                                                                4326,
                                                                self.quotedValue('POINT'))

        uri = QgsDataSourceUri()
        layer = QgsVectorLayer()

        if self.mDatabaseComboBox.currentText().startswith('postgres://'):
            sql = u'create table ' + self.quotedIdentifier(self.leLayerName.text()) + '('
            sql += u'pkuid serial primary key,'
            sql += u'name varchar(255),description varchar(255),class varchar(255), timestamp varchar(255))'

            try:
                dbn = self.mDatabaseComboBox.currentText().split('://')[1].split('@')
                realm = 'dbname=\'{}\' host={} port=5432'.format(dbn[0], dbn[1])
                for i in range(3):
                    (valid, usr, pw) = QgsCredentials.instance().get(realm, '', '')
                    if valid:
                        QgsCredentials.instance().put(realm, usr, pw)
                        db = psycopg2.connect(dbname=dbn[0], host=dbn[1], user=usr, password=pw)
                        cur = db.cursor()
                        cur.execute(sql)
                        cur.execute(sqlGeom)
                        db.commit()
                        db.commit()
                        db.close()
                        break
                if i == 2:
                    raise psycopg2.InterfaceError
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                self.iface.messageBar().pushMessage(self.tr("PostGIS Database"), self.tr("Could not create a new layer!"),
                                     level=Qgis.Critical, duration=5)
                return

            uri.setConnection(aHost=dbn[1], aPort='5432', aDatabase=dbn[0], aUsername=usr, aPassword=pw)
            schema = 'public'
            table = self.leLayerName.text()
            geom_column = 'Geometry'
            uri.setDataSource(schema, table, geom_column)
            display_name = self.leLayerName.text()
            layer = QgsVectorLayer(uri.uri(), display_name, 'postgres')

        elif os.path.splitext(self.mDatabaseComboBox.currentText())[1] == '.sqlite':
            sql = u'create table ' + self.quotedIdentifier(self.leLayerName.text()) + '('
            sql += u'pkuid integer primary key autoincrement,'
            sql += u'name text,description text,class text, timestamp text)'
            sqlIndex = u'select CreateSpatialIndex(%s,%s)' % (self.quotedValue(self.leLayerName.text()),
                                                              self.quotedValue('Geometry'))
            try:
                db = spatialite_connect(self.mDatabaseComboBox.currentText())
                cur = db.cursor()
                cur.execute(sql)
                cur.execute(sqlGeom)
                cur.execute(sqlIndex)
                db.commit()
                db.close()
            except OperationalError:
                self.iface.messageBar().pushMessage(self.tr("SpatiaLite Database"), self.tr("Could not create a new layer!"),
                                     level=Qgis.Critical, duration=5)
                return

            uri.setDatabase(self.mDatabaseComboBox.currentText())
            schema = ''
            table = self.leLayerName.text()
            geom_column = 'Geometry'
            uri.setDataSource(schema, table, geom_column)
            display_name = self.leLayerName.text()
            layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')

        else:
            uri = 'point?crs=epsg:4326&field=name:string' \
                    '&field=description:string' \
                    '&field=class:string' \
                    '&field=timestamp:string'
            layer = QgsVectorLayer(uri, self.leLayerName.text(), 'memory')

        if layer.isValid():
            layer.loadNamedStyle(':/plugins/PlaceMarker/Styles/default_style.qml')
            QgsProject.instance().addMapLayer(layer)

    def quotedIdentifier(self, idf):
        idf = idf.replace('\"', '\"\"')
        return '\"' + idf + '\"'

    def quotedValue(self, value):
        value = value.replace('\'', '\'\'')
        return '\'' + value + '\''

    @pyqtSlot(name='on_pushButtonNewLayer_clicked')
    def newLayer(self):
        self.iface.newLayerMenu().popup(self.pos())

    @pyqtSlot()
    def accept(self):
        if not self.leLayerName.text():
            self.bar.pushMessage(self.tr("Database"), self.tr("Need a layer name"),
                                 level=Qgis.Warning)
        else:
            self.createLayer()
            QDialog.accept(self)
