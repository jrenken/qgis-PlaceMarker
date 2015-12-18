.. PlaceMarker documentation master file, created by
   sphinx-quickstart on Sun Feb 12 17:11:03 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PlaceMarker's documentation!
============================================

Contents:

.. toctree::
   :maxdepth: 2

Concepts
==================
Placemarker offers a convenient way of placing markers on a vector layer. The preferred dataprovider is spatialite.
This eases the synchronisation of placemarks between several QGis instances.
The plugin also works with other vector data providers if the required attributes are present in the layer.
Creation of a new layer is only available for spatialite.



.. index:: Configuration and Operation
 
Configuration and Operation
==================

#. Activate the dialog by clicking on the toolbutton or on the plugin menu entry.
#. Select a layer from the combobox. The available layersfullfill the necessary requirements.
#. If no layer is available a new spatialite layer and a databse if needed can be created by clicking on the toolbutton. The new layer contains the necessary attributes
#. In the layer properties enable labeling and configure symbols and symbol classification
#. To set a placemark click on the canvas. The geographic position is displayed and the time is updated. To confirm the placemark click **Apply**
#. By checking the **Autorefresh** box the layers are checked every five seconds for modifications and will then be repainted.

.. index:: General Hints

General Hints
==================


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

