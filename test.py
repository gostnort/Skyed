import yaml

with open('resources/keyboard_outputing.yml','r') as file:
    yaml_content = file.read()

yaml_content = yaml_content.replace('${arrival_flight_number}', 'CA983')
yaml_content = yaml_content.replace('${arrival_date}','23JUL24')
yaml_content = yaml_content.replace('${arrival}','PEK')

config=yaml.safe_load(yaml_content)
print(config['arrival_section']['sy']['command'])