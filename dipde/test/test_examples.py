
def test_singlepop():
    from dipde.examples.singlepop import example
    t, y = example(show=False)
    assert t[5] == 0.0005
    assert y[5] == 0.00039095499999999633
    
def test_twopop():
    from dipde.examples.twopop import example
    t, y1, y2 = example(show=False)
    
    assert t[5] == 0.0005
    assert y1[5] == 0.0016196734665460703
    assert y2[500] == 4.8713503006780812
    
def test_singlepop_sine():
    from dipde.examples.singlepop_sine import example
    t, y = example(show=False)

    assert t[10] == 0.0010000000000000002
    assert y[100] == 0.14373468423783811
    
def test_singlepop_recurrent():
    from dipde.examples.singlepop_recurrent import example
    t, y = example(show=False)

    assert t[10] == 0.0010000000000000002
    assert y[100] == 1.1767330411623518
    
def test_singlepop_exponential_distribution():
    from dipde.examples.singlepop_exponential_distribution import example
    t, y = example(show=False)

    assert t[-1] == 0.10000000000000184
    assert y[-1] == 21.300801986164682
    
def test_excitatory_inhibitory():
    from dipde.examples.excitatory_inhibitory import example
    t, y = example(show=False)

    assert t[-1] == 0.20009999999999428
    assert y[-1] == 0.90670046727316733
    

if __name__ == "__main__":                      # pragma: no cover
    test_singlepop()                            # pragma: no cover
    test_twopop()                               # pragma: no cover
    test_singlepop_sine()                       # pragma: no cover
    test_singlepop_recurrent()                  # pragma: no cover
    test_singlepop_exponential_distribution()   # pragma: no cover
    test_excitatory_inhibitory()                # pragma: no cover