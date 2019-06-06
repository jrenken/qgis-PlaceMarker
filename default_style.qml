<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.6.3-Noosa" styleCategories="Labeling|Fields|MapTips" labelsEnabled="1">
  <labeling type="simple">
    <settings>
      <text-style fontWeight="50" textOpacity="1" fontLetterSpacing="0" fontItalic="0" fontUnderline="0" blendMode="0" multilineHeight="1" previewBkgrdColor="#ffffff" useSubstitutions="0" fontStrikeout="0" namedStyle="Regular" fontCapitals="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSizeUnit="Point" fieldName="name" fontFamily="Ubuntu" fontSize="10" fontWordSpacing="0" isExpression="0" textColor="0,0,0,255">
        <text-buffer bufferBlendMode="0" bufferSize="1" bufferColor="255,255,255,255" bufferNoFill="1" bufferOpacity="1" bufferJoinStyle="128" bufferSizeUnits="MM" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferDraw="0"/>
        <background shapeType="0" shapeSizeX="0" shapeJoinStyle="64" shapeOffsetY="0" shapeFillColor="255,255,255,255" shapeOffsetX="0" shapeRadiiX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeY="0" shapeBorderWidth="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeBlendMode="0" shapeDraw="0" shapeOffsetUnit="MM" shapeBorderColor="128,128,128,255" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeRadiiY="0" shapeBorderWidthUnit="MM" shapeOpacity="1" shapeSVGFile="" shapeSizeUnit="MM" shapeSizeType="0" shapeRotationType="0"/>
        <shadow shadowColor="0,0,0,255" shadowUnder="0" shadowBlendMode="6" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetGlobal="1" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowOffsetDist="1" shadowScale="100" shadowOffsetAngle="135" shadowRadius="1.5" shadowOffsetUnit="MM" shadowDraw="0" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0"/>
        <substitutions/>
      </text-style>
      <text-format useMaxLineLengthForAutoWrap="1" addDirectionSymbol="0" rightDirectionSymbol=">" reverseDirectionSymbol="0" wrapChar="" formatNumbers="0" multilineAlign="3" decimals="3" leftDirectionSymbol="&lt;" plussign="0" autoWrapLength="0" placeDirectionSymbol="0"/>
      <placement yOffset="0" offsetType="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" repeatDistanceUnits="MM" placement="0" preserveRotation="1" rotationAngle="0" distMapUnitScale="3x:0,0,0,0,0,0" dist="0" maxCurvedCharAngleOut="-25" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" centroidWhole="0" fitInPolygonOnly="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" repeatDistance="0" offsetUnits="MM" placementFlags="10" xOffset="0" maxCurvedCharAngleIn="25" priority="5" distUnits="MM" centroidInside="0" quadOffset="4"/>
      <rendering obstacleFactor="1" scaleMax="0" fontLimitPixelSize="0" obstacleType="0" displayAll="0" fontMinPixelSize="3" obstacle="1" mergeLines="0" fontMaxPixelSize="10000" upsidedownLabels="0" zIndex="0" minFeatureSize="0" labelPerPart="0" maxNumLabels="2000" scaleVisibility="0" drawLabels="1" limitNumLabels="0" scaleMin="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option name="properties"/>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
    </settings>
  </labeling>
  <fieldConfiguration>
    <field name="pkuid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="name">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="description">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="class">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="timestamp">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="latitude">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="longitude">
      <editWidget type="">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="pkuid" index="0" name=""/>
    <alias field="name" index="1" name=""/>
    <alias field="description" index="2" name=""/>
    <alias field="class" index="3" name=""/>
    <alias field="timestamp" index="4" name=""/>
    <alias field="latitude" index="5" name=""/>
    <alias field="longitude" index="6" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default field="pkuid" expression="" applyOnUpdate="0"/>
    <default field="name" expression="" applyOnUpdate="0"/>
    <default field="description" expression="" applyOnUpdate="0"/>
    <default field="class" expression="" applyOnUpdate="0"/>
    <default field="timestamp" expression="" applyOnUpdate="0"/>
    <default field="latitude" expression="" applyOnUpdate="0"/>
    <default field="longitude" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" unique_strength="1" notnull_strength="1" field="pkuid" constraints="3"/>
    <constraint exp_strength="0" unique_strength="0" notnull_strength="0" field="name" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" notnull_strength="0" field="description" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" notnull_strength="0" field="class" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" notnull_strength="0" field="timestamp" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" notnull_strength="0" field="latitude" constraints="0"/>
    <constraint exp_strength="0" unique_strength="0" notnull_strength="0" field="longitude" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="pkuid" desc="" exp=""/>
    <constraint field="name" desc="" exp=""/>
    <constraint field="description" desc="" exp=""/>
    <constraint field="class" desc="" exp=""/>
    <constraint field="timestamp" desc="" exp=""/>
    <constraint field="latitude" desc="" exp=""/>
    <constraint field="longitude" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields>
    <field type="10" comment="" expression="to_dm($y, 'y', 4, 'suffix')" length="0" typeName="string" precision="0" name="latitude" subType="0"/>
    <field type="10" comment="" expression="to_dm($x, 'x', 4, 'suffix')" length="0" typeName="string" precision="0" name="longitude" subType="0"/>
  </expressionfields>
  <mapTip> &lt;b>[% "name" %]&lt;/b>&lt;br>
 [% "description" %]&lt;br>
 [%  to_dm( $y, 'y', 4, 'suffix') %], [%  to_dm( $x, 'x', 4, 'suffix') %]</mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
