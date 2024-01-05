import camelot
from datetime import date, timedelta
import pandas as pd
import numpy as np


def get_backfill_dates():

  """
  This function runs each day. It generates a pandas series of dates in the past 30 days where the jail did not upload data on the same day when the pdf scraper ran.
  """

  bf_df = pd.read_csv('https://raw.githubusercontent.com/brandendupont-mcw/git_scrape_cook_jail/main/data/cook-jail-data.csv')

  #convert date col to datetime  
  bf_df['Date'] = pd.to_datetime(bf_df['Date'], errors='coerce')

  #make sure the data is a date
  assert bf_df['Date'].dtype.type == np.datetime64

  #grab the last 30 days of the dataset
  last_30 = bf_df.set_index('Date').last('30D')

  #generate a backfill range  
  backfill_range = pd.date_range(last_30.index.min(), last_30.index.max())

  #return non intersect array of the two date lists
  # AKA, all dates not stored in the pdf file
  return pd.Series(np.setxor1d(last_30.index, backfill_range))


def parse_append_pdf(pdf_day, pdf_month=None, pdf_year=None):

    """
    A function to parse and append jail data.
    """

    
    # import data
    PAST_JAIL_DATA = pd.read_csv("data/cook-jail-data.csv")
    FAILED_URL = pd.read_csv("data/failed_url.csv")

  
    today_yr = date.today().year
    today_month =  date.today().month
    
    # run the scraper on a day lag
    today_day =  pdf_day

    # add leading zeros to single digit month and days to match the sherrif's pdf template
    if pdf_month == None:
        month = "{:02d}".format(today_month)
    else:
        month = "{:02d}".format(pdf_month)

    if pdf_year == None:
        year = "{:02d}".format(today_yr)
    else:
        year = "{:02d}".format(pdf_year)
        
    day = "{:02d}".format(today_day)

    #drop this later
    today_month = "{:02d}".format(today_month)

    # create the templated pdf
    #pdf_url = f"https://www.cookcountysheriffil.gov/wp-content/uploads/{year}/{month}/CCSO_BIU_CommunicationsCCDOC_v1_{year}_{month}_{day}.pdf"

    #backfill new url briefly used
    pdf_url =  f"https://www.cookcountysheriffil.gov/wp-content/uploads/{today_yr}/{today_month}/CCSO_BIU_CommunicationsCCDOC_v1_{year}_{month}_{day}.pdf"

    # parse the pdf
    try:
        #parse the pdf table
        df = camelot.read_pdf(pdf_url)
        pdf_date = str.replace(str(pdf_url).split(".")[-2].split("/")[-1].split("v1_")[-1], "_", "-")
        
        if len(df) == 1:
            dfs = df[0].df

            dfs.to_csv(f'data/{pdf_date}-parsed-pdf-table.csv', index=False)

            # replace any null values
            dfs = dfs.replace('', np.nan)
            # remove any completely null rows
            dfs = dfs.dropna(axis=1, how='all')

            # split any tables with the table in one row seperated by a /n character
            if dfs.shape[1] < 2:
                dfs[[0,1]] = dfs[0].str.split('\n', expand=True)
                dfs = dfs.replace('', np.nan)
                dfs = dfs.dropna(axis=1, how='all')

            dfs[0] = dfs[0].str.strip().str.lower().str.replace(" ","-")

            #subset to only include these values
            dfs = dfs[dfs[0].isin(['total-male-and-female',
                'jail-population', 'community-corrections'])]


            dfs['Date'] = pdf_date

            # make sure the dataframe is the correct size before appending
            if dfs.shape == (3, 3):
                
                dfs[0] = dfs[0].str.strip().str.title().str.replace("-"," ")
                #pivot data horizontally
                pdf_table_final = dfs.pivot(index='Date', columns=0, values=1).reset_index()
                
                # remove any commas in the table
                pdf_table_final[['Community Corrections', 'Jail Population',
            'Total Male And Female']] = pdf_table_final[['Community Corrections', 'Jail Population',
            'Total Male And Female']].apply(lambda x: x.str.replace(",",""))
                
                print(pdf_table_final.head())
                
                combine = pd.concat([PAST_JAIL_DATA, pdf_table_final])
                
                #ensure types are numeric
                combine[['Jail Population', 'Community Corrections',
            'Total Male And Female']].apply(lambda x: pd.to_numeric(x))
                
                # ensure dates are dates
                combine['Date'] = pd.to_datetime(combine['Date'])

                #deduplicate
                combine = combine.groupby('Date').first().reset_index()

                #overwrite and save data
                combine.to_csv('data/cook-jail-data.csv', index=False)

        else:
            print("PDF Report Name: ", pdf_url, " had more than one table")
            print("unsuccessful pdf table parse:",pdf_url)

    except:
        url_failed = True
        print("unsuccessful:",pdf_url)
        # save failed url if the pdf broke
        if url_failed == True:

            # add the failed dataset to pandas
            FAILED_URL['failed_url'] = FAILED_URL['failed_url'].add(pdf_url)

            #overwrite and save data
            FAILED_URL.to_csv('data/failed_url.csv', index=False)




if __name__ == "__main__":

    today_day =  date.today().day
    weekday = date.today().weekday()

    backfill_dates = get_backfill_dates()

    #on mondays parse pdfs that are updated on the weekend
    if weekday == 0:

        saturday = (date.today() - timedelta(days = 2)).day
        sunday = (date.today() - timedelta(days = 1)).day

        for pdf_day in [today_day, saturday, sunday]:
            
            parse_append_pdf(pdf_day=pdf_day)
        
        # perform any backfill pdf parsing 
        if len(backfill_dates) > 0:
        
            for day in backfill_dates:

                parse_append_pdf(pdf_day=day.day, pdf_month=day.month, pdf_year=day.year)


    # parse pdfs normally Tuesday-Friday
    elif (weekday > 0) & ( weekday < 5):

        parse_append_pdf(pdf_day=today_day)
    
        # perform any backfill pdf parsing 
        if len(backfill_dates) > 0:
        
            for day in backfill_dates:

                parse_append_pdf(pdf_day=day.day, pdf_month=day.month, pdf_year=day.year)





