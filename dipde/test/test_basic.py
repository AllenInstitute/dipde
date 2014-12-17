
def test_imports():
    
    # Trick to get around code coverage report skipping __ini__.py sinde dipde is imported in setup.py to get version
    import dipde as dd
    reload(dd)
    
