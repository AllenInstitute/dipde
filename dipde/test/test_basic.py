
def test_imports():
    
    # Trick to get around code coverage report skipping __ini__.py sinde dipde is imported in setup.py to get version
    import dipde as dd
    reload(dd)
    
def test_internal():
    
    import dipde.internals as dd
    reload(dd)
    
    import dipde.internals.connection as cc
    reload(cc)
    
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