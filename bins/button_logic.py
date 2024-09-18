from bins.key_output_core import output_simulate
from bins.commands_processing import handle_sy, handle_se, handle_pd
import yaml
import os

def arrival_button_logic(resources_path, yaml_arg):
    mouse = None
    file_monitor = None
    try:
        # Load and prepare YAML configuration
        config = load_and_prepare_yaml(resources_path, yaml_arg)

        # Initialize required classes
        screen = output_simulate.ScreenCapture(6)
        mouse = output_simulate.MouseClickMonitor(1)
        send_key = output_simulate.SendKey()
        
        # Get the file path using the new function
        file_path = output_simulate.get_file_path_from_config()
        if not file_path:
            return False, "No suitable log file found for today or yesterday."
        
        file_monitor = output_simulate.FileMonitor.create_and_start(file_path, callback=file_change_callback)

        # Start mouse monitoring
        mouse.start()

        # Process commands
        for command_dict in config['arrival_section']:
            send_key.execute_command(command_dict['command'], screen, bPrint=False)
            if 'pages_command' in command_dict and command_dict['pages_command']:
                send_key.execute_command(command_dict['pages_command'], screen, bPrint=False)

        return True, ""
    except Exception as e:
        return False, str(e)
    finally:
        if mouse and file_monitor:
            output_simulate.cleanup_threads(file_monitor, mouse)

def load_and_prepare_yaml(resources_path, yaml_arg):
    with open(os.path.join(resources_path, 'processing.yml'), 'r') as file:
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

    def cleanup(self):
        if self._file_monitor:
            self._file_monitor.stop()
            self._file_monitor.join(timeout=self.FILE_MONITOR_TIMEOUT)
            if self._file_monitor.is_alive():
                output_simulate.FileMonitor.terminate(self._file_monitor)
        self._file_monitor = None