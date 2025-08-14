from datetime import datetime
import numpy as np
import tidy3d as td
import gdsfactory as gf
import tidy3d.web as web
import re
import logging

from helper_functions.generic.misc import write_to_json
from helper_functions.tidy3d.materials import load_pole_material
from helper_functions.tidy3d.gds_handling import import_gds_to_tidy3d
from helper_functions.generic.gds_handling import extend_from_ports

logger = logging.getLogger(__name__)

def fdtd_from_gds(parameters):

    # unit conversion: micrometer
    um = 1
    
    # default simulation parameters
    p = dict(
        temperature = 300,
        
        resolution = 6,
        
        wavelength = 1.55,
        wav_span = 0.05,
        wav_step = 0.01,

        gds_file = 'mmi_1x2_450_VISPIC2.gds',

        material_type = 'universal',
        guiding_material = 'SiN',
        
        file_name = 'test_'+str(datetime.now().strftime('%Y%m%d%H%M%S')),
        task_name = 'test_'+str(datetime.now().strftime('%Y%m%d%H%M%S')),
        
        flag_extend = 1,
        extension = 10.0,
        
        flag_run_simulation = 0,
        flag_flux_monitor = 0,
        
        flag_boolean = 0,
        mode_num = 5,
        mode_idx = 1,
        
        solver_z_min = -1,
        solver_z_max = 1,
        
        change_cladding = False,
    )
    
    # update default setting with input
    p.update(parameters)
    
    # convert settings to local variables
    for key, value in p.items():
        globals()[key] = value
    
    # save parameters to a json file
    write_to_json(dict_name=p, json_name=file_name+'_fdtd.json')

    ##### convert wavelength (um) to frequency (Hz)
    freq0 = td.C_0/wavelength

    wav_stop = wavelength + 0.5*wav_span
    wav_start = wavelength - 0.5*wav_span
    freq_start = td.C_0/wav_stop
    freq_stop = td.C_0/wav_start
    freqs = np.linspace(freq_start, freq_stop, num=round(wav_span/wav_step+1.0))

    ##### import material data to tidy3d #####
    if guiding_material == 'SiN':
        mat_WG = load_pole_material(filename=r"materials_library\\"+material_type+'_SiN_pole')
    if guiding_material == 'Si':
        mat_WG = load_pole_material(filename=r"materials_library\\"+material_type+'_Si_pole')
    
    mat_OX = load_pole_material(filename=r"materials_library\\"+material_type+'_SiO2_pole')

    # read gds, and extend from ports
    if flag_extend:
        device = gf.import_gds(gds_file, read_metadata=True)
        device, ports = extend_from_ports(device, offset=extension)
        device.write_gds(file_name+'_extended.gds', with_metadata=True)
        # structures = import_gds_to_tidy3d(gds_file=file_name+'_extended.gds', material=mat_WG, cell_name='extended_cell')
        structures = import_gds_to_tidy3d(gds_file=file_name+'_extended.gds', material=mat_WG, flag_boolean=flag_boolean)
        
    else:
        device = gf.import_gds(gds_file, read_metadata=True)
        ports = device.ports
        device.write_gds(file_name+'.gds', with_metadata=True)
        structures = import_gds_to_tidy3d(gds_file=file_name+'.gds', material=mat_WG, flag_boolean = flag_boolean)
    
    x_min = np.inf
    x_max = -1*np.inf
    y_min = np.inf
    y_max = -1*np.inf

    for port_name in ports:
        x = ports[port_name].center[0]
        y = ports[port_name].center[1]
        w = ports[port_name].width
        x_min = min(x_min, x)
        x_max = max(x_max, x)
        y_min = min(y_min, y - w)
        y_max = max(y_max, y + w)
    
    if y_max < device.ymax:
        y_max = device.ymax
    if y_min > device.ymin:
        y_min = device.ymin
    
    if x_min == x_max: # like a 180-degree bend, U-shape
        x_min = ports['o1'].center[0]
        x_max = device.xmax
    
    solver_x_min = x_min - 1.0
    solver_x_max = x_max + 1.0
    solver_y_min = y_min - 1.0
    solver_y_max = y_max + 1.0

    struc = []
    if change_cladding:
        cladding = td.Structure(
            geometry = td.Box.from_bounds(
                rmin = (solver_x_min-5.0, solver_y_min-5.0, 0),
                rmax = (solver_x_max+5.0, solver_y_max+5.0, solver_z_max+5.0)
            ),
            medium = td.Medium(permittivity=2.0**2)
        )
        struc.append(cladding)
    
    struc.extend(structures)

    # define mode source
    src_plane = td.Box(
        center=(
            ports['o1'].center[0]*um, 
            ports['o1'].center[1]*um, 
            0,
        ), 
        size=(
            0, 
            (ports['o1'].width+4.0)*um, 
            2.0*um,
        ),
    )
    src_time = td.GaussianPulse(freq0=freq0, fwidth=freq_stop-freq_start)

    mode_spec = td.ModeSpec(num_modes=mode_num, group_index_step=True)

    mode_source = td.ModeSource(
        center = src_plane.center,
        size = src_plane.size,
        source_time = src_time,
        direction = "+",
        mode_spec = mode_spec,
        mode_index = mode_idx,
        num_freqs=round(wav_span/0.01+1.0),
        )
    
    # input field monitor
    in_mnt = td.FieldMonitor(
        center=[
            (ports['o1'].center[0]+0.5)*um, 
            ports['o1'].center[1]*um, 
            0,
            ],
        size=src_plane.size,
        freqs=list(freqs),
        name='input field',
        )

    # z-normal (overhead) field monitor
    freq_mnt = td.FieldMonitor(
        center=(
            0.5*(solver_x_max+solver_x_min)*um, 
            0.5*(solver_y_max+solver_y_min)*um,  
            0.1*um,
            ),
        size=(
            (solver_x_max-solver_x_min)*um, 
            (solver_y_max-solver_y_min)*um, 
            0
            ),
        freqs=list(freqs),
        name='z-normal field',
        )
    
    monitors = [in_mnt, freq_mnt]

    # add output monitors

    for port_name in ports:
        if re.match(r'^o\d+$', port_name) and port_name!='o1':
            orientation = ports[port_name].orientation
            center = (ports[port_name].center[0] * um, ports[port_name].center[1] * um, 0)
            
            if orientation in [0.0, 180.0]:
                size = (0, (ports[port_name].width + 4.0)*um, 2.0*um)
                if flag_flux_monitor:
                    # add flux monitor
                    flux_mnt = td.FluxMonitor(
                        center = center,
                        size = size,
                        freqs = list(freqs),
                        name = port_name+' flux',
                    )
                    monitors.append(flux_mnt)

                # add mode monitor
                mode_mnt = td.ModeMonitor(
                    center=center,
                    size=size,
                    freqs = list(freqs),
                    mode_spec = mode_spec,
                    name = port_name + ' mode'
                )
                monitors.append(mode_mnt)
            
            if orientation in [90.0, 270.0]:
                size = ((ports[port_name].width + 4.0)*um, 0, 2.0*um)
                if flag_flux_monitor:
                    # add flux monitor
                    flux_mnt = td.FluxMonitor(
                        center = center,
                        size = size,
                        freqs = list(freqs),
                        name = port_name+' flux',
                    )
                    monitors.append(flux_mnt)

                # add mode monitor
                mode_mnt = td.ModeMonitor(
                    center=center,
                    size=size,
                    freqs = list(freqs),
                    mode_spec = mode_spec,
                    name = port_name + ' mode'
                )
                monitors.append(mode_mnt)
            
    ##### add solver #####
    sim_size=(
        (solver_x_max-solver_x_min)*um,
        (solver_y_max-solver_y_min)*um,
        (solver_z_max-solver_z_min)*um,
    )
    sim_time = 15.0*(solver_x_max-solver_x_min)*um*2.0/td.C_0

    sim = td.Simulation(
        size = sim_size,
        center = (
            0.5*(solver_x_max+solver_x_min)*um, 
            0.5*(solver_y_max+solver_y_min)*um, 
            0.5*(solver_z_max+solver_z_min)*um
            ),
        grid_spec=td.GridSpec.auto(min_steps_per_wvl=resolution),
        structures = struc,
        sources=[mode_source],
        monitors=monitors,
        run_time=sim_time,
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.Absorber()), # absorber or PML
        medium = mat_OX,
        subpixel=td.SubpixelSpec(dielectric=td.ContourPathAveraging()),
    )

    job = web.Job(simulation=sim, task_name=task_name, verbose=True)

    # Estimate the maximum cost
    estimated_cost = web.estimate_cost(job.task_id)
    logger.info(f'The estimated maximum cost is {estimated_cost:.3f} Flex Credits.')

    # optionally run simulation
    if flag_run_simulation:
        sim_data = job.run(path=file_name+'_results.hdf5')

        return sim_data