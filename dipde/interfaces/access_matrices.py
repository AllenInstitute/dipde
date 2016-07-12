from dipde.internals.network import Network
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.connection import Connection 

def get_leak_matrix(internal_population):
    
    network = Network([internal_population], [])
    network.dt = 1.
    network.t0 = 1.
    network.ti = 1.
    internal_population.initialize()
    return internal_population.leak_flux_matrix_dict['dense'].copy()
    
def get_connection_flux_matrices(connection):

    Network([], [connection])
    connection.initialize_connection_distribution()
    connection.connection_distribution.initialize()

    flux_matrix = connection.connection_distribution.flux_matrix_dict['dense']
    flux_vector = connection.connection_distribution.threshold_flux_vector
    
    return flux_matrix, flux_vector

if __name__ == "__main__":

    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.0001)
    c1 = Connection(None, i1, 1, weights=.005)
    
    print get_leak_matrix(i1)
    print get_connection_flux_matrices(c1)
