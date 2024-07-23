import re
from datetime import datetime
class SY():
    def __init__(self,SyContent,Arrival=''):
        super().__init__()
        self.flight=''
        self.flight_date=''
        self.ac_type=''
        self.ac_reg=''
        self.ret_minus_id=''
        self.checked=''
        self.gate=''
        self.leg=''
        self.bdt=''
        self.seat_configuration=''
        self.__arrival = str(Arrival)
        self.__sy_content = SyContent
        self.__run()
        self.Pattern = ''

    def __run(self):
        last_index = self.__get_start()
        if last_index == 0:
            return
        last_index = self.__get_flight_date(last_index)
        last_index = self.__get_ac_type(last_index)
        last_index = self.__get_gate(last_index)
        last_index = self.__get_bdt(last_index)
        last_index = self.__get_Cnf(last_index)
        if self.__arrival != '':
            self.leg= self.__arrival + "LAX"
            last_index = self.__get_checked(last_index)
        else:
            last_index = self.__get_leg(last_index)
            last_index = self.__get_ret_minus_id(last_index)

    def __get_start(self):
        try:
            station = 'LAX' if self.__arrival == "" else self.__arrival
            pattern = r'SY:.*' + station+r'.*'
            match=re.search(pattern,self.__sy_content)
            if match:
                self.Pattern = pattern
                return match.start()
            else:
                return 0
        except ValueError as e:
            print("__get_start() has an error.\n",e)
            return 0

    def __get_flight_date(self, last_index):
        try:
            pattern = r'CA\d{3}/\d{2}[A-Z]{3}\d{2}'
            match=re.search(pattern,self.__sy_content[last_index:])
            tmp=match.group(0)
            tmp_list=tmp.split('/')
            self.flight=tmp_list[0]
            self.flight_date=tmp_list[1]
            input_format = r"%d%b%y"
            # Parse the input date string into a datetime object
            parsed_date = datetime.strptime(tmp_list[1], input_format)
            # Format the parsed date into the desired output format
            output_format = r"%m-%d"
            self.flight_date = parsed_date.strftime(output_format)
            return match.end()
        except ValueError as e:
            print("__get_flight_date() has an error.\n",e)
            return 0

    def __get_ac_type(self,last_index):
        try:
            pattern=re.compile(r'\sTCI\s')
            match=re.search(pattern,self.__sy_content)
            last_index=match.end()
            pattern=re.compile(r'\d{3}/.*?/B\d{4}')
            match=re.search(pattern,self.__sy_content[last_index:])
            self.ac_type=match.group(0)
            split_ac_type=self.ac_type.split('/')
            self.ac_reg=split_ac_type[2]
            return match.end()
        except ValueError as e:
            print("__get_ac_type() has an error.\n",e)
            return 0
        
    def __get_gate(self,last_index):
        try:
            pattern=re.compile(r'\sGTD/.*?\s')
            match=re.search(pattern,self.__sy_content[last_index:])
            self.gate=match.group(0)
            self.gate=self.gate.split('/')[1]
            return match.end()
        except ValueError as e:
            print("__get_gate() has an error.\n",e)
            return 0
        
    def __get_bdt(self,last_index):
        try:
            pattern=re.compile(r'BDT\d{4}')
            match=re.search(pattern,self.__sy_content[last_index:])
            self.bdt=match.group(0)[3:]
            return match.end()
        except ValueError as e:
            print("__get_bdt() has an error.\n",e)
            return 0
        
    def __get_Cnf(self,last_index):
        try:
            pattern=re.compile(r'CNF/.*?\s')
            match=re.search(pattern,self.__sy_content[last_index:])
            self.seat_configuration=match.group(0)[4:]
            return match.end()
        except ValueError as e:
            print("__get_Cnf() has an error.\n",e)
            return 0    
    
    def __get_leg(self,last_index):
        try:
            pattern=re.compile(r'\*[A-Z]{6}\sR')
            match=re.search(pattern,self.__sy_content[last_index:])
            self.leg=match.group(0)[1:7]
            return match.end()
        except ValueError as e:
            print("__get_leg() has an error.\n",e)
            return 0
    
    def __get_ret_minus_id(self,last_index):
        try:
            pattern=re.compile(r'\s{3}SA\d+(/\d+)*')
            match=re.search(pattern,self.__sy_content[last_index:])
            id=match.group(0)
            id=id.lstrip()[2:]
            id_split=id.split('/')
            pattern=re.compile(r'\s{3}RET\d+(/\d+)*')
            match=re.search(pattern,self.__sy_content[match.end():])
            ret=match.group(0)
            ret=ret.lstrip()[3:]
            ret_split=ret.split('/')
            for index in range(0,len(ret_split)):
                if self.ret_minus_id != '':
                    self.ret_minus_id = self.ret_minus_id + '/'
                self.ret_minus_id = self.ret_minus_id + str(int(ret_split[index])-int(id_split[index]))
            return match.end()
        except ValueError as e:
            print("__get_ret_minus_id() has an error.\n",e)
            return 0
        
    def __get_checked(self,last_index):
        try:
            target_str='*'+self.__arrival
            while(1):
                tmp_sy=self.__sy_content[last_index:]
                if target_str in tmp_sy:
                    pattern=re.compile(r'\s{3}C\d+(/\d+)*')
                    match=re.search(pattern,tmp_sy)
                    tmp=match.group(0)[4:]
                    tmp_list=tmp.split('/')
                    total = 0
                    for n in tmp_list:
                        total = total + int(n)
                    last_index=last_index + match.end()
                    if total != 0:
                        self.checked=tmp
                        break
                else:
                    break
            return last_index
        except ValueError as e:
            print("__get_checked() has an error.\n",e)
            return 0
        


def main():
    from txt_operation import ReadTxt2String
    sy_content=ReadTxt2String(r'C:\Users\gostn\OneDrive\桌面\eterm\sy_transit.txt')
    sy=SY(sy_content,'IAD')
    print(sy.flight,sy.flight_date,sy.ac_reg,sy.ac_type,sy.bdt,sy.gate,sy.seat_configuration,sy.leg,sy.ret_minus_id)
if __name__ == "__main__":
    main()