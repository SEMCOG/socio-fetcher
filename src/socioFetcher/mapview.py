import ipyleaflet
from branca.colormap import linear
from ipywidgets import IntSlider, HTML


class MapView:
    def __init__(self, geo_data, choro_data, name, **kwargs):
        self.geo_data = geo_data
        self.choro_data = choro_data
        self.name = name
        self.map = ipyleaflet.Map(
            layers=(ipyleaflet.basemap_to_tiles(
                ipyleaflet.basemaps.CartoDB.Positron),),
            center=(42.124026, -84.102547),
            **kwargs
        )
        choro = self.choro_layer()

        def handle_click(**kwargs):
            chron.style = {'opacity': 1, 'weight': 1.9,
                           'dashArray': '9', 'fillOpacity': 1}
            chron.choro_data = {
                "26161": 20,
                "26163": 10
            }
            data_box.value = "new data"
        chron.on_click(handle_click)
        year_slider = IntSlider(description='Year:',
                                min=2010, max=2017, value=2017)
        year_widget = ipyleaflet.WidgetControl(
            widget=year_slider, position='topright')

        data_box = HTML(
            value="click to show data"
        )
        data_widget = ipyleaflet.WidgetControl(
            widget=data_box, position='topright')
        self.map.add_layer(chron)
        self.map.add_control(ipyleaflet.LayersControl())
        self.map.add_control(ipyleaflet.FullScreenControl())
        self.map.add_control(year_widget)
        self.map.add_control(data_widget)

    def choro_layer(self):
        choro = ipyleaflet.Choropleth(geo_data=self.geo_data,
                                      choro_data=self.choro_data,
                                      colormap=linear.YlOrRd_04,
                                      name=self.name,
                                      style={
                                          'opacity': 1,
                                          'weight': 1.9,
                                          'dashArray': '9',
                                          'fillOpacity': 0.5})
        return choro

    def show(self):
        return self.map
