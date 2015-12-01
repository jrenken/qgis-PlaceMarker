# -*- coding: utf-8 -*-
'''
Created on 01.11.2015

@author: jrenken
'''

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSlot
from placemark_layer import checkLayer

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
        excepted = []
        for i in range(self.mMapLayerComboBox.count()):
            l = self.mMapLayerComboBox.layer(i)
            if not checkLayer(l):
                excepted.append(l)
                print "Except", l.name()
        self.mMapLayerComboBox.setExceptedLayerList(excepted)

    def currentLayer(self):
        return self.mMapLayerComboBox.currentLayer()
    
    @pyqtSlot(name='on_pushButtonNewLayer_clicked')
    def newLayer(self):
        self.iface.newLayerMenu().popup(self.pos())
