import re
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from bins.txt_operation import String2List

class PD():
    def __init__(self,PdList):
        super().__init__()
        self.__source_pd_list={}
        if isinstance(PdList,str):
            self.__source_pd_list=String2List(PdList)
        else:
            self.__source_pd_list=PdList
        self.__pd_dict={}
        self.__pax_dict_in_list=[]
        self.ErrorMessage=[]
        self.AsvcKeys = []  # The list stores keys that has a property of 'ASVC' from __pd_dict.
        self.__item_with_properties = {}
        self.__separate_pd_items()
        self.Properties = self.collect_properties()
        self.__add_none_existing_properties()
        self.__fill_out_pax_dict()
        self.__verified_all_sn()
        return
    
    def GetLastCount(self,PdTextList=[]):
        pattern = re.compile(r'\d+\.\s')
        if len(PdTextList)==0:
            sn_values = [int(item['sn'].strip()) for item in self.__pax_dict_in_list]
            if len(sn_values) == 0:
                return 0
            else:
                return max(sn_values)
        else:
            for line in reversed(PdTextList):
                match=pattern.search(line)
                if match:
                    name_line = self.__split_first_line(line)
                    return name_line[0]
        return 0
            
    def __separate_pd_items(self):
        pattern_1st_line=re.compile(r'\d+\.\s')
        pattern_spaces = r'^ {22}'
        key = 0
        for line in self.__source_pd_list:
            if len(line.strip()) == 0:
                continue
            if line == 'NIL':
                break
            match_1st_line=pattern_1st_line.search(line)
            if match_1st_line:
                key=int(line[:3])# the serial number without '.'
                new_list=[line]
                self.__pd_dict[key]=new_list
                continue
            else:
                if re.match(pattern_spaces,line):
                    if key==0:
                        continue
                    self.__pd_dict[key].append(line)
                    continue
        return
    
    def __fill_out_pax_dict(self):
        for key in self.__pd_dict:
            pd_split=self.__split_first_line(self.__pd_dict[key][0])
            new_item = {}  # Create a new dictionary for each item
            new_item['sn'] = pd_split[0]
            new_item['name'] = pd_split[1]
            new_item['bn'] = pd_split[2]
            new_item['seat'] = [pd_split[3]]
            new_item['cls'] = pd_split[4]
            for line in self.__pd_dict[key][1:]:
                seat2 = self.__capture_2nd_seat(line)
                if seat2 is not None:
                    new_item['seat'].append(seat2)
            self.__pax_dict_in_list.append(new_item)
        return

    def __split_first_line(self, first_line_text):
        try:
            sn=first_line_text[0:3]
            pax_name=first_line_text[6:21]
            pax_name=pax_name.rstrip().lstrip()
            pax_name=pax_name.replace('+','')
            bn=first_line_text[28:31]
            pax_seat=first_line_text[33:37]
            pax_seat=pax_seat.rstrip()
            pax_cls=first_line_text[40]
            return sn,pax_name,bn,pax_seat,pax_cls
        except:
            self.ErrorMessage.append("An Error occured of "+first_line_text)
        return False

    def __capture_2nd_seat(self,line):
        pattern=re.compile(r'\s\d{2}[A-L]\s')
        match=pattern.search(line)
        if match:
            return line[match.start()+1:match.end()-1]
        
    def GetSameNames(self):
        name_messages=[]
        # Dictionary to track names and their corresponding 'sn' values
        name_to_sn = {}
        # Loop through each item in the list
        for item in self.__pax_dict_in_list:
            name = item['name']
            if 'ZZZZ' in name:
                continue
            sn = item['sn'].strip()  # Strip any leading/trailing whitespace from 'sn'
            if name in name_to_sn:
                name_to_sn[name].append(sn)
            else:
                name_to_sn[name] = [sn]
        # Find names with multiple 'sn' values and return them
        duplicates = {name: sns for name, sns in name_to_sn.items() if len(sns) > 1}
        for name, sns in duplicates.items():
            name_messages.append(f"Name: {name}, PRPD#: {sns}")
        if not len(name_messages):
            name_messages.append('None of Duplicate Names.')
        return name_messages
        

    def GetSameSeats(self):
        seat_messages=[]
        # Dictionary to track seats and their corresponding 'sn' values
        seat_to_sn = {}
        # Loop through each item in the list
        for item in self.__pax_dict_in_list:
            sn = item['sn'].strip()  # Strip any leading/trailing whitespace from 'sn'
            for seat in item['seat']:
                if seat in seat_to_sn:
                    seat_to_sn[seat].append(sn)
                else:
                    seat_to_sn[seat] = [sn]
        # Find seats with multiple 'sn' values and return them
        duplicates = {seat: sns for seat, sns in seat_to_sn.items() if len(sns) > 1}
        for seat, sns in duplicates.items():
            seat_messages.append(f"Seat: {seat}, PRPD#: {sns}")
        if not len(seat_messages):
            seat_messages.append('None of Duplicate Seats.')
        return seat_messages
    
    def __verified_all_sn(self):
        # Extract 'sn' values, strip whitespace, and convert to integers
        sn_values = [int(item['sn'].strip()) for item in self.__pax_dict_in_list]
        if len(sn_values)==0:
            return
        # Sort the 'sn' values
        sn_values.sort()
        # Find the missing 'sn' values
        missing_sn = []
        for i in range(1, sn_values[-1]):
            if i not in sn_values:
                missing_sn.append(i)
        if len(missing_sn):
            self.ErrorMessage.append(r"Missing the following PRPD#:\n")
            self.ErrorMessage.append(missing_sn)
        return

    def collect_properties(self):
        property_counts = {}
        for key, lines in self.__pd_dict.items():
            item_properties = set()  # Use a set to avoid counting duplicates within an item
            for i, line in enumerate(lines):
                if len(line) > 45:
                    if i == 0:  # First line of the item
                        properties = line[52:].split()  # Start from 52nd character (45 + 7)
                    else:
                        properties = line[45:].split()
                    item_properties.update(properties)           
            self.__item_with_properties[key] = list(item_properties)
            for prop in item_properties:
                if prop in property_counts:
                    property_counts[prop] += 1
                else:
                    property_counts[prop] = 1               
                # Record the key if 'ASVC' is found
                if prop == 'ASVC' and key not in self.AsvcKeys:
                    self.AsvcKeys.append(key)                 
        return property_counts
    
    def __add_none_existing_properties(self):
        # NET
        # Count items without 'ID' and 'ET' properties
        net_count = sum(1 for key, props in self.__item_with_properties.items() 
                if 'ID' in props and 'ET' not in props)
        # Add 'NET' to Properties
        self.Properties['NET'] = net_count



def main():
    import sys
    import os
    from bins.txt_operation import ReadTxt2List
    # Get the absolute path of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Add the parent directory of 'bins' to the Python path
    project_root = os.path.dirname(os.path.dirname(current_dir))
    pd_sample_path = os.path.join(project_root, 'resources', 'samples', 'pdStar.txt')
    print(pd_sample_path)
    pdcontent = ReadTxt2List(pd_sample_path)
    pd = PD(pdcontent)
    print(pd.Properties)
    print(pd.AsvcKeys)
    #print(pd.GetSameNames())
    #print(pd.GetSameSeats())
    #print(pd.GetLastCount(pdcontent))
    #print(pd.ErrorMessage)
if __name__ == "__main__":
    main()