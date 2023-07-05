.. PlaceMarker documentation master file, created by
   sphinx-quickstart on Sun Feb 12 17:11:03 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PlaceMarker's documentation
============================================

.. toctree::
   :maxdepth: 2

Concepts
==================
Place Marker offers a convenient way of creating and handling placemarks in a vector layer. 
The preferred dataproviders for the layer are Spatialite or PostgreSQL. 
This facilitates synchronization of placemarks across multiple running QGIS instances. 
The plugin also works with other vector data providers, provided the required attributes in the layer are present.
Creating a new layer is only supported for Spatialite, PostgreSQL and temporary scratch layers.

.. index:: Configuration and Operation
 
Configuration and Operation
============================

#. Activate the dialog by clicking on the toolbutton or on the plugin menu entry.
#. Select a layer from the combo box. The available layers meet the necessary requirements.
#. If desired, apply the preset style. This will add comment fields for lat/lon and, if not provided by the database, a unique id.
#. If no layer is available, create a Spatialite or PostGIS layer and,
   if necessary, a new Spatialite database by clicking on the toolbutton. Creating a Temporary Scratch Layer is also possible
   The new layer contains the necessary attributes.
#. To set a placemark, click on the canvas. The geographic position will be displayed and the time will be updated.
   The position can be edited. Valid formats are decimal degrees, degrees/minutes and degrees/minutes/seconds
   with or without suffix and separated by comma.
#. It is also possible to drag and drop position text into the position widget. Holding the left shift key will add the text, otherwise it will be replaced.
   To confirm the placemark click **Apply**
#. By checking the **Autorefresh** box, the layers are checked every five seconds for modifications 
   and will be repainted if necessary.

.. index:: General Hints

General Hints
==================
* A basic labeling is applied to new layers by pressing the Style Button in the upper right corner.
* The appearence of the symbols can be changed in the layer properties.
* The class can be used to apply different symbols
  depending on the class. Select *Categorized* or *Rule-based* in the style panel of the layer properties.
* The class combo box can be extended by additional classes. Remove a class with *CTRL-Delete*


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

