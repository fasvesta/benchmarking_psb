from xpart.longitudinal import generate_longitudinal_coordinates
from xpart import build_particles
import numpy as np


def parabolic_longitudinal_distribution(_context=None, num_particles=None,
                nemitt_x=None, nemitt_y=None, sigma_z=None,
                particle_ref=None, tracker=None, total_intensity_particles=None):

    zeta, delta = generate_longitudinal_coordinates(distribution='parabolic', 
                num_particles=num_particles, 
                engine='single-rf-harmonic', sigma_z=sigma_z,
                                                    particle_ref=particle_ref, tracker=tracker)

    x_norm = np.random.normal(size=num_particles)
    px_norm = np.random.normal(size=num_particles)
    y_norm = np.random.normal(size=num_particles)
    py_norm = np.random.normal(size=num_particles)

    if total_intensity_particles is None:   
        total_intensity_particles = num_particles

    particles = build_particles(_context=_context,  particle_ref=particle_ref,
                tracker=tracker, zeta=zeta, delta=delta*particle_ref._xobject.beta0[0], 
                x_norm=x_norm, px_norm=px_norm,
                y_norm=y_norm, py_norm=py_norm,
                scale_with_transverse_norm_emitt=(nemitt_x, nemitt_y),
                weight=total_intensity_particles/num_particles)

    return particles
