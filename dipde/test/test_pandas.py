from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection
from dipde.internals.utilities import compare_dicts
from dipde.interfaces.pandas import dict_from_df

def test_internalpopulation_df():
    i1 = InternalPopulation(v_min=0, v_max=.02)
    i2 = InternalPopulation(**dict_from_df(i1.to_df()))
    compare_dicts(i1.to_dict(), i2.to_dict())

def test_enternalpopulation_df():
    e1 = ExternalPopulation(100)
    e2 = ExternalPopulation(**dict_from_df(e1.to_df()))
    compare_dicts(e1.to_dict(), e2.to_dict())
    
def test_network_df():
    p1 = ExternalPopulation(100, record=True)
    p2 = ExternalPopulation(200, record=False)
    p3 = InternalPopulation(v_min=0, v_max=.02, metadata={'X':0})
    p4 = InternalPopulation(v_min=0, v_max=.01, metadata={'X':0})
    n1 = Network(population_list=[p1, p2, p3, p4])
    
    print n1.to_df()
    
if __name__ == "__main__":              # pragma: no cover
    test_internalpopulation_df()      # pragma: no cover
    test_enternalpopulation_df()      # pragma: no cover
    test_network_df()              # pragma: no cover
