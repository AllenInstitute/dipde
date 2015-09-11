import numpy as np
import matplotlib
matplotlib.use('Agg')

def test_singlepop():
    from dipde.examples.singlepop import example
    t, y = example(show=False)

    np.testing.assert_almost_equal(t[5], .0005)
    np.testing.assert_almost_equal(y[5], .00039095499999999633)
    
def test_singlepop_sine():
    from dipde.examples.singlepop_sine import example
    t, y = example(show=False)

    np.testing.assert_almost_equal(t[10], .001)
    np.testing.assert_almost_equal(y[100], 1.8977443953614115)
    
def test_singlepop_recurrent():
    from dipde.examples.singlepop_recurrent import example
    t, y = example(show=False)

    np.testing.assert_almost_equal(t[10], .001)
    np.testing.assert_almost_equal(y[100], 1.18954810997)
    
def test_singlepop_exponential_distribution():
    from dipde.examples.singlepop_exponential_distribution import example
    t, y = example(show=False)

    np.testing.assert_almost_equal(t[-1], .1)
    np.testing.assert_almost_equal(y[-1], 8.6633532147226759)
    
def test_excitatory_inhibitory():
    from dipde.examples.excitatory_inhibitory import example
    t, y = example(show=False)

    np.testing.assert_almost_equal(t[-1], .1)
    np.testing.assert_almost_equal(y[-1], 0.90731622281068436)
    

if __name__ == "__main__":                      # pragma: no cover
    test_singlepop()                            # pragma: no cover
    test_singlepop_sine()                       # pragma: no cover
    test_singlepop_recurrent()                  # pragma: no cover
    test_singlepop_exponential_distribution()   # pragma: no cover
    test_excitatory_inhibitory()                # pragma: no cover
