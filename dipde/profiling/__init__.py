import re
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

def extract_value(result, key, file_name, function_name):

    header_line = re.findall("^.*filename:lineno\(function\).*$", result, re.MULTILINE)[0].strip()
    key_ind = header_line.split().index(key)
    
    value_line = re.findall("^.*%s:.*\(%s\).*$" % (file_name, function_name), result, re.MULTILINE)[0].strip()
    return float(value_line.split()[key_ind])