import nest
from distutils.version import LooseVersion
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Simulation
from dipde.internals.connection import Connection as Connection
from dipde.examples.potjans_diesmann_cortical_column import population_list,\
    connection_list

assert LooseVersion(nest.version().split()[1]) >= LooseVersion("2.6.0")

class Kernel(object):
    
    def __init__(self, population_list=[], connection_list=[]):
        self.simulation = Simulation(population_list, connection_list)
    
#     def Create("poisson_generator", number_of_neurons, params={"rate": float(firing_rate), 'start':float(start)/.001})
# 
# 
#     def Connect(self):

if __name__ == "__main__":

    kernel = Kernel()


#     # Settings:
#     t0 = 0.
#     dt = .0001
#     dv = .0001
#     tf = .1
#     update_method = 'approx'
#     approx_order = 1
#     tol = 1e-14
#     
#     b1 = ExternalPopulation('100', record=True)
#     i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
#     b1_i1 = Connection(b1, i1, 1, weights=.005, delay=0.0)
#     simulation = Simulation([b1, i1], [b1_i1], verbose=True)
#     
#     simulation.run(dt=dt, tf=tf, t0=t0)
#     
#     # Visualize:
#     import matplotlib.pyplot as plt
#     i1 = simulation.population_list[1]
#     fig, ax = plt.subplots(figsize=(3,3))
#     i1.plot(ax=ax)
#     plt.xlim([0,tf])
#     plt.ylim(ymin=0)
#     plt.xlabel('Time (s)')
#     plt.ylabel('Firing Rate (Hz)')
#     fig.tight_layout()
#     plt.show()