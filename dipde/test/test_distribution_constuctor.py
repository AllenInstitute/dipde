import json
import scipy.stats as sps
from dipde.internals.utilities import discretize_if_needed

def test_continuous_no_N():
    discretize_if_needed(sps.norm(loc=2, scale=1.5))
 
def test_continuous_N():
    discretize_if_needed((sps.norm(loc=2, scale=1.5),25))
    
def test_scalar():
    discretize_if_needed(.02)
 
def test_discrete_rv():
    discretize_if_needed(sps.rv_discrete(values=(.02,1)))
 
def test_dist_specified():
    discretize_if_needed(((0,1,2,3),(.25,.25,.25,.25)))
    
def test_dist_xk_pk_off_by_one():
    discretize_if_needed(((0,1,2,3),(.5,.25,.25)))
    
def test_dist_dict_delta():
    discretize_if_needed({'distribution':'delta', 'weight':.5})
    
def test_dist_json_delta():
    discretize_if_needed(json.dumps({'distribution':'delta', 'weight':.5}))


if __name__ == "__main__":                      # pragma: no cover
    test_continuous_no_N()                      # pragma: no cover
    test_continuous_N()                         # pragma: no cover
    test_scalar()                               # pragma: no cover
    test_discrete_rv()                          # pragma: no cover
    test_dist_specified()                       # pragma: no cover
    test_dist_xk_pk_off_by_one()                # pragma: no cover
    test_dist_dict_delta()                      # pragma: no cover
    test_dist_json_delta()                      # pragma: no cover