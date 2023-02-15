import numpy as np
from cpymad.madx import Madx
import xtrack as xt
import xpart as xp
from statisticalEmittance import *
# import json
import xobjects as xo
import xfields as xf
from parabolic_longitudinal_distribution import parabolic_longitudinal_distribution
import sys
import time

####################
# Choose a context #
####################

context = xo.ContextCpu()
#context = xo.ContextCupy()
#context = xo.ContextPyopencl('0.0')

print(context)

with open('PSB/madx/tune.madx', 'w') as f:
    f.write('Qy=4.'+str(sys.argv[1])+';')   

mad = Madx()
mad.call('PSB/madx/psb_injection_example.madx')

line= xt.Line.from_madx_sequence(mad.sequence['psb'],install_apertures=True)
line.particle_ref=xp.Particles(mass0=xp.PROTON_MASS_EV,
                               gamma0=mad.sequence.psb.beam.gamma)

nemitt_x=3e-6
nemitt_y=2.3e-6
bunch_intensity=55e10
sigma_z=16.9#15.85*0.67#
n_part = int(200e3)

# from space charge example
num_turns= int(1)

num_spacecharge_interactions = 160 # is this interactions per turn?
tol_spacecharge_position = 1e-2 # is this the minimum/maximum space between sc elements?

# Available modes: frozen/quasi-frozen/pic
mode = 'pic'#'frozen'

#############################################
# Install spacecharge interactions (frozen) #
#############################################

lprofile = xf.LongitudinalProfileQGaussian(
        number_of_particles=bunch_intensity,
        sigma_z=sigma_z,
        z0=0.,
        q_parameter=1.)

xf.install_spacecharge_frozen(line=line,
                   particle_ref=line.particle_ref,
                   longitudinal_profile=lprofile,
                   nemitt_x=nemitt_x, nemitt_y=nemitt_y,
                   sigma_z=sigma_z,
                   num_spacecharge_interactions=num_spacecharge_interactions,
                   tol_spacecharge_position=tol_spacecharge_position)

#################################
# Switch to PIC or quasi-frozen #
#################################

if mode == 'frozen':
    pass # Already configured in line
elif mode == 'quasi-frozen':
    xf.replace_spacecharge_with_quasi_frozen(
                                    line,
                                    update_mean_x_on_track=True,
                                    update_mean_y_on_track=True)
elif mode == 'pic':
    pic_collection, all_pics = xf.replace_spacecharge_with_PIC(
        _context=context, line=line,
        n_sigmas_range_pic_x=8,
        n_sigmas_range_pic_y=8,
        nx_grid=128, ny_grid=128, nz_grid=64,
        n_lims_x=7, n_lims_y=3,
        z_range=(-3*sigma_z, 3*sigma_z))
else:
    raise ValueError(f'Invalid mode: {mode}')

#################
# Build Tracker #
#################

tracker = xt.Tracker(_context=context,
                    line=line)
tracker_sc_off = tracker.filter_elements(exclude_types_starting_with='SpaceCh')

######################
# Generate particles #
######################

particles = xp.generate_matched_gaussian_bunch(_context=context, num_particles=n_part,
                            total_intensity_particles=bunch_intensity,
                            nemitt_x=nemitt_x, nemitt_y=nemitt_y, sigma_z=sigma_z,
                            particle_ref=line.particle_ref,
                            tracker=tracker_sc_off)

#particles = parabolic_longitudinal_distribution(_context=context, num_particles=n_part,
#                            total_intensity_particles=bunch_intensity,
#                            nemitt_x=nemitt_x, nemitt_y=nemitt_y, sigma_z=sigma_z,
#                            particle_ref=line.particle_ref,
#                            tracker=tracker_sc_off)


#monitor = xt.ParticlesMonitor(_context=context,
#                              start_at_turn=0, stop_at_turn=1,
#                              n_repetitions=2,
#                              repetition_period=500,
#                              num_particles=n_part)

r=StatisticalEmittance(context='CPU')
bunch_moments=r.measure_bunch_moments(particles)
print(bunch_moments['nemitt_x'])
print(bunch_moments['nemitt_y'])
output=[]
start = time.time()
np.save('distribution_in_hi_g', r.coordinate_matrix)
'''
#tracker.track(particles, num_turns=num_turns, turn_by_turn_monitor=monitor)
for i in range(num_turns):
    tracker.track(particles)
    bunch_moments=r.measure_bunch_moments(particles)
    output.append([len(r.coordinate_matrix[0]),bunch_moments['nemitt_x'].tolist(),bunch_moments['nemitt_y'].tolist(),bunch_moments['emitt_z'].tolist()])
    #if i in range(-1, num_turns, 1000):
    #    if r.context=='GPU':
    #        np.save('output/distribution_'+str(int(i)), r.coordinate_matrix.get())
    #    else:
    np.save('distribution_'+str(int(i)), r.coordinate_matrix)
end = time.time()
bunch_moments=r.measure_bunch_moments(particles)
print('epsn_x = ',bunch_moments['nemitt_x'])
print('epsn_y = ',bunch_moments['nemitt_y'])
print('eps_z = ',bunch_moments['emitt_z'])
print('time = ', end - start)
ouput=np.array(output)
#np.save('output/emittances', output)
'''