import re
from bins.txt_operation import String2List
class AV():
    def __init__(self,AvContent):
        super().__init__()
        if isinstance(AvContent,str):
            self.__content=String2List(AvContent)
        else:
            self.__content=AvContent
        for line in self.__content:
            if line[:3]=='LAX':
                new_line = line[:22]
                pattern=re.compile(r'\d+(\+\d)?')
                try:
                    matches=[match.group(0) for match in re.finditer(pattern, new_line)]
                    self.Etd=matches[0]
                    self.Eta=matches[1]
                except:
                    print('AV Class malfunction.')
                break


def main():
    from txt_operation import ReadTxt2String
    content=ReadTxt2String(r'C:\Users\gostn\OneDrive\桌面\eterm\av.txt')
    av=AV(content)
    print(av.eta,av.etd)
if __name__=="__main__":
    main()