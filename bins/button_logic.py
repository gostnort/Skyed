from bins.key_output_core import output_simulate
import yaml
import os

def arrival_button_logic(resources_path, yaml_arg):
    try:
        # Load and prepare YAML configuration
        config = load_and_prepare_yaml(resources_path, yaml_arg)

        # Initialize required classes
        screen = output_simulate.ScreenCapture(6)
        mouse = output_simulate.MouseClickMonitor(1)
        send_key = output_simulate.SendKey()
        file_monitor = output_simulate.FileMonitor.create_and_start(config['default_path'], callback=file_change_callback)

        # Start mouse monitoring
        mouse.start()

        # Process commands
        for command_dict in config['arrival_section']:
            send_key.execute_command(command_dict['command'], screen, bPrint=False)
            if 'pages_command' in command_dict and command_dict['pages_command']:
                send_key.execute_command(command_dict['pages_command'], screen, bPrint=False)

        # Clean up
        mouse.stop()
        file_monitor.stop()

        return True, ""
    except Exception as e:
        return False, str(e)

def load_and_prepare_yaml(resources_path, yaml_arg):
    with open(os.path.join(resources_path, 'keyboard_outputing.yml'), 'r') as file:
        config = yaml.safe_load(file)
    
    # Replace placeholders with actual values
    for section in config.values():
        if isinstance(section, list):
            for item in section:
                if 'command' in item:
                    item['command'] = item['command'].format(
                        airline=yaml_arg[0],
                        arrival_flight_number=yaml_arg[1],
                        departure_flight_number=yaml_arg[2],
                        arrival_date=yaml_arg[3],
                        departure_date=yaml_arg[4],
                        arrival=yaml_arg[5]
                    )
    
    return config

def file_change_callback(content):
    print(f"File changed. New content: {content}")