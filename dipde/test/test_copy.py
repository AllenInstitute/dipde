from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Simulation
from dipde.internals.connection import Connection as Connection
from dipde.internals.utilities import compare_dicts

def compare(o1, o2):
    
    compare_dicts(o1.to_dict(), o2.to_dict())

def test_internalpopulation_copy():
    i1 = InternalPopulation(v_min=0, v_max=.02)
    i2 = i1.copy()
    compare(i1, i2)
    
def test_enternalpopulation_copy():
    o1 = ExternalPopulation(100)
    o2 = o1.copy()
    compare(o1, o2)

def test_connection_copy_1():
    o1 = Connection(0, 1, 2, weights=.005, delays=.005)
    o2 = o1.copy()
    compare(o1, o2)

def test_connection_copy_2():    
    o1 = Connection(nsyn=2, weights=.005, delays=.005)
    o2 = o1.copy()
    compare(o1, o2)

def test_simulation_copy():
    b1 = ExternalPopulation(100)
    i1 = InternalPopulation(v_min=0, v_max=.02)
    b1_i1 = Connection(b1, i1, 2, weights=.005)
    o1 = Simulation([b1, i1], [b1_i1])
    o2 = o1.copy()
    compare(o1, o2)
    
if __name__ == "__main__":              # pragma: no cover
    test_internalpopulation_copy()      # pragma: no cover
    test_enternalpopulation_copy()      # pragma: no cover
    test_simulation_copy()              # pragma: no cover
    test_connection_copy_1()              # pragma: no cover
    test_connection_copy_2()              # pragma: no cover