import xml.etree.ElementTree as ET
from neuroml.utils import validate_neuroml2
import warnings

schema_location = sl = 'http://www.neuroml.org/schema/neuroml2'
neuroml_template = 'dipde_2.net.nml'

elem_path_dict = {'root':None,
                  'network':'./{%s}network' % sl,
                  'iafCell':'./{%s}iafCell' % sl,
                  'population':'./{%s}network/{%s}population' % tuple([sl]*2)}

def get_bare_elem(nml_file_name, path=None):
    tree = ET.parse(nml_file_name)
    if path is None:
        elem = tree.getroot()
    else:
        elem = tree.find(path)
    
    for child in elem:
        elem.remove(child)
    return elem

def create_elem(neuroml_template, elem_type='root', **kwargs):    
    elem = get_bare_elem(neuroml_template, path=elem_path_dict[elem_type])
    elem.attrib.update(kwargs)
    return elem

def create_root(id): 
    return create_elem(neuroml_template, elem_type='root', id=id)

def create_network(id): 
    return create_elem(neuroml_template, elem_type='network', type='network')

def create_internal_population_type(id, v_max, tau_m): 
    warnings.warn('Timescale not used for conversion')
    param_dict = {'leakReversal':"0mV",
                  'leakConductance':'0 nS',
                  'C':'1.0 nF',
                  'reset':'0mV',
                  'thresh':"%smV" % (v_max*1000),
                  'id':id}

    return create_elem(neuroml_template, elem_type='iafCell', **param_dict)

def create_internal_population(id, component): 
    return create_elem(neuroml_template, id=id, elem_type='population', component=component)

    

root = create_root(id='dipde_root_id')
print(root.attrib)

network = create_network(id='dipde_network_id')
print(network.attrib)

internal_population_type = create_internal_population_type(id='internal_population_type_1', v_max=.015, tau_m=.02)
print(internal_population_type.attrib)

internal_population = create_internal_population(id='internal_population_type_1', component='yeah')
print(internal_population.attrib)



# network = create_network_elem(neuroml_example_file_name, id=)
# print network.attrib

# def get_network_element(nml_file_name):
#     tree = ET.parse(nml_file_name)
#     elem = 
#     for child in elem:
#         elem.remove(child)
#     return elem
# 
# def 
#     tree = ET.parse(nml_file_name)
#     root = tree.getroot()
#     for child in root:
#         root.remove(child)
#     return root


# print root.findall('.')
# print root.find('./neuroml')
# for x in root:
#     print x.find('network')
#     for xx in x:
#         print xx

# print root.tag
# print
# for key, val in root.attrib.items():
#     print key, val
#     


# tree.write('tmp.nml')
# 
# validate_neuroml2('tmp.nml')

# # Write root element:
# root = get_bare_neuroml_root(neuroml_example_file_name)
# ET.ElementTree(root).write('root.nml')
# validate_neuroml2('root.nml')
# 
# # Write a network in 
# root = get_bare_neuroml_root(neuroml_example_file_name)
# print get_network_element(neuroml_example_file_name)
