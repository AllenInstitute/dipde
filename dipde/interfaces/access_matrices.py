from dipde.internals.network import Network
from dipde.internals.connectiondistribution import ConnectionDistribution
def get_leak_matrix(internal_population):
    
    internal_population_copy = internal_population.copy()
    network = Network([internal_population_copy], [])
    network.dt = 1.
    network.t0 = 1.
    network.ti = 1.
    internal_population_copy.initialize()
    return internal_population_copy.leak_flux_matrix_dict['dense'].copy()
    
def get_connection_flux_matrices(connection):

    target_population_copy = connection.target.copy()
    network = Network([target_population_copy], [])
    network.dt = 1.
    network.t0 = 1.
    network.ti = 1.
    target_population_copy.initialize()

    conn_dist = ConnectionDistribution(target_population_copy.edges, connection.weights, connection.probs)
    conn_dist.initialize()
    flux_matrix = conn_dist.flux_matrix_dict['dense']
    flux_vector = conn_dist.threshold_flux_vector
     
    return flux_matrix, flux_vector

