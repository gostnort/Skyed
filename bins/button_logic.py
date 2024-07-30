import os
import yaml
from bins.key_output_core import output_simulate, screen_mensuring

def  triggered_button(ResourcesPath:str,YamlArg:list):
    try:
        with open(os.path.join(ResourcesPath,'keyboard_outputing.yml'),'r') as file:
            setting_file = file.read()
        commands_config = yaml.safe_load(setting_file)
    except FileNotFoundError as e:
        print(f'The keyboard output commands configuration files NOT found. {e}')
        return False, e
    try:
        commands_config = commands_config.replace('${arrival_flight_number}', YamlArg[0])
        commands_config = commands_config.replace('${departure_flight_number}', YamlArg[1])
        commands_config = commands_config.replace('${arrival_date}',YamlArg[2])
        commands_config = commands_config.replace('${departrue_date}', YamlArg[3])
        commands_config = commands_config.replace('${arrival}',YamlArg[4])
    except:
        pass
    screen=screen_mensuring.ScreenCapture(6)
    mouse=output_simulate.MouseClickMonitor(2)
    send_key=output_simulate.SendKey()
    mouse.start()
    for_loop_count = len(commands_config['arrival_section'])
    while mouse.is_alive():
        if mouse.count == 1:
            for command_dict in commands_config['arrival_section']:
                send_key.execute_command(command_dict['command'],screen,bPrint=False)
                for_loop_count -= 1
                if for_loop_count == 0:
                    mouse.join()
                    mouse.stop()
    return True,''