import pytest
try:
    reload
except:
    from importlib import reload


def test_imports():
    
    # Trick to get around code coverage report skipping __ini__.py sinde dipde is imported in setup.py to get version
    import dipde as dd
    reload(dd)


@pytest.mark.skip()
def test_internal():
    
    import dipde.internals.simulationconfiguration as simconf
    reload(simconf)
    
    import dipde.internals as dd
    reload(dd)
    
    import dipde.interfaces as tf
    reload(tf)
    
    import dipde.interfaces.pandas as ipd
    reload(ipd)
    
    import dipde.interfaces.zmq as izmq
    reload(izmq)
    
    import dipde.internals.connection as cc
    reload(cc)
    
    import dipde.internals.firingrateorganizer as ifro
    reload(ifro)
    
    import dipde.internals.network as ntw
    reload(ntw)
    
    import dipde.internals.connectiondistribution as cd
    reload(cd)
    
    import dipde.internals.connectiondistributioncollection as cdc
    reload(cdc)
    
    import dipde.internals.externalpopulation as ep
    reload(ep)
    
    import dipde.internals.internalpopulation as ip
    reload(ip)
    
    import dipde.internals.simulation as ss
    reload(ss)
    
    import dipde.internals.utilities as ut
    reload(ut)
    

    
if __name__ == "__main__":                         # pragma: no cover
    test_internal()                         # pragma: no cover
    test_imports()                         # pragma: no cover