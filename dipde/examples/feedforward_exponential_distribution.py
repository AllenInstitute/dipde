# Copyright 2013 Allen Institute
# This file is part of dipde
# dipde is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# dipde is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with dipde.  If not, see <http://www.gnu.org/licenses/>.

import matplotlib.pyplot as plt 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection

def get_simulation(dv=.001, update_method='approx', tol=1e-8):
    import scipy.stats as sps

    # Create simulation:
    b1 = ExternalPopulation(50)
    b2 = ExternalPopulation(1000)
    i1 = InternalPopulation(v_min=-.04, v_max=.02, dv=dv, update_method=update_method, tol=tol)
    b1_i1 = Connection(b1, i1, 1, delays=0.0, weights=(sps.expon(0,.00196), 301))
    b2_i1 = Connection(b2, i1, 1, delays=0.0, weights=(sps.expon(0, .001), 301))
    simulation = Network([b1, b2, i1], [b1_i1, b2_i1])

    return simulation


def example(show=True, save=False):

    # Settings:
    t0 = 0.
    dt = .0001
    dv = .0001
    tf = .1
    update_method = 'approx'
    tol = 1e-14
    
    # Run simulation:
    simulation = get_simulation(dv=dv, update_method=update_method, tol=tol)
    simulation.run(dt=dt, tf=tf, t0=t0)

    i1 = simulation.population_list[2]
    if show == True:

        # Visualize:
        plt.figure(figsize=(3,3))

        plt.plot(i1.t_record, i1.firing_rate_record)
        plt.plot([tf],[8.6687760498], 'r*')
        plt.xlim([0,tf])
        plt.ylim(ymin=0, ymax=10)
        plt.xlabel('Time (s)')
        plt.ylabel('Firing Rate (Hz)')
        plt.tight_layout()

        if save == True:
            plt.savefig('./singlepop_exponential_distribution.png')

        print i1.firing_rate_record[len(i1.firing_rate_record) - 1]
        plt.show()

    return i1.t_record, i1.firing_rate_record

if __name__ == "__main__": example()        # pragma: no cover