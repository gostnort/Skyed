from bins.key_output_core import output_simulate
from bins.commands_processing import handle_sy, handle_se, handle_pd
import yaml
import os
import re

class Buttons():
    MOUSE_CLICK_LIMIT = 2
    FILE_MONITOR_TIMEOUT = 2

    def __init__(self, resources_path):
        self.resources_path = resources_path
        self._send_key = output_simulate.SendKey()
        self._mouse = output_simulate.MouseClickMonitor(self.MOUSE_CLICK_LIMIT)
        self._file_monitor = None
        self.yaml_config = None

    def initialize(self, yaml_arg):
        try:
            self.yaml_config = self.load_and_prepare_yaml(self.resources_path, yaml_arg)
            file_path = self.yaml_config['default_path']
            self._file_monitor = output_simulate.FileMonitor.create_and_start(file_path, callback=self.file_change_callback)
            return True, ""
        except Exception as e:
            return False, str(e)

    def arrival_button_logic(self):
        if not self.yaml_config:
            return False, "Buttons class not initialized"

        try:
            self._mouse.start()

            result_string = ""
            last_result = ""

            # Process commands
            for command_dict in self.yaml_config['arrival_section']:
                if not self._mouse.is_alive():
                    break

                # Send main command
                result = self.send_command_and_get_result(command_dict['command'])
                result_string += self.process_result(result, last_result)
                last_result = result

                # Process page command if exists
                if 'pages_command' in command_dict:
                    while 'PN' in command_dict['pages_command']:
                        result = self.send_command_and_get_result(command_dict['pages_command'])
                        result_string += self.process_result(result, last_result)
                        last_result = result
                        if '+\n' not in result:
                            break

            # Process the command head
            command_head = self.extract_command_head(result_string)
            if command_head:
                self.process_command_head(command_head)

            return True, result_string
        except Exception as e:
            return False, str(e)
        finally:
            self._mouse.stop()
            self._mouse.join(timeout=self.FILE_MONITOR_TIMEOUT)

    def send_command_and_get_result(self, command):
        self._send_key.execute_command(command, self._file_monitor.get_latest_result, bPrint=False)
        return self._file_monitor.get_latest_result(timeout=self.FILE_MONITOR_TIMEOUT)

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

    def cleanup(self):
        if self._file_monitor:
            self._file_monitor.stop()
            self._file_monitor.join(timeout=self.FILE_MONITOR_TIMEOUT)
            if self._file_monitor.is_alive():
                output_simulate.FileMonitor.terminate(self._file_monitor)
        self._file_monitor = None