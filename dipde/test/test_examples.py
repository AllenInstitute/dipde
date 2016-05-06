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
    np.testing.assert_almost_equal(y[-1], 8.6661023435049493)
    
def test_excitatory_inhibitory():
    from dipde.examples.excitatory_inhibitory import example
    t, y = example(show=False)

    np.testing.assert_almost_equal(t[-1], .1)
    np.testing.assert_almost_equal(y[-1], 0.90725590501763964)
    
def test_potjans_diesmann():
    from dipde.examples.potjans_diesmann_cortical_column import example

    result_dict = example(show=False)

    true_ans_dict = {(23, 'e'):0.36683677638000578,
                     (23, 'i'):3.1151133546760521,
                     (4, 'e'):4.7552501275610446,
                     (4, 'i'):6.7775636919284405,
                     (5, 'e'):12.147501318850377,
                     (5, 'i'):11.178004318697729,
                     (6, 'e'):2.1020601597049673,
                     (6, 'i'):9.2949915351536987}
    
    for layer in [23, 4, 5, 6]:
        for celltype in ['e', 'i']:
            np.testing.assert_almost_equal(result_dict[layer, celltype], true_ans_dict[layer, celltype])
#  
#     np.testing.assert_almost_equal(t[-1], .1)

    

if __name__ == "__main__":                      # pragma: no cover
    test_singlepop()                            # pragma: no cover
    test_singlepop_sine()                       # pragma: no cover
    test_singlepop_recurrent()                  # pragma: no cover
    test_singlepop_exponential_distribution()   # pragma: no cover
    test_excitatory_inhibitory()                # pragma: no cover
    test_potjans_diesmann()                     # pragma: no cover

