from django import template
from django.template import Library

register = Library()

INCLUDE_TEMPLATE = """
<script src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false" type="text/javascript"></script>
"""

BASIC_TEMPLATE = """
<div id="map_%(name)s" style="width:%(width)spx;height:%(height)spx;"></div>
<script type="text/javascript">
   //<![CDATA[
   function create_map_%(name)s(extra_options) {

    var latlng = new google.maps.LatLng(%(lat)s, %(lon)s);
    var myOptions = {
      zoom: %(zoom)s,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.%(view)s
    };
    var map = new google.maps.Map(document.getElementById("map_%(name)s"), myOptions);

    var marker = new google.maps.Marker({
        position: latlng,
        map: map,
        title: "Mobile Vikings"
    });

    var infowindow = new google.maps.InfoWindow({
        content: '%(message)s'
    });

    if ('%(message)s' != '') {
        google.maps.event.addListener(marker, 'click', function() {
           infowindow.open(map, marker);
        });
    }

    if (typeof extra_options === 'function') {
        extra_options(map);
    }
   }
//]]>
</script>
"""
# {% gmap name:mimapa width:300 height:300 latitude:x longitude:y zoom:20 view:hybrid %} Message for a marker at that point {% endgmap %}

class GMapNode (template.Node):
    def __init__(self, params, nodelist):
        self.params = params
        self.nodelist = nodelist

    def render (self, context):
        for k, v in self.params.items():
            try:
                self.params[k] = template.Variable(v)
            except:
                pass
        self.params["message"] = self.nodelist.render(context).replace("\n", "<br />")
        # translate params
        self.params['lon'] = self.params['longitude']
        self.params['lat'] = self.params['latitude']
        # render
        return BASIC_TEMPLATE % self.params

def do_gmap(parser, token):
    items = token.split_contents()

    nodelist = parser.parse(('endgmap',))
    parser.delete_first_token()

    #Default values
    parameters = {
            'name'      : "default",
            'width'     : "300",
            'height'    : "300",
            'latitude'  : "33",
            'longitude' : "-3",
            'zoom'      : "15",
            'view'      : "ROADMAP", # ROADMAP, SATELLITE, HYBRID, TERRAIN
            'message'   : "",
    }
    for item in items[1:]:
        param, value = item.split(":")
        param = param.strip()
        value = value.strip()

        if parameters.has_key(param):
            if value[0] == "\"":
                value = value[1:-1]
            parameters[param] = value

    return GMapNode(parameters, nodelist)

class GMapScriptNode (template.Node):
    def render (self, context):
        return INCLUDE_TEMPLATE

def do_gmap_script(parser, token):
    try:
        token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Don't have the required parameters: %s" % token.contents[0])
    return GMapScriptNode()

register.tag('gmap', do_gmap)
register.tag('gmap-script', do_gmap_script)
