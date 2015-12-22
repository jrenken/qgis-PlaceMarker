# qgis-PlaceMarker

Place Marker offers a convenient way of creating and handling placemarks in a vector layer. 
The preferred dataprovider for the layer is Spatialite. This eases synchronisation of 
placemakers over multiple running QGIS instances.

## Features

The Plugin allows placement of markers in a vector layer without switching the layer to edit mode.
The layer needs to have a defined minimum set of attributes, e.g. name, description, class and timestamp.
The layer selection combobox only contains layers which fullfill these minimum reqirements.
The plugin can create and add a spatialite database and vector layer.
Basic labeling is enabled on newly created vector layers. 

## Installation

### via git

* Clone the repository
* Execute "make deploy" (works fluently only on Linux due to dependencies of QGIS custom widgets)

### via repo server

* Go to plugin manager
* Enable experimental plugins 
* Install PlaceMarker

## License

```
    Place Marker offers a convenient way of creating and handling placemarks in a vector layer. 

    Copyright (C) 2015 MARUM - Center for Marine Environmental Sciences

    PlaceMarker Plugin is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with PlaceMarker Plugin.  If not, see <http://www.gnu.org/licenses/>.
```

