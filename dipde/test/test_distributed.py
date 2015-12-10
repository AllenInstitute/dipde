from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection
import numpy as np
import threading
from dipde.interfaces.distributed.distributedconfiguration import DistributedConfiguration

def threaded_distributed_compare(simulation_dict, run_dict):

    def run(simulation_dict, run_dict, result_dict, rank=None):
    
        t0 = run_dict['t0']
        dt = run_dict['dt']
        tf = run_dict['tf']
        number_of_processes = run_dict.get('number_of_processes', 1)
    
        simulation = Simulation(**simulation_dict)
        if rank is None:
            simulation.run(dt=dt, tf=tf, t0=t0)
        else:
            simulation.run(dt=dt, tf=tf, t0=t0, distributed_configuration=DistributedConfiguration(rank, number_of_processes=number_of_processes))
        
        result_dict[rank] = {}
        for p in simulation.population_list:
            result_dict[rank][p.gid] = p.firing_rate_record
    
    number_of_processes = run_dict.get('number_of_processes', 1)
    result_dict = {}
    thread_list = []
    for rank in range(number_of_processes):
        t = threading.Thread(target=run, args=(simulation_dict, run_dict, result_dict), kwargs={'rank':rank})
        t.daemon = True
        thread_list.append(t)
        t.start()
    
    for t in thread_list:   
        t.join()
     
    run(simulation_dict, run_dict, result_dict)
      
    for ii in range(len(simulation_dict['population_list'])):
        np.testing.assert_array_almost_equal(result_dict[None][ii], result_dict[ii%number_of_processes][ii], 12)


def get_multipop_model():

    # Settings:
    dv = .001
    update_method = 'approx'
    approx_order = None
    tol = 1e-14
    
    
    # Create simulation:
    b1 = ExternalPopulation(100)
    b2 = ExternalPopulation(50)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
    i2 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
    b1_i1 = Connection(b1, i1, 1, weights=.005)
    i1_i2 = Connection(i1, i2, 20, weights=.005, delays=.001)
    b2_i2 = Connection(b2, i2, 2, weights=.005, delays=.002)
    simulation = Simulation([b1, b2, i1, i2], [b1_i1, i1_i2, b2_i2])
    simulation_dict = simulation.to_dict()
    
    return simulation_dict

def test_multipop_model_2():
    
    simulation_dict = get_multipop_model()
    t0 = 0.
    number_of_processes = 2
    dt = .001
    tf = .01
    
    run_dict = {'t0':t0, 'dt':dt,'tf':tf, 'number_of_processes':number_of_processes}
    threaded_distributed_compare(simulation_dict, run_dict)
    
def test_multipop_model_4():
    
    simulation_dict = get_multipop_model()
    t0 = 0.
    number_of_processes = 4
    dt = .001
    tf = .01
    
    run_dict = {'t0':t0, 'dt':dt,'tf':tf, 'number_of_processes':number_of_processes}
    threaded_distributed_compare(simulation_dict, run_dict)

if __name__ == "__main__":    # pragma: no cover
    test_multipop_model_2()   # pragma: no cover
    test_multipop_model_4()   # pragma: no cover
