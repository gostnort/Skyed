import yaml
from functools import reduce
import timeit

with open('resources/keyboard_outputing.yml','r') as file:
    yaml_content = file.read()

yaml_content = yaml_content.replace('${arrival_flight_number}', 'CA983')
yaml_content = yaml_content.replace('${arrival_date}','23JUL24')
yaml_content = yaml_content.replace('${arrival}','PEK')

config=yaml.safe_load(yaml_content)

def get_value_original(yaml_structure:dict,dict_keys:list):
    current_level=yaml_structure
    for key in dict_keys:
        try:
            current_level=current_level[key]
        except(KeyError, TypeError):
            return None
    return current_level

def get_value(yaml_structure:dict[str,any],dic_keys:list[str]):
    try:
        return reduce(lambda d, key:d[key], dic_keys, yaml_structure)
    except (KeyError, TypeError):
        return None

test_keys = ['departure_section', 'sy', 'command']
number = 10000
time_original = timeit.timeit(
    'get_value_original(config, test_keys)', 
    globals=globals(), 
    number=number
)

time_reduce = timeit.timeit(
    'get_value(config, test_keys)', 
    globals=globals(), 
    number=number
)

print(f"Original fucntion: {time_original:0.6f}")
print(f"Reduce function: {time_reduce:.6f}")

print(get_value(config,['departure_section','sy','command']))