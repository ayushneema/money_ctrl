"""
Created on Tue Oct 16 11:46:14 2018

@author: Ayush
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import datetime
import itertools
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = r'https://www.moneycontrol.com/mutual-funds/performance-tracker'
FILE_PATH  = r'C:\Users\Ayush\MarketData_Merged.xlsx'


def extractTable(fundCategory, dataType):
    url = '%s/%s/%s.html' % (BASE_URL, dataType, fundCategory)
    logger.info("Extracting data from: %s", url)
    resp = urlopen(url)
    soup = BeautifulSoup(resp.read())
    table = soup.find_all('table')[1]
    headers = [ str(headrtags.get_text()) for headrtags in table.find_all('th')[:-1]]
    data = []
    for row in table.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) >= len(headers):
            x = [str(columntag.get_text()) for columntag in columns[:-1]]
            if len(x) == 10 and ('Direct' in x[0] or 'D (G)' in x[0]):
               data.append(x)
    df = pd.DataFrame.from_records(data, columns = headers)
    df['date'] = datetime.date.today()
    df['fundCategory'] =fundCategory
    df['dataType'] = dataType
    return df


if __name__ == "__main__":
    fundCategories = ['large-cap', 'small-and-mid-cap', 'multi-cap-fund', 'mid-cap-fund', 'elss', 'balanced','focused-fund']
    dataTypes = ['returns', 'ranks']
    
    #Extract table from different links
    dataFrames = [ extractTable(*parmas) for parmas in itertools.product(fundCategories, dataTypes)]
    logger.info('No of rows extracted: %s' % len(dataFrames))
    
    old = pd.read_excel(r'C:\Users\Ayush\MarketData_Merged.xlsx')
    old = old[old.date != datetime.date.today()]
    dataFrames.append(old)
    df = pd.concat(dataFrames)
    logger.info('Total number of rows: %s' % len(df))
    df[['1mth', '3mth', '6mth', '1yr', '2yr', '3yr', '5yr']] = df[['1mth', '3mth', '6mth', '1yr', '2yr', '3yr', '5yr']].apply(pd.to_numeric, errors = 'coerce')
    writer = pd.ExcelWriter(FILE_PATH)
    df.to_excel(writer, datetime.date.strftime(datetime.date.today(), '%d-%b-%Y'), engine='xlsxwriter', index=False, columns= ['1mth', '3mth', '6mth', '1yr', '2yr', '3yr', '5yr', 'Mutual Fund Scheme', 'dataType', 'date', 'fundCategory'])
    writer.save()
    print('done')

