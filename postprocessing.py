import camelot
from datetime import date
import pandas as pd
import numpy as np



if __name__ == "__main__":

    # import data
    PAST_JAIL_DATA = pd.read_csv("data/cook-jail-data.csv")
    FAILED_URL = pd.read_csv("data/failed_url.csv")

  
    today_yr = date.today().year
    today_month =  date.today().month
    # run the scraper on a day lag
    today_day =  date.today().day - 1

    # add leading zeros to single digit month and days to match the sherrif's pdf template
    month = "{:02d}".format(today_month)
    day = "{:02d}".format(today_day)

    # create the templated pdf
    pdf_url = f"https://www.cookcountysheriffil.gov/wp-content/uploads/{today_yr}/{month}/CCSO_BIU_CommunicationsCCDOC_v1_{today_yr}_{month}_{day}.pdf"

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
            print("PDF Report Name: ", pdf_report_name, " had more than one table")
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





