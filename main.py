# This is a sample Python script.
import pandas as pd
# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    json_scrap = pd.read_json('orias/orias.json')
    sample = json_scrap.head(100)
    sample.to_csv('result.csv', sep=";", encoding='ansi')

