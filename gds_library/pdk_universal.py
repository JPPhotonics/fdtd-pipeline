from functools import partial
import json
import gdsfactory as gf
from gdsfactory.technology import (LayerLevel, LayerStack, LayerMap, LayerView, LayerViews)
from gdsfactory.typings import Layer

try:
    with open('stack_universal.json', 'r') as file:
        config = json.load(file)
except FileNotFoundError:
    raise Exception("Layer stack configuration file does not exist.")

nm = 1e-3
min_feat_size = config['min_feat_size']

class MyLayerMap(LayerMap):
    Si: Layer = tuple(config['Si_layer'])
    SLAB: Layer = tuple(config['SLAB_layer'])
    PORT: Layer = (1,10)

LAYER = MyLayerMap()

PORT_TYPE_TO_LAYER = dict(optical=(180,0))

class MyLayerView(LayerViews):
    Si: LayerView = LayerView()
    SLAB: LayerView = LayerView()
    PORT: LayerView = LayerView()

LAYER_VIEWS = MyLayerView(layer_map=dict(LAYER))

def get_layer_stack(
        thickness_Si = config['Si_thickness'],
        thickness_Si_clad = config['Si_clad_thickness'],
        thickness_SLAB = config['SLAB_thickness'],
        thickness_SLAB_clad = config['SLAB_clad_thickness']
) -> LayerStack:
    return LayerStack(
        layers = dict(
            Si = LayerLevel(
                layer = LAYER.Si,
                thickness = thickness_Si,
                zmin = 0,
            ),
            SLAB = LayerLevel(
                layer = LAYER.SLAB,
                thickness = thickness_SLAB,
                zmin = 0,
            ),
        )
    )

LAYER_STACK = get_layer_stack()

pdk = gf.Pdk(
    name = "universal - ZL",
    layers = dict(LAYER),
    layer_stack = LAYER_STACK,
    layer_views = LAYER_VIEWS,
)

pdk.activate()