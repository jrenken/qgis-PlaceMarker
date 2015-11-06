# -*- coding: utf-8 -*-
'''
Created on 01.11.2015

@author: jrenken
'''

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer_dialog_base.ui'))


class LayerDialog(QtGui.QDialog, FORM_CLASS):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(LayerDialog, self).__init__(parent)
        self.setupUi(self)

    def currentLayer(self):
        return self.mMapLayerComboBox.currentLayer()
        
