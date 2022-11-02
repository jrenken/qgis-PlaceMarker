# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DropLineEdit
                                 A QGIS plugin
 Place Marker offers a convenient way of setting placemarks in a vector layer
                             -------------------
        begin                : 2022-10-13
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Jens Renken (Marum/University of Bremen)
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

from qgis.PyQt.QtWidgets import QLineEdit
from qgis.PyQt.QtCore import Qt


class DropLineEdit(QLineEdit):
    '''
    QLineEdit that overwrites the current content when dropping with shift pressed
    '''

    def dropEvent(self, e):
        if e.keyboardModifiers() & Qt.ShiftModifier:
            self.clear()
        super(DropLineEdit, self).dropEvent(e)
