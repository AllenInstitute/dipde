from dipde.profiling import profile_simulation
from dipde.examples.singlepop import get_simulation

def test_profile_singlepop():
    
    dv = .00005
    update_method = 'approx'
    approx_order = None
    tol = 1e-14
    
    run_dict = {'dt':.00005, 't0':0, 'tf':.2}
    simulation = get_simulation(dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
    profile_simulation(simulation.to_dict(), run_dict)
    
if __name__ == "__main__":                      # pragma: no cover
    test_profile_singlepop()                    # pragma: no cover