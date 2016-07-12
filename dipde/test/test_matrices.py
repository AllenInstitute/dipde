from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.connection import Connection 
from dipde.interfaces.access_matrices import get_leak_matrix, get_connection_flux_matrices

def test_access_matrices():

    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.0001)
    c1 = Connection(None, i1, 1, weights=.005)
    
    leak_matrix = get_leak_matrix(i1)
    synaptic_matrix, threshold_vector = get_connection_flux_matrices(c1)
    assert leak_matrix.shape == synaptic_matrix.shape
    assert synaptic_matrix.shape[0] == threshold_vector.shape[0]  
    
if __name__ == "__main__":                         # pragma: no cover
    test_access_matrices()                         # pragma: no cover