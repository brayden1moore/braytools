# Braytools
Module with some useful tools for data validation. Mostly for personal use.

TO USE:
* Clone git repository to python working directory
* In your .py or .ipynb file, <code>import braytools as bt</code>

METHODS:
* <code>isrealname(names,lastname=False)</code> iterates through a given list and returns a dict of each unique list item and the likelihood that it is a name using the Names Dataset.
* <code>validateemails(emails)</code> iterates through a given list and returns a dict of each list item and and whether it is a valid email.
* <code>validateaddressesGoogle(addList)</code> iterates through a given list and returns a dict of each list item and whether it is a valid address using Google Maps API.
* <code>validateaddressesNCOA(fname,lname,address,city,state,zipcode,country)</code> takes lists of address components and generates an official NCOA report using TrueNCOA API.
* <code>getcoords(addList)</code> iterates through a given list of addresses and returns a dict of each list item and its coordinates using Nominatim API.
* <code>namesinemail(emails)</code> iterates through a given list of emails and returns a dict of each list item and any names found in it using the Names Dataset.
* <code>dupes(df)</code> searches a dataframe for potential duplicate names and returns a new dataframe with each names' potential duplicates.
* <code>retentionDate(df,yearCol,contactIdCol)</code> iterates through a transaction dataframe and returns a dataframe with each year's 1-year and 2-year retention rates.

NOTE:
* The "APIKEYS.json" file does not contain any APIs. If it does, I have screwed up. 
* Google Cloud API keys can be obtained here: https://console.cloud.google.com/apis/credentials
* TrueNCOA API keys can be obtained here: https://truencoa.com/api/
