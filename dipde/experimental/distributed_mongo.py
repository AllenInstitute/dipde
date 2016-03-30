from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection
# from dipde.profiling import profile_simulation, extract_value
from mongodistributedconfiguration import MongoDistributedConfiguration
import sys
import os
import logging
import time

logging.disable(logging.CRITICAL)

number_of_processes = int(os.environ.get('NUMBER_OF_NODES',2))
try:
    rank = int(sys.argv[1])
except:
    rank = 0

# Settings:
t0 = 0.
dt = .0001
dv = .0001
tf = .1
update_method = 'approx'
approx_order = None
tol = 1e-14

# Run simulation:
b1 = ExternalPopulation(100)
b2 = ExternalPopulation(100)
b3 = ExternalPopulation(100)
b4 = ExternalPopulation(100)
i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
i2 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
i3 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
i4 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
b1_i1 = Connection(b1, i1, 1, weights=.005)
b2_i2 = Connection(b2, i2, 1, weights=.005)
b3_i3 = Connection(b3, i3, 1, weights=.005)
b4_i4 = Connection(b4, i4, 1, weights=.005)

network = Network([b1, b2, b3, b4, i1, i2, i3, i4], [b1_i1, b2_i2, b3_i3, b4_i4])

run_dict = {'t0':t0, 
            'dt':dt,
            'tf':tf,
            'distributed_configuration':MongoDistributedConfiguration(rank, number_of_processes=number_of_processes)}


import re
from dipde.internals.network import Network
import cProfile
import pstats
import StringIO
import logging as logging_module
prof = cProfile.Profile()
prof.runcall(network.run, **run_dict)
stream = StringIO.StringIO()
p = pstats.Stats(prof, stream=stream)

p.strip_dirs().sort_stats('cumtime').print_stats(20)
if rank == 0:
    print  stream.getvalue()
# network.run(**run_dict)
# print time.time() - t0


# profile = profile_simulation(simulation, run_dict, logging=False)
# total_time = extract_value(profile, 'simulation.py', 'run')
# parallel_overhead = extract_value(profile, 'distributedconfiguration.py', 'update')
# parallel_win = extract_value(profile, 'internalpopulation.py', 'update')
# if rank == 0: print 'total time: %s' % total_time
# if rank == 0: print 'parallel_overhead: %s' % parallel_overhead
# print 'parallel_win: %s' % parallel_win


#      1001    0.001    0.000    0.193    0.000 distributedconfiguration.py:28(update)

# if rank == 0:
#     print profile


    
# print extract_value(profile, 'cumtime', 'simulation.py', 'run')

  
# # Visualize:
# i1 = simulation.population_list[1]
# fig, ax = plt.subplots(figsize=(3,3))
# i1.plot(ax=ax)
# plt.xlim([0,tf])
# plt.ylim(ymin=0)
# plt.xlabel('Time (s)')
# plt.ylabel('Firing Rate (Hz)')
# fig.tight_layout()
# plt.show()
    

    
#     
# # 
# # 
# 
#              
#  class ThreadCallback(threading.Thread):
#  
#     def __init__(self, obj, callback, sleep_time):
#         super(self.__class__, self).__init__()
#         self.daemon = True
#         self.callback = callback
#         self.sleep_time = sleep_time
#         self.obj = obj
#         self.start()
#         
#          
#     def run(self):
#         while True:
#             self.callback(self.obj)
#             time.sleep(self.sleep_time)
# 
# def sleep_callback(self):
#     time.sleep(1)
#     pass
# 
# def firing_rate_callback(self):
#     print self.recent_full_firing_rate_dict

# tmp = ThreadCallback(simulation, firing_rate_callback, .5)


