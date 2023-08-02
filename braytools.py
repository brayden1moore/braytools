import pandas as pd
import numpy as np
import requests
import json

from tqdm import tqdm
from names_dataset import NameDataset
nd = NameDataset()

def getApiKey(service):
    '''Reads API key from APIKEYS.json file'''

    # read file
    with open('braytools/APIKEYS.json', 'r') as myfile:
        data=myfile.read()

    # parse file
    obj = json.loads(data)
    return obj[service]


def isrealname(names,lastname=False):
    '''Iterates through a given list and returns a dict of 
    each unique list item and the likelihood that it is a name'''

    probDict = {}
    for name in set(names):
        
        name = str(name)
        prob = 0
        tokens = len(name.split(' '))
        
        if ' ' in name and tokens <= 3:
            i = name.split(' ')[0] 
        elif '-' in name and tokens <= 3:
            i = name.split('-')[0] 
        else:
            i = name

        if lastname:
            try:
                prob = (10000-sorted(list(filter(lambda v: v!=None, list(nd.search(i.replace("'",""))['last_name']['rank'].values()))))[0])/10000
            except:
                pass
        else:
            try:
                prob = (10000-sorted(list(filter(lambda v: v!=None, list(nd.search(i.replace("'",""))['first_name']['rank'].values()))))[0])/10000
            except:
                pass

        probDict[name] = max(prob,0)

    return probDict


def validateemails(emails):
    '''Iterates through a given list and returns a dict of each list 
    item and and whether it is a valid email.'''

    from email_validator import validate_email, EmailNotValidError
    
    errorDict = {}
    for e in emails:
        try:
            e = validate_email(e).email
            errorDict[e] = ''
        except EmailNotValidError as err:
            errorDict[e] = str(err)

    return errorDict


def validateaddressesGoogle(addList):
    '''Iterates through a given list and returns a dict of each list 
    item and whether it is a valid address using Google Maps API'''

    key = getApiKey('google')
    url = f'https://addressvalidation.googleapis.com/v1:validateAddress?key={key}'

    addDict = {}

    for i in addList:
        payload = {
            "address": {
                "addressLines": [f"{i}"]
            },
            "enableUspsCass": 'true'
            }

        hdr = {'Content-Type': 'application/json'}

        r = requests.post(url=url,data=json.dumps(payload),headers=hdr).json()
        
        try:
            try:
                addDict[i] = 'Missing ' + str(r['result']['address']['missingComponentTypes'])
            except:
                addDict[i] = r['result']['address']['formattedAddress']
        except:
            print(r,i)
        
    return addDict


def validateaddressesNCOA(fname,lname,address,city,state,zipcode,country):
    '''Takes lists of address components and generates an
     official NCOA report using TrueNCOA API'''

    import requests
    key = getApiKey('truencoa')

    url = "https://api.testing.truencoa.com/files//records"
    id = range(len(fname))
    payload = ''

    for i,f,l,a,c,s,z,p in zip(id,fname,lname,address,city,state,zipcode,country):
        payload += f"individual_id={i}&individual_first_name={'%'.join(f.split(' '))}&individual_last_name={'%'.join(l.split(' '))}&address_line_1={'%'.join(a.split(' '))}&address_city_name={'%'.join(c.split(' '))}&address_state_code={s}&address_postal_code={z}&address_country_code={p}&"

    headers = {
    'user_name': '{{api_user_name}}',
    'password': '{{api_password}}',
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print(payload)
    #response = requests.request("POST", url, headers=headers, data=payload)


def getcoords(addList):
    '''Iterates through a given list and returns a dict of each list 
    item and its coordinates using Nominatim API'''

    import requests
    import urllib.parse
    from tqdm import tqdm

    coordDict = {}

    for i in tqdm(addList):

        # using Nominatim to get coordinates, skipping if the request returns null
        try:
            url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(i) +'?format=json'
            response = requests.get(url).json()
            coordDict[i] = (response[0]["lat"],response[0]["lon"])
        except:
            coordDict[i] = (np.nan,np.nan)
        
    return coordDict


def namesinemail(emails):
    '''Iterates through a given list of emails and returns a dict of each list 
    item and any names found in it using the Names Dataset'''

    foundDict = {}
    for e in emails:
        try:
            token = e.split('@')[0]
            foundname = ''
            likelihood = 0
            for start in range(len(token)):
                for end in range(len(token))[1:(-start-1)]:
                    itertoken = token[start:start+end+2]
                    iterlikelihood = isrealname([itertoken])[itertoken]
                    if iterlikelihood>likelihood:
                        foundname = itertoken
                        likelihood = iterlikelihood
            else:
                foundDict[e] = (foundname,likelihood)
        except:
            foundDict[e] = ''

    return foundDict    
    

def dupes(df):
    '''Searches a dataframe for potential duplicate names 
    and returns a new dataframe with each names' potential duplicates'''
    
    from IPython.display import clear_output
    dupeDf = pd.DataFrame()
    iteration = 1

    for last_name in df.sort_values('Last Name')['Last Name'].unique():
        print(f"Searching through {iteration} / {len(df['Last Name'].unique())} unique last names for duplicates.")
        print(f"{round(iteration*100/len(df['Last Name'].unique()),2)}%")
        lastnameagg = df.loc[df['Last Name']==last_name].groupby(['First Name','Last Name']).agg({'First Name':list}).rename(columns={'First Name':'Name'}).reset_index()
        first_name_list = lastnameagg['Name']

        potentialDupes = []

        for i in lastnameagg['First Name'].str.lower():
            dupe_names = []
            for j in first_name_list:
                for k in j:
                    lettercount = 0
                    for l in range(len(k)):
                        if len(k)-l>=3:
                            if k[l:l+2].lower() in i:
                                lettercount += 1
                    if lettercount >= 3:
                        dupe_names.append(k)  
            potentialDupes.append(dupe_names)

        lastnameagg['Potential Dupes'] = potentialDupes
        dupeDf = pd.concat([dupeDf,lastnameagg])
        clear_output()
        iteration += 1
    
    dupeDf['Num Potential'] = [len(i) for i in dupeDf['Potential Dupes']]
    dupeDf = dupeDf.loc[dupeDf['Num Potential']>1].drop_duplicates(subset=['Potential Dupes']).drop(columns=['Num Potential','Name'])
    return dupeDf


def retentionRate(df,yearCol,contactIdCol):
    '''Calculates 1- and 2-year Donor Retention Rates'''
    donors = df.groupby(yearCol).agg({contactIdCol:set}).reset_index()

    newDonors = []
    for i,c in zip(donors.index,donors[contactIdCol]):
        if donors.loc[i,yearCol]!=min(donors[yearCol]):
            prevYr = donors.iloc[i-1,1]
            newDonors.append(list(filter(lambda v: v not in prevYr, c)))
        else:
            newDonors.append([])
    donors['New Donors'] = newDonors

    retained_1 = []
    for i,c in zip(donors.index,donors['New Donors']):
        if donors.loc[i,yearCol]!=max(donors[yearCol]):
            nextYr = donors.iloc[i+1,1]
            retained_1.append(list(filter(lambda v: v in nextYr, c)))
        else:
            retained_1.append([])
    donors['Retained_1'] = retained_1

    retained_2 = []
    for i,c in zip(donors.index,donors['Retained_1']):
        if donors.loc[i,yearCol] < max(donors[yearCol])-1:
            nextYr = donors.iloc[i+2,1]
            retained_2.append(list(filter(lambda v: v in nextYr, c)))
        else:
            retained_2.append([])
    donors['Retained_2'] = retained_2

    donors['Total Donors'] = [len(i) for i in donors[contactIdCol]]
    donors['Total New Donors'] = [len(i) for i in donors['New Donors']]
    donors['Percent New'] = donors['Total New Donors'] / donors['Total Donors']
    donors['Donors Retained_1'] = [len(i) for i in donors['Retained_1']]
    donors['Donors Retained_2'] = [len(i) for i in donors['Retained_2']]
    donors['1-year Overall Donor Retention Rate'] = donors['Donors Retained_1']/donors['Total Donors']
    donors['1-year New Donor Retention Rate'] = donors['Donors Retained_1']/donors['Total New Donors']
    donors['2-year New Donor Retention Rate'] = donors['Donors Retained_2']/donors['Total New Donors']
    
    return donors