from dipde.internals.network import Network
from dipde.internals.connectiondistribution import ConnectionDistribution
import scipy.sparse as spsp

def get_leak_matrix(internal_population, sparse=False):
    
    internal_population_copy = internal_population.copy()
    network = Network([internal_population_copy], [])
    network.dt = 1.
    network.t0 = 1.
    network.ti = 1.
    internal_population_copy.initialize()
    
    if sparse == False:
        return internal_population_copy.leak_flux_matrix_dict['dense'].copy()
    else:
        return spsp.csr_matrix(internal_population_copy.leak_flux_matrix_dict['dense'])

    
    
    
def get_connection_flux_matrices(connection, sparse=False):

    target_population_copy = connection.target.copy()
    network = Network([target_population_copy], [])
    network.dt = 1.
    network.t0 = 1.
    network.ti = 1.
    target_population_copy.initialize()

    conn_dist = ConnectionDistribution(target_population_copy.edges, connection.weights, connection.probs)
    conn_dist.initialize()
    
    if sparse == False:
        flux_matrix = conn_dist.flux_matrix_dict['dense'].copy()
    else:
        flux_matrix = spsp.csr_matrix(conn_dist.flux_matrix_dict['dense'])
    flux_vector = conn_dist.threshold_flux_vector.copy()
     
    return flux_matrix, flux_vector

