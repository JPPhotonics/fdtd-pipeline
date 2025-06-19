import gdsfactory as gf 

def get_layer_name_by_tuple(layer_tuple):
    r"""Get layer name in the active PDK from a layer (GDS) tuple.

    Args:
        layer_tuple (tuple): GDS layer/datatype pair, e.g. (1, 0)

    Returns:
        name (str): Name of the corresponding layer in the PDK, or "Unknown Layer" if not found
    """

    pdk = gf.get_active_pdk()
    layers = pdk.get_layer_views().layer_map
    
    r""" get layer name in custom pdk from tuple

    Args:
        layer_tuple: e.g. (1, 0)

    Returns:
        name: str, layer name in pdk
    """
    for name in layers:  
        # skip private attributes
        if not name.startswith('__'):
            attr = layers[name]
            if attr == layer_tuple:
                return name
    return "Unknown Layer"

def extend_from_ports(device, offset: float=10.0):
    r""" add straight sections to all ports of a device in order to extend through boundaries in simulations.

    Args:
        device (Component): A gdsfactory component with ports
        offset (float, optional): Length of the straight section to extend ports. Default is 10.0 um

    Returns:
        c (Component): A new component with extended ports
        ports (dict): Original ports of the unmodified device
    """
    
    c = gf.Component('extended_cell')
    device = c << device

    # add straight extensions to each port
    for port_name in device.ports:
        port = device.ports[port_name]
        
        # use port cross_section if available
        if port.cross_section:
            xs = gf.get_cross_section(port.cross_section)
        else:
            # fallback: use layer and width to define cross-section
            xs = gf.cross_section.cross_section(width=port.width, layer=port.layer)
        
        ### Note ###
        # Cross-section is not preserved in GDS export/import.
        # After re-importing from GDS, ports won't retain cross_section info.
        # Only width and layer are preserved. Extensions will use single-layer only.
        # If your original device uses multi-layer cross-sections, ensure each layer
        # has a separate port when exporting the GDS.
        ################
        
        # create and connect extension
        extension = c << gf.components.straight(length=offset, cross_section=xs)
        extension.connect('o2', port)
        
        # add new extended port
        c.add_port(name=port_name, port=extension.ports['o1'])
        
        # absorb extension into component
        c.absorb(extension)
    
    # save original ports before they are overwritten
    original_ports = device.ports
    c.absorb(device)
    
    return c, original_ports