import sympy.parsing.sympy_parser as symp
from sympy.utilities.lambdify import lambdify
from sympy.abc import t as sym_t


class ExternalPopulation(object):
    
    def __init__(self, firing_rate, record=False, **kwargs):
        
        self.firing_rate_string = str(firing_rate)
        self.symbolic_function = symp.parse_expr(self.firing_rate_string)
        self.closure = lambdify(sym_t,self.symbolic_function)
        self.record = record
        self.type = "external"
        
        # Additional metadata:
        self.metadata = kwargs
        
    def firing_rate(self, t):
        return self.closure(t)
    
    def initialize_firing_rate_recorder(self):
        
        # Set up firing rate recorder:
        self.firing_rate_record = [self.curr_firing_rate]
        self.t_record = [0]
    
    def update_firing_rate_recorder(self):
        self.firing_rate_record.append(self.curr_firing_rate)
        self.t_record.append(self.t_record[-1]+self.simulation.dt)
    
    @property
    def curr_firing_rate(self):
        return float(self.firing_rate(self.simulation.t))