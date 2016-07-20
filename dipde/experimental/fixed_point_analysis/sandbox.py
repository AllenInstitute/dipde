import numpy as np
import scipy.stats as sps

def get_infinitesimal_perturbation(t0, sigma, amplitude):
    rv = sps.norm(t0, sigma)
    return lambda t: rv.pdf(t)*sigma*np.sqrt(2*np.pi)*amplitude

f = get_infinitesimal_perturbation(.1, .005, 2)

for t in np.linspace(0,.2,1000):
    print t, f(t)