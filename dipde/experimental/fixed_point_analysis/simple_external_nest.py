import matplotlib.pyplot as plt
from column_analysis_5.utilities import get_kernel, PoissonPopulation, IAFPSCDeltaPopulation, connect_one_to_one, SpikeMonitor 

N = 100000
dt=.0001
tf=.2
seed=12345
number_of_processors=2
verbose=True

neuron_params = {   "V_reset"   : 0.,
                    "tau_m"     : 20.,
                    "C_m"       : 250.,
                    "V_th"      : 20.,
                    "t_ref"     : 0.,
                    "V_m"       : 0.,
                    "E_L"       : 0.}

kernel = get_kernel(dt=dt, tf=tf, seed=seed, number_of_processors=number_of_processors, verbose=verbose)

background_population = PoissonPopulation('bg', 100, N, kernel, start=0.) 
internal_population = IAFPSCDeltaPopulation('int', N, kernel, neuron_params=neuron_params)
monitor = SpikeMonitor('int_m', internal_population, kernel)

connect_one_to_one(background_population,internal_population, .005, kernel, delay=0)

kernel.Simulate(tf*1000)

t, y = monitor.firing_rate(0, tf, .005)
plt.plot(t, y)

plt.show()