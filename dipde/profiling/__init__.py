from dipde.internals.simulation import Simulation
import cProfile
import pstats
import StringIO
import logging


def profile_simulation(simulation_dict, run_dict, sort_stats='cumulative', print_stats=20):

    logging.disable(logging.CRITICAL)    
    simulation = Simulation(**simulation_dict)
        
    prof = cProfile.Profile()
    prof.runcall(simulation.run, **run_dict)
    stream = StringIO.StringIO()
    p = pstats.Stats(prof, stream=stream)
    
    p.strip_dirs().sort_stats(sort_stats).print_stats(print_stats)
    return stream.getvalue()