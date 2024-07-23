import re
class BND():
    def __init__(self,BndCommand):
        super().__init__()
        self.__command=BndCommand
        #self.__find_deletes()
        self.numbers=self.__deleted_numbers()

    def __find_deletes(self):
        delete_index = self.__command.find("DELETED:")+9
        index = self.__command[delete_index:].find('\n')+1
        after_delete=self.__command[delete_index+index:]
        bol_comma=False
        if delete_index != -1:
            for c in after_delete:
                if c.isdigit():
                    self.numbers=self.numbers + c
                    bol_comma=True
                else:
                    if bol_comma:
                        self.numbers=self.numbers+','
                        bol_comma = False
                if c == '\n':
                    break
    
    def __deleted_numbers(self):
        # Find the 'DELETED:' section and extract numbers using regex
        deleted_section = re.search(r'DELETED:(.*?)\n', self.__command, re.DOTALL)
        after_delete=self.__command[deleted_section.end():]
        enter_index=after_delete.find('\n')
        after_delete=after_delete[:enter_index]
        if deleted_section:
            numbers_match = re.findall(r'\d+', after_delete)
            return ','.join(numbers_match)
        else:
            return ""

def main():
    sample = " DELETED:    \n   12  143         \nNONLAX:  1  5-6"
    result=BND(sample).numbers
    print(result)
if __name__ == "__main__":
    main()