import yaml
import os
import re
import time
from datetime import datetime, timedelta
from bins.key_output_core import output_simulate
from bins.key_output_core.output_simulate import is_thread_alive, terminate_thread

class ConfigManager:
    def __init__(self, resources_path):
        self.resources_path = resources_path
        self.config = self.load_yaml()

    def load_yaml(self):
        with open(os.path.join(self.resources_path, 'processing.yml'), 'r') as file:
            return yaml.safe_load(file)

    def prepare_yaml(self, yaml_arg):
        for section in self.config.values():
            if isinstance(section, list):
                for item in section:
                    if 'command' in item:
                        item['command'] = item['command'].format(
                            airline=yaml_arg[0],
                            arrival_flight_number=yaml_arg[1],
                            departure_flight_number=yaml_arg[2],
                            arrival_date=yaml_arg[3],
                            departure_date=yaml_arg[4],
                            arrival=yaml_arg[5],
                            ac_reg=None,
                        )
        return self.config

    def get_file_path(self):
        default_log_folder = self.config['default_log_folder']
        default_log_name_re = self.config['default_log_name_re']
        return self.find_latest_log_file(default_log_folder, default_log_name_re)

    @staticmethod
    def find_latest_log_file(folder_path, file_name_pattern):
        today = datetime.now()
        
        for _ in range(2):  # Try today and yesterday
            date_str = today.strftime('%Y_%m_%d')
            files = [f for f in os.listdir(folder_path) if f.startswith(date_str) and re.match(file_name_pattern, f)]
            
            if files:
                # Sort files by modification time (newest first)
                files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
                return os.path.join(folder_path, files[0])
            
            today -= timedelta(days=1)  # Try yesterday's date
        
        return None  # If no file is found

class ButtonLogic:
    def __init__(self):
        super().__init__()

    def arrival_button_logic(self,resources_path, yaml_arg):
        config_manager = ConfigManager(resources_path)
        mouse = None
        file_monitor = None
        send_key = None
        STOP_LISTEN_MOUSE = 2
        TIME_OUT_SECOND = 1
        try:
            config = config_manager.prepare_yaml(yaml_arg)
            mouse = output_simulate.MouseClickMonitor(STOP_LISTEN_MOUSE)
            send_key = output_simulate.SendKey()
            file_path = config_manager.get_file_path()
            if not file_path:
                return False, "No suitable log file found for today or yesterday."
            file_monitor = output_simulate.FileMonitor.create_and_start(file_path, callback=file_change_callback)
            mouse.start()
            time.sleep(0.1)
            while mouse.is_alive() and file_monitor.is_alive():
                if mouse.count > 0:
                    for command_dict in config['arrival_section']:
                        time.sleep(0.1)
                        send_key.execute_command(command_dict['command'], file_monitor.get_latest_result, bPrint=False)
                        if command_dict['pages_command'] != None:
                            if "PN" not in command_dict['pages_command']:
                                send_key.execute_command(command_dict['pages_command'], file_monitor.get_latest_result, bPrint=False)
                            else:
                                file_result = []
                                while not self.add_new_items(file_result, file_monitor.result):
                                    send_key.execute_command(command_dict['pages_command'], file_monitor.get_latest_result, bPrint=False)
            return True, ""
        except FileNotFoundError as e:
            return False, f"Configuration file not found: {str(e)}"
        except yaml.YAMLError as e:
            return False, f"Error in YAML configuration: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
        finally:
            self.cleanup(mouse, file_monitor, send_key)

    def add_new_items(self,list_1, list_2, n=6):
        if list_1 == list_2:
            return True, list_1 # this is for the first adding.
        # Determine the comparison range: use all of list_1 if it's shorter than list_2
        comparison_range = list_1[-len(list_2):] if len(list_1) >= len(list_2) else list_1
        # Check if list_2 is already included in list_1
        if all(item in list_1 for item in list_2):
            return False  # If all items in list_2 are already in list_1, return False
        # Advanced mode: check if the first `n` items match between the end of list_1 and the start of list_2
        consecutive_match = True
        for i in range(min(n, len(list_1), len(list_2))):  # Limit to the shortest list or `n`
            if list_1[-(i+1)] != list_2[-(i+1)]:
                consecutive_match = False
                break
        # Flag to indicate if something was added
        added = False
        # If advanced mode conditions are met (n consecutive items match), append the rest of list_2
        if consecutive_match and len(list_1) >= n:
            list_1.extend(list_2[n:])
            added = True
        else:
            # Fall back to single-item comparison mode
            for item in list_2:
                if item not in comparison_range:
                    list_1.append(item)
                    added = True
        return added, list_1  # Return True if something was added, False otherwise


    def cleanup(self, mouse, file_monitor, send_key=None):
        threads_to_cleanup = [
            ('MouseClickMonitor', mouse),
            ('FileMonitor', file_monitor),
            ('SendKey', send_key)
        ]

        for thread_name, thread in threads_to_cleanup:
            if thread:
                print(f"Stopping {thread_name} thread...")
                thread.stop()
                thread.join(timeout=5)  # Wait for up to 5 seconds for the thread to stop

                if is_thread_alive(thread):
                    print(f"{thread_name} thread couldn't be terminated normally. Forcing termination...")
                    terminate_thread(thread)
                    thread.join(timeout=1)  # Give it a moment to terminate

                if not is_thread_alive(thread):
                    print(f"{thread_name} thread terminated.")
                else:
                    print(f"Failed to terminate {thread_name} thread.")

        print("Cleanup completed.")