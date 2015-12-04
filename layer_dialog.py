# -*- coding: utf-8 -*-
'''
Created on 01.11.2015

@author: jrenken
'''

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot, QSettings, QFile, QLibrary, QFileInfo
from placemark_layer import checkLayer
from PyQt4.QtGui import QDialogButtonBox, QFileDialog, QMessageBox
from qgis._core import QgsProviderRegistry, QgsDataSourceURI, QgsVectorLayer,\
    QgsMapLayerRegistry
from pyspatialite import dbapi2 as sqlite

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
        self.iface = iface
        settings = QSettings()
        settings.beginGroup( '/SpatiaLite/connections' )
        self.mDatabaseComboBox.clear()
        for k in settings.childGroups():
            text = settings.value(k + '/sqlitepath', '###unknown###')
            self.mDatabaseComboBox.addItem(text)
        settings.endGroup()
        self.mOkButton = self.buttonBox.button(QDialogButtonBox.Ok)
        
#         excepted = []
#         for i in range(self.mMapLayerComboBox.count()):
#             l = self.mMapLayerComboBox.layer(i)
#             if not checkLayer(l):
#                 excepted.append(l)
#                 print "Except", l.name()
#         self.mMapLayerComboBox.setExceptedLayerList(excepted)

    @pyqtSlot(name='on_toolButtonNewDatabase_clicked')
    def newDataBase(self):
        fileName = QFileDialog.getSaveFileName(self, self.tr('New SpatiaLite Database File'), '.', 
                                               self.tr('SpatiaLite') + '(*.sqlite *.db)')
        if not fileName:
            return;

        if  not fileName.lower().endswith('.sqlite') and not fileName.lower().endswith('.db'):
            fileName += ".sqlite";

        self.mDatabaseComboBox.insertItem(0, fileName)
        self.mDatabaseComboBox.setCurrentIndex(0)
        self.createDb(fileName);


    def createDb(self, fileName):
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
            settings.setValue( '/SpatiaLite/connections/selected', fi.fileName() + self.tr( "@" ) + fi.canonicalFilePath())
            settings.setValue( key, fi.canonicalFilePath() );
 
#             QMessageBox.information( 0, self.tr( "SpatiaLite Database" ), self.tr( "Registered new database!" ) );
        return True;

    def createLayer(self):
        sql = u'create table ' + self.quotedIdentifier(self.leLayerName.text()) + '('
        sql += u'pkuid integer primary key autoincrement,'
        sql += u'name text,description text,class text, datetime text)'
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
#             self.iface.addVectorLayer(layer)
        db.close()
        
        
        

#     def createDb(self):
#         dbPath = self.mDatabaseComboBox.currentText();
#         if not dbPath:
#             return False
# 
#         newDb = QFile(dbPath)
#         if not newDb.exists():
#             res = False
# 
#             spatialite_lib = QgsProviderRegistry.instance().library('spatialite')
#             myLib = QLibrary(spatialite_lib)
#             loaded = myLib.load()
#             if loaded:
#                 print('spatialite provider loaded')
# 
#                 createDbPtr = myLib.resolve('createDb')
#                 if createDbPtr:
#                     res = createDbPtr(dbPath)
#                 else:
#                     errCause = "Resolving createDb(...) failed";
# 
#         if not res:
#             QMessageBox.warning(0, tr('SpatiaLite Database'), errCause);
# 
#         fi = QFileInfo(newDb)
#         if not fi.exists():
#             return False
# 
#         key = u'/SpatiaLite/connections/' + fi.fileName() + u'/sqlitepath'
# 
#         settings = QSettings()
#         if not settings.contains(key):
#             settings.setValue( '/SpatiaLite/connections/selected', fi.fileName() + tr( "@" ) + fi.canonicalFilePath())
#             settings.setValue( key, fi.canonicalFilePath() );
# 
#             QMessageBox.information( 0, tr( "SpatiaLite Database" ), tr( "Registered new database!" ) );
# 
#         return True;
        
    def quotedIdentifier(self, id):
        id = id.replace('\"', '\"\"')
        return '\"' + id + '\"'
        
    def quotedValue(self, value):
        value = value.replace('\'', '\'\'')
        return '\'' + value + '\''
    
    def currentLayer(self):
#         return self.mMapLayerComboBox.currentLayer()
        return None
    
    @pyqtSlot(name='on_pushButtonNewLayer_clicked')
    def newLayer(self):
        self.iface.newLayerMenu().popup(self.pos())

    @pyqtSlot()
    def accept(self):
        self.createLayer()
        print 'accept'
        QtGui.QDialog.accept(self)
