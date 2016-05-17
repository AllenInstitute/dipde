import scipy.spatial as sps
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import dipde.internals.network as dipde_network_module
dipde_network_module_name = dipde_network_module.__name__

def create_position_array(G, pos=lambda n: (n['x'], n['y'], n['z']), dim=3):
    
    position_array = np.zeros((len(G), dim))
    for ii, n in G.nodes_iter(data=True):
        try:
            position_array[ii,:]=pos(n)
        except KeyError:
            position_array[ii,:]=np.inf

    return position_array

def create_kdtree(G, leafsize=10):
    position_array = create_position_array(G)
#     return sps.KDTree(position_array, leafsize=leafsize)
    return position_array, sps.cKDTree(position_array, leafsize=leafsize)
    
    

def to_graph(network):

    data_model = network.to_dict()

    G = nx.MultiDiGraph()
    for ii, node in enumerate(data_model['population_list']):
        G.add_node(ii, attr_dict=node)
    
    for ii, edge in enumerate(data_model['connection_list']):
        source = edge.pop('source')
        target = edge.pop('target')
        G.add_edge(source, target, attr_dict=edge)
    
    return G

def visualize(G, show=True, markersize=1, precision=0):
    M = nx.adjacency_matrix(G) # Sparse matrix
    plt.spy(M, markersize=markersize, precision=precision)
    if show == True:
        plt.show()
        
def to_dict(G):
    
    population_list = [G.node[gid] for gid in G.nodes()]
    connection_list = []
    for u, v in G.edges():
        edge_data_dict = G[u][v]
        for edge_data in edge_data_dict.values(): 
            edge_data['source'] = u
            edge_data['target'] = v
            connection_list.append(edge_data)
    
    return {'population_list':population_list, 'connection_list':connection_list, 'class':'Network', 'module':dipde_network_module_name}
    

def edge_select(G, query, full=True):
    '''Call the query for each edge, return subgraph'''
    result = []
    for u,v,d in G.edges(data=True):
        if query(u,v,d):
            result.append((u,v,d))
    
    G2 = nx.MultiDiGraph(result)
    for n in G2.nodes_iter():
        G2.node[n] = G.node[n]
        
    if full == True:
        for ii in range(G.number_of_nodes()):
            if not ii in G2:
                G2.add_node(ii, G.node[n])
            
    return G2
    
    
if __name__ == "__main__":
    
    from dipde.examples.cortical_column import get_network, example
    from dipde.internals.network import Network

    network = get_network() 

    G = to_graph(network)
    D = to_dict(G)
    
    round_trip_network = Network(**D)
    example(show=True, network=round_trip_network)
    
    
    
    
    