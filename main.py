# This is a sample Python script.
import cnki_analyser


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

collection_name = 'intangible_heritage'
data_source = 'DataSource/非遗数字化.txt'
output_dir = 'result'

analyser = cnki_analyser.CNKIAnalyser(collection_name, data_source)
analyser.data_loader()
analyser.output_stat_result(output_dir)
