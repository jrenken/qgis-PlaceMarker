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

from PyQt5.QtWidgets import QLineEdit


class DropLineEdit(QLineEdit):
    '''
    QLineEdit that overwrites the current content on drop event
    '''

    def dropEvent(self, e):
        self.setText(e.mimeData().text())
        e.accept()
