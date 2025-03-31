# A gitscraper to pull down Chicago incident data.

A Python script that collects Chicago incident data for the Cook County Dashboard.

## Enable Git Large File Storage to Save this Data

- download it here https://git-lfs.com/
- changed the script to import reference tables as.txt (convert to parquet for later?)
- add git lfs track "*incident.csv"
- Ran a small subset as a test
- Then ran the full file


## Execution :

- the Github Action action is scheduled daily.

- the `flat.yml` specifies the action, triggers the install of python, and installs the required dependencies. 

- the `postprocess.py` script is then trigged and parses the csv table into a cleaned pandas dataframe.
  
## Data Notes

- Data is taken from the [Chicago Incident Data]([https://www.cookcountysheriffil.gov/jail-population-data/](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2/about_data))
- Data begins at 01-01-2018 and is updated daily.


## Maintainted by the Loyola Center for Criminal Justice.

<img src="https://loyolaccj.org/static/images/ccj-loyola-black.svg" alt="drawing" width="250"/> 

