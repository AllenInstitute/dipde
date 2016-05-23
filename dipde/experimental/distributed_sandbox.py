from dipde.interfaces.distributed.distributedconfiguration import DistributedConfiguration
import os
import sys

number_of_nodes = int(os.environ['NUMBER_OF_NODES'])
try:
    rank = int(sys.argv[1])
except:
    rank = 0

dc = DistributedConfiguration(rank, number_of_processes=number_of_nodes)

# address_config_dict = {}
# for ii in range(number_of_nodes):
#     address_config_dict[ii] = "ipc://%s" % (5559+ii)
# 
# SH = SynchronizationHarness(rank, address_config_dict)

dc.initialize(0)

for ii in range(10):
    dc.update(ii, {'a':ii+.1*rank})
    
dc.finalize()