import yaml
import os
import re
import time
from datetime import datetime, timedelta
from bins.key_output_core import output_simulate
from bins.key_output_core.output_simulate import is_thread_alive, terminate_thread
from bins.commands_processing import handle_sy, handle_av, handle_se,handle_pd

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


    def get_file_path(self, yaml_arg):
        default_log_folder = self.config['default_log_folder']
        default_log_name_re = self.config['default_log_name_re']
        return self.find_related_log_file(default_log_folder, default_log_name_re, yaml_arg[3], yaml_arg[4])


    @staticmethod
    def find_related_log_file(folder_path, file_name_pattern, arrival_date, departure_date):
        related_date = datetime.strptime(departure_date, '%Y-%m-%d')
        arrival_date = datetime.strptime(arrival_date, '%Y-%m-%d')
        matching_files = []
        for _ in range(2):  # Try departure_date and arrival_date
            date_str = related_date.strftime('%Y_%m_%d')
            files = [f for f in os.listdir(folder_path) if f.startswith(date_str) and re.match(file_name_pattern, f)]
            if files:
                # Sort files by modification time (newest first)
                files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
                matching_files.extend([os.path.join(folder_path, f) for f in files])
            if related_date == arrival_date:
                break
            else:
                related_date = arrival_date  # Try arrival_date
        return matching_files if matching_files else None




class ButtonLogic:
    def __init__(self):
        super().__init__()
        self._arrival_flight=''
        self._arrival_leg=''
        self._SeatCnf=''
        self._ac_reg=''
        self._arrival_pax=''
        self._arrival_block_seats=''
        self._departure_pax=''
        self._departure_eta=''
        self._departure_bdt=''
        

    def arrival_button_logic(self, resources_path, yaml_arg):
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
            file_paths = config_manager.get_file_path(yaml_arg)
            if not file_paths:
                return False, "No suitable log file found for departure or arrival date."
            
            # Create a single FileMonitor for all file paths
            file_monitor = output_simulate.FileMonitor(file_paths)
            file_monitor.start()
            
            mouse.start()
            time.sleep(0.1)
            while mouse.is_alive() and file_monitor.is_alive():
                if mouse.count > 0:
                    file_result = []
                    for command_dict in config['arrival_section']:
                        time.sleep(0.1)
                        # Execute command once for all monitored files
                        send_key.execute_command(command_dict['command'], file_monitor.get_latest_result, bPrint=False)
                        result = file_monitor.get_latest_result()
                        if result:
                            file_result.append(result)
                        
                        if command_dict['pages_command'] is not None:
                            if "PN" not in command_dict['pages_command']:
                                send_key.execute_command(command_dict['pages_command'], file_monitor.get_latest_result, bPrint=False)
                                result = file_monitor.get_latest_result()
                                if result:
                                    self.add_new_items(file_result, result)
                            else:
                                while True:
                                    send_key.execute_command(command_dict['pages_command'], file_monitor.get_latest_result, bPrint=False)
                                    result = file_monitor.get_latest_result()
                                    if result:
                                        added, file_result = self.add_new_items(file_result, result)
                                        if not added:
                                            break
                    if 'SY:' in command_dict['command']:
                        sy = handle_sy.SY(file_result, yaml_arg[5])
                        self._arrival_flight = sy.flight
                        self._arrival_leg = sy.leg
                        self._SeatCnf = sy.seat_configuration
                        self._ac_reg = sy.ac_reg
                        self._arrival_pax = sy.checked
                    elif 'SE:' in command_dict['command']:
                        se = handle_se.SE(file_result, 'X')
                        self._arrival_block_seats = se.combination_seats
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