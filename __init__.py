# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlaceMarker
                                 A QGIS plugin
 Place Marker offers a convenient way of setting placemarks in a vector layer
                             -------------------
        begin                : 2015-10-27
        copyright            : (C) 2015 by Jens Renken (Marum/University of Bremen)
        email                : renken@marum.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

import os

if os.name == 'nt':
    ''' Workaround for windows platform.
            Currently the qgis_customwidgets plugin is moved from
            the directory where it is searched to another directory.
            I don't know why
    '''

    import qgis
    from qgis.PyQt import uic

    uic.widgetPluginPath.append(os.path.normpath(
        os.path.join(qgis.__path__[0], '..', 'PyQt4', 'uic', 'widget-plugins')))


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PlaceMarker class from file PlaceMarker.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .place_marker import PlaceMarker
    return PlaceMarker(iface)
