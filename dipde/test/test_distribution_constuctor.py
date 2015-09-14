import scipy.stats as sps
from dipde.internals.utilities import discretize_if_needed

def test_continuous_no_N():
    test_dist = discretize_if_needed(sps.norm(loc=2, scale=1.5))
 
def test_continuous_N():
    test_dist = discretize_if_needed((sps.norm(loc=2, scale=1.5),25))
    
def test_scalar():
    test_dist = discretize_if_needed(.02)
 
def test_discrete_rv():
    test_dist = discretize_if_needed(sps.rv_discrete(values=(.02,1)))
 
def test_dist_specified():
    test_dist = discretize_if_needed(((0,1,2,3),(.25,.25,.25,.25)))


if __name__ == "__main__":                      # pragma: no cover
    test_continuous_no_N()                      # pragma: no cover
    test_continuous_N()                         # pragma: no cover
    test_scalar()                               # pragma: no cover
    test_discrete_rv()                          # pragma: no cover
    test_dist_specified()                       # pragma: no cover

