import os
import yaml

def  triggered_button(ResourcesPath:str):
    try:
        with open(os.path.join(ResourcesPath,'keyboard_outputing.yml'),'r') as file:
            setting_file = file.read()
        commands_config = yaml.safe_load(setting_file)
    except FileNotFoundError as e:
        print(f'The keyboard output commands configuration files NOT found. {e}')
        return False, e
    for command_dict in commands_config['arrival_section']:
        print(command_dict['command'])
    return True,''