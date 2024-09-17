from bins.key_output_core import output_simulate
from bins.commands_processing import handle_sy, handle_se, handle_pd
import yaml
import os
import re

class Buttons():
    def __init__(self, resources_path, yaml_arg):
        super().__init__()
        try:
            self.yaml_config = self.load_and_prepare_yaml(resources_path, yaml_arg)
        except Exception as e:
            return False, str(e)
        
    def arrival_button_logic(self):
        try:
            # Initialize required classes
            send_key = output_simulate.SendKey()
            mouse = output_simulate.MouseClickMonitor(2)  # Assuming 2 clicks as the limit
            file_path = self.yaml_config['default_path']
            file_monitor = output_simulate.FileMonitor.create_and_start(file_path, callback=self.file_change_callback)

            # Start mouse monitoring
            mouse.start()

            result_string = ""
            last_result = ""

            # Process commands
            for command_dict in self.yaml_config['arrival_section']:
                if not mouse.is_alive():
                    break

                # Send main command
                result = self.send_command_and_get_result(send_key, command_dict['command'], file_monitor)
                result_string += self.process_result(result, last_result)
                last_result = result

                # Process page command if exists
                if 'pages_command' in command_dict:
                    while 'PN' in command_dict['pages_command'] and '+\n' in result:
                        result = self.send_command_and_get_result(send_key, command_dict['pages_command'], file_monitor)
                        result_string += self.process_result(result, last_result)
                        last_result = result

            # Process the command head
            command_head = self.extract_command_head(result_string)
            if command_head:
                self.process_command_head(command_head)

            return True, result_string
        except Exception as e:
            return False, str(e)
        finally:
            # Clean up
            mouse.stop()
            file_monitor.stop()
            output_simulate.terminate_thread(mouse)
            output_simulate.terminate_thread(file_monitor)

    def send_command_and_get_result(self, send_key, command, file_monitor):
        send_key.execute_command(command, file_monitor.get_latest_result, bPrint=False)
        return file_monitor.get_latest_result(timeout=1)  # 1 second timeout

    def process_result(self, new_result, last_result):
        if new_result:
            return new_result.replace(last_result, '', 1)
        return ""

    def extract_command_head(self, result_string):
        match = re.search(r'>(.*?):', result_string)
        return match.group(1) if match else None

    def process_command_head(self, command_head):
        command_handlers = {
            "SY": handle_sy.SY,
            "SE": handle_se.SE,
            "PD": handle_pd.PD
        }

        for suffix, handler in command_handlers.items():
            if command_head.endswith(suffix):
                handler()
                break

    def load_and_prepare_yaml(self, resources_path, yaml_arg):
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