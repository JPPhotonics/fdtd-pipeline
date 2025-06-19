from helper_functions.generic.gds_handling import get_layer_name_by_tuple
import gdsfactory as gf
import pya

um = 1e-6

def import_gds_to_lumerical(project, gds_file, material, cell_name: str | None=None, flag_boolean = 0):
    r"""Import each layer of a GDS file into Lumerical.

    Args:
        project: Lumerical project handle.
        gds_file (str): Path to the GDS file.
        material: Material name used for all layers.
        cell_name (str | None): Optional specific cell name to import.
        flag_boolean (int): If set, applies boolean ops on partial etch layers.

    Returns:
        None
    """

    # get layer views and stack from active PDK
    pdk = gf.get_active_pdk()
    layers = pdk.get_layer_views().layer_map
    layer_stack = pdk.get_layer_stack()

    # import top cell
    if cell_name:
        top_cell = gf.import_gds(gdspath=gds_file, cellname=cell_name, read_metadata=True)
    else:
        top_cell = gf.import_gds(gds_file, read_metadata=True)
        cell_name = top_cell.name

    cell_layers = top_cell.layers

    # boolean operation of partial etch layer
    if flag_boolean:
        if layers['SiN1'] in cell_layers and layers['SiN1p'] in cell_layers:
            # load layout
            layout = pya.Layout()
            layout.read(gds_file)
            top_cell = layout.top_cell()
            
            # Define layers
            layer1_info = pya.LayerInfo(layers['SiN1'][0], layers['SiN1'][1])
            layer2_info = pya.LayerInfo(layers['SiN1p'][0], layers['SiN1p'][1])
            result_layer_info = pya.LayerInfo(layers['SiN1'][0], layers['SiN1'][1])

            layer1 = layout.layer(layer1_info)
            layer2 = layout.layer(layer2_info)

            layer1 = pya.Region()
            layer2 = pya.Region()

            # extract regions
            for shape in top_cell.shapes(layout.layer(layer1_info)):
                if shape.is_polygon() or shape.is_box() or shape.is_path():
                    layer1.insert(shape.polygon)

            for shape in top_cell.shapes(layout.layer(layer2_info)):
                if shape.is_polygon() or shape.is_box() or shape.is_path():
                    layer2.insert(shape.polygon)

            # boolean operation (difference: SiN1 - SiN1p)
            result_region = layer1 - layer2  # Change ^ to & for AND, | for OR, - for NOT

            # overwrite result layer
            result_layer_index = layout.layer(result_layer_info)
            top_cell.shapes(result_layer_index).clear()
            top_cell.shapes(result_layer_index).insert(result_region)

            # write modified layout back to file
            layout.write(gds_file)
    
    # import each layer into Lumerical
    for layer in cell_layers:
        layer_name = get_layer_name_by_tuple(layer) # map (layer, datatype) to name
        zmin = layer_stack.layers[layer_name].zmin # get z-min from PDK
        thickness = layer_stack.layers[layer_name].thickness
        zmax = zmin + thickness
        
        # import geometry into Lumerical
        project.gdsimport(gds_file, cell_name, str(layer[0])+':'+str(layer[1]), material, zmin*um, zmax*um)
        project.set('name', layer_name)