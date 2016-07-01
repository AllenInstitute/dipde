# import matplotlib
# matplotlib.use('Qt4Agg')
# import matplotlib.pyplot as plt
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection
from dipde.visualization import visualize

dv = .0001
update_method = 'approx'
approx_order = 1
tol = 1e-14

b1 = ExternalPopulation('100', record=True)
i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
i2 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
b1_i1 = Connection(b1, i1, 1, weights=.005, delays=0.0)
b1_i2 = Connection(b1, i2, 2, weights=.005, delays=0.0)
network = Network([b1, i1, i2], [b1_i1, b1_i2])


network.run(dt=.0001, tf=.1, t0=0)

print i1.get_firing_rate(.1)

visualize(network, show=True)

print network.to_dict()