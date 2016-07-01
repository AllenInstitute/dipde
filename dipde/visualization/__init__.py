import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import RadioButtons

def visualize(network, show=True):
    
    gs = gridspec.GridSpec(len(network.internal_population_list), 3)
    ax = plt.subplot(gs[0, 0])

    for ii, pop in enumerate(network.internal_population_list):
        ax = plt.subplot(gs[ii, 0])
        pop.plot(ax=ax)
        ax.set_xlim([pop.t_record[0], pop.t_record[-1]])
        
        try:
            ax = ax = plt.subplot(gs[ii, 1])
            pop.plot_probability_distribution(ax=ax)
        except AttributeError:
            pass
        
        
    rax = plt.subplot(gs[0, -1], frameon=False)
    
    button_label_list = range(len(network.internal_population_list))
    radio = RadioButtons(rax, button_label_list, active=None)
    
    if show == True:
        plt.tight_layout()
        plt.show()
        
    
    