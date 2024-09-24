from bins.txt_operation import ReadTxt2List, String2List
import re

class SE:
    def __init__(self,SeContent,Symbol:str):
        super().__init__()
        if isinstance(SeContent,str):
            self.__se_content = String2List(SeContent)
        else:    
            self.__se_content=SeContent
        self.individual_seats=[]
        self.combination_seats=[]
        self.FirstLineIndex = self.__SearchSe()
        self.GetListOfSymbol(Symbol)

    def __SearchSe(self):
        for index, line in enumerate(self.__se_content):
            if line.find('SE:') != -1:
                return index

    def __combination_seats(self):
        seats=[]
        for seat in reversed(self.individual_seats):
            current_row=seat[:2]
            bol_found = False
            for i in range(0,len(seats)):
                exsit_row=seats[i][:2]
                if current_row == exsit_row:
                    seats[i]=seats[i] + seat[-1]
                    bol_found = True
                    break
            if not bol_found:
                seats.append(seat)
        return seats

    def __sort_by_row(self):
        # Regex pattern to match leading digits
        pattern = re.compile(r'^\d+')
        # Extract the leading digits and convert to integer for sorting
        sorted_list = sorted(self.combination_seats, key=lambda x: int(pattern.match(x).group()) if pattern.match(x) else 0)
        return sorted_list

    def GetListOfSymbol(self,Symbol):
        columns = {}
        coordinates = {}
        # 先找有数据的列，并整理列号。
        digit10=0
        for i, char in enumerate(self.__se_content[self.FirstLineIndex+2]):
            if char.isdigit():
                if self.__se_content[self.FirstLineIndex+1][i].isdigit():
                    digit10=int(self.__se_content[self.FirstLineIndex+1][i]) * 10
                column_number = int(char) + digit10
                columns[i] = column_number

        # 跳过前两行，根据已有的列号，找每行内的非数字，非空格，非回车。
        # 然后逆向查找前面的字母，且这个字母所在列的第一行是一个字母。
        # 写入座位号。
        for i, line in enumerate(self.__se_content):
            if i > self.FirstLineIndex+2 and len(line) > 4:# 跳过指令和坐标段，且跳过空行或者只有>
                for key in columns:
                    char = line[key]
                    if not char.isdigit() and not char.isspace() and char != '\n':
                        for n in range(key-1,0,-1):
                            if line[n].isalpha() and self.__se_content[self.FirstLineIndex+1][n].isalpha():
                                coordinates[f"{columns[key]}{line[n]}"]=char
                                break

        # Find the coordinates where the character is the Symbol
        for key, char in coordinates.items():
            if char == Symbol:
                self.individual_seats.append(key)

        self.combination_seats = self.__combination_seats()
        self.combination_seats = self.__sort_by_row()

def main():
    se=SE(ReadTxt2List(r'C:\Users\gostn\OneDrive\桌面\eterm\se.txt'),'X')
    print(se.individual_seats)
    print(se.combination_seats)
if __name__ == "__main__":
    main()