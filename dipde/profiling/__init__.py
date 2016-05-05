import re
from dipde.internals.network import Network
import cProfile
import pstats
import StringIO
import logging as logging_module


def profile_network(network, run_dict, sort_stats='cumulative', print_stats=20, logging=True):

    if not logging == True:
        logging_module.disable(logging_module.CRITICAL) # pragma: no cover
        
    prof = cProfile.Profile()
    prof.runcall(network.run, **run_dict)
    stream = StringIO.StringIO()
    p = pstats.Stats(prof, stream=stream)
    
    p.strip_dirs().sort_stats(sort_stats).print_stats(print_stats)
    return stream.getvalue()

def extract_value(result, file_name, function_name, key='cumtime'):

    header_line = re.findall("^.*filename:lineno\(function\).*$", result, re.MULTILINE)[0].strip()
    key_ind = header_line.split().index(key)
    
    found_in_line = re.findall("^.*%s:.*\(%s\).*$" % (file_name, function_name), result, re.MULTILINE)
    if len(found_in_line) > 0:
        value_line = found_in_line[0].strip()
        return float(value_line.split()[key_ind])
    else:
        return # pragma: no cover
    
def time_network(network, t0=0., dt=.0001, tf=.1, synchronization_harness=None):

    run_dict = {'t0':t0, 
                'dt':dt,
                'tf':tf,
                'synchronization_harness':synchronization_harness}

    profile = profile_network(network, run_dict, logging=False)
    return extract_value(profile, 'network.py', 'run')

