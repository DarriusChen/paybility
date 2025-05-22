import argparse

from file_validator import PathValidator

parser = argparse.ArgumentParser(description='Paybility')

parser.add_argument('filepath', type=str, help='.xls path')
parser.add_argument('--maxyear', type=int, help='最大民國年限', default=150)
parser.add_argument('--minyear', type=int, help='最小民國年限', default=0)
parser.add_argument('--period', type=list, help='期別', default=['2', '3', '31', '4', '41', '5'])
parser.add_argument('--county', type=list, help='縣市', default=['台北', '新北', '桃園', '台中', '台南', '高雄', '彰化', '南投'])
parser.add_argument('--tables', type=list, help='表種', default=['表4', '表7', '表9', '表單4', '表單7', '表單9'])

def main(args):
    
    pv = PathValidator(args)
    
    pv.show_info()
    
    
if __name__ == "__main__":
    args = parser.parse_args()
    main(args)