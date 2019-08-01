import ipyleaflet
from branca.colormap import linear
from ipywidgets import IntSlider, HTML, Dropdown
"""
Expected behavior: 
First load: show latest year data for the first attribute 
When click a county: show the data number in the box 
When change year in slider: change choro layer data to show new year data
When change attribute: change choro layer data to show the new attr data
"""


class MapView:
    """
    A map view class to generate map using ipyleaflet Map and 
    ipywidgets.

    Attributes
    -----------
    dataset:str
        dataset name used in creating layer
    geo_data:dict
        geoJSON object with FIPSCode as ID
    choro_data:dict {attributeName=>{year=>{areaID=>value}}}
    fipsLookUp:dict {fipsCode=>Name}
    availableYearDict:dict  {attrName=>[available year]}
    selectedAttr:str
        selected attribute name
    selectedYear:str
        selected year
    clickedID:str  
        clicked ID
    map:ipyleaflet.Map
        Map object
    """

    def __init__(self, dataset, geo_data, choro_data, fipsLookUp):
        """
        The constructor for MapView

        Parameters
        ----------
        dataset:str
            dataset name used in creating layer
        geo_data:dict
            GeoJSON object with FIPSCode as ID
        choro_data:dict {attributeName=>{year=>{areaID=>value}}}
        fipsLookUp:dict {fipsCode=>Name}

        Returns
        ------------
        None
        """
        self.dataset = dataset
        self.geo_data = geo_data
        self.choro_data = choro_data
        self.fipsLookUp = fipsLookUp
        self.availableYearDict = self.getAvailableYear(choro_data)
        # Init default with the first one
        self.selectedAttr = list(choro_data.keys())[0]
        self.selectedYear = list(self.choro_data[list(
            choro_data.keys())[0]].keys())[-1]
        self.clickedID = None

    def show(self, **kwargs):
        """
        Generate and return the map object for displaying the map
        Parameters
        -----------
        None

        Returns
        ----------
            map:ipyleaflet.Map
        """
        self.map = ipyleaflet.Map(
            layers=(ipyleaflet.basemap_to_tiles(
                ipyleaflet.basemaps.CartoDB.Positron),),
            **kwargs
        )
        choro_layer = ipyleaflet.Choropleth(
            name=self.dataset,
            geo_data=self.geo_data,
            choro_data=self.choro_data[self.selectedAttr][self.selectedYear],
            colormap=linear.YlOrRd_04,
            style={
                'opacity': 1,
                'weight': 1.9,
                'dashArray': '9',
                'fillOpacity': 0.5}
        )

        def handle_click(**kwargs):
            if kwargs['event'] == 'click':
                clickedFips = kwargs['properties']['GEOID']
                clickedName = self.fipsLookUp[clickedFips]
                dataBox.value = f"{clickedName} : {self.choro_data[self.selectedAttr][self.selectedYear][clickedFips]:,}"
                self.clickedID = clickedFips
        choro_layer.on_click(handle_click)
        # Year select

        def handle_year_change(change):
            new_year = str(change.new)
            choro_layer.choro_data = self.choro_data[self.selectedAttr][new_year]
            if self.clickedID:
                clickedName = self.fipsLookUp[self.clickedID]
                dataBox.value = f"{clickedName} : {self.choro_data[self.selectedAttr][new_year][self.clickedID]:,}"
            self.selectedYear = new_year
        yearList = self.availableYearDict[self.selectedAttr]
        yearListNum = list(map(int, yearList))
        minYear = min(yearListNum)
        maxYear = max(yearListNum)
        yearSlider, yearWidget = self.yearSlider(minYear, maxYear, maxYear)
        yearSlider.observe(handle_year_change, 'value')
        dataBox, dataWidget = self.dataBox()

        def handle_attr_change(change):
            new_attr = change.new
            choro_layer.choro_data = self.choro_data[new_attr][self.selectedYear]
            if self.clickedID:
                clickedName = self.fipsLookUp[self.clickedID]
                dataBox.value = f"{clickedName} : {self.choro_data[new_attr][self.selectedYear][self.clickedID]:,}"
            self.selectedAttr = new_attr
        attrDropdown, attrDropdownWidget = self.attrDropdown()
        attrDropdown.observe(handle_attr_change, "value")
        # Add to map
        self.map.add_layer(choro_layer)
        self.map.add_control(ipyleaflet.LayersControl())
        self.map.add_control(ipyleaflet.FullScreenControl())
        self.map.add_control(attrDropdownWidget)
        self.map.add_control(yearWidget)
        self.map.add_control(dataWidget)
        return self.map

    def yearSlider(self, minYear, maxYear, value):
        """
        Generate year slider for map use given available years
        """
        yearSlider = IntSlider(description='Year:',
                               min=minYear, max=maxYear, value=value)
        yearWidget = ipyleaflet.WidgetControl(
            widget=yearSlider, position='topright')
        return yearSlider, yearWidget

    def attrDropdown(self):
        """
        Generate attribute dropdown for map use

        """
        dropdown = Dropdown(
            options=set(self.choro_data.keys()),
            value=self.selectedAttr,
            description='Attribute:',
            disabled=False,
        )
        dropdown_wgt = ipyleaflet.WidgetControl(
            widget=dropdown, position='topright')
        return dropdown, dropdown_wgt

    def dataBox(self):
        """
        generate data box for map use

        """
        data_box = HTML(
            value="click to show data"
        )
        data_widget = ipyleaflet.WidgetControl(
            widget=data_box, position='topright')
        return data_box, data_widget

    def getAvailableYear(self, choro_data):
        """
        Helper function to get avaiable year for each attribute
        given choro_data

        """
        year_dict = {}
        for attrName, attrDict in choro_data.items():
            year_dict[attrName] = list(attrDict.keys())
        return year_dict
