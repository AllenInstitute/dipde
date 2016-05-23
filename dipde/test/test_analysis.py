from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection


def test_get_J():

    # Settings:
    bgfr=100
    update_method='approx'
    weights={'distribution':'delta', 'weight':.005}
    p0=((0.,),(1.,)) 
    tau_m=.02
    dv = .001
    v_min = -.01
    v_max = .02
    
    # Create simulation:
    b1 = ExternalPopulation(bgfr)
    i1 = InternalPopulation(v_min=v_min, tau_m=tau_m, v_max=v_max, dv=dv, update_method=update_method, p0=p0)
    b1_i1 = Connection(b1, i1, 1, weights=weights)
    network = Network([b1, i1], [b1_i1])
    network.get_total_flux_matrix(i1,.001)

if __name__ == "__main__":                         # pragma: no cover
    test_get_J()                         # pragma: no cover

# def f(internal_population, input_dict):
#     
#     population_list = [internal_population]
#     connection
#     for key, val in input_dict.items():
#         population_list.append(ExternalPopulation(val))
        


# simulation_configuration = SimulationConfiguration(dt, tf, t0=t0)
# simulation = Simulation(network=network, simulation_configuration=simulation_configuration)
# simulation.run()