# -*- coding: utf-8 -*-
"""
Title: makeJson.py

Description: This program creates JSON files of each state legislative district
and which party it is represented by so that it can be joined to the map of
state legislative districts and used for force layouts.  It creates IDs for 
each district matching those found in the shapefiles and recodes any 
multi-legislator districts represented by legislators of different parties 
as party="Multi".
    
Inputs:
    state_fips_codes.csv
    state_upper_houses.csv 
    state_lower_houses.csv
    
Outputs:
    state_upper_houses.json, state_upper_houses2.json
    state_lower_houses.json, state_lower_houses2.json
    
Created on Fri Jul 28 19:29:38 2017

@author: Alice
"""

import pandas as pd
import json


fips = pd.read_csv('state_fips_codes.csv')
sldu = pd.read_csv('state_upper_houses.csv')
sldl = pd.read_csv('state_lower_houses.csv')


# create a new index for each state to be used to determine the center of the
# force layout for each state
fips['state_index'] = fips.index.astype('str')


# build an id to match the geojson district IDs
# merge fips code onto each dataframe, then concatenate with the district ID
sldu = sldu.merge(fips, left_on='state', right_on='name')
sldu['ID'] = sldu.fips_code.apply(str).str.zfill(2) + sldu.district.apply(str).str.zfill(3)

sldl = sldl.merge(fips, left_on='state', right_on='name')
sldl['ID'] = sldl.fips_code.apply(str).str.zfill(2) + sldl.district.apply(str).str.zfill(3)



# handle multi-legislator districts
    
# drop duplicates for multi-legislator districts where all of the legislators are
# of the same party
sldu.drop_duplicates(['state', 'district', 'party', 'ID'], inplace=True)
sldl.drop_duplicates(['state', 'district', 'party', 'ID'], inplace=True)

# identify multi-legislator districts represented by different parties
sldu_count = pd.DataFrame({'count': sldu.groupby(by=['state', 'district']).size()}).reset_index()
sldu_multi_party = sldu_count[sldu_count['count']>1]

sldl_count = pd.DataFrame({'count': sldl.groupby(by=['state', 'district']).size()}).reset_index()
sldl_multi_party = sldl_count[sldl_count['count']>1]

# change the 'party' value for multi-party districts to be "Multi"
sldu = sldu.merge(sldu_multi_party, how='left')
sldu.loc[sldu['count'].notnull(), 'party'] = 'Multi'
sldu.drop_duplicates(['state', 'district', 'party', 'ID'], inplace=True)

sldl = sldl.merge(sldl_multi_party, how='left')
sldl.loc[sldl['count'].notnull(), 'party'] = 'Multi'
sldl.drop_duplicates(['state', 'district', 'party', 'ID'], inplace=True)


# recode parties
sldu['party2'] = sldu['party']
sldu.loc[sldu['party']=='D/IDC', 'party2'] = 'D'
sldu.loc[sldu['party']=='Libertarian', 'party2'] = 'Third'

sldl['party2'] = sldl['party']
sldl.loc[sldl['party']=='Independent', 'party2'] = 'I'
sldl.loc[sldl['party']=='Libertarian', 'party2'] = 'Third'
sldl.loc[sldl['party']=='Progressive', 'party2'] = 'Third'
sldl.loc[sldl['party']=='Common Sense Independent', 'party2'] = 'Third'
sldl.loc[sldl['party']=='Independence', 'party2'] = 'Third'

# add a sequence number for each district within each state to help with labeling
# the force layouts
sldu['sequence'] = sldu.groupby('state').cumcount().astype('str')
sldl['sequence'] = sldl.groupby('state').cumcount().astype('str')



# create JSON objects for the maps
upper_result = []
for i in sldu.index:
    d = {'id': sldu['ID'][i], 'party': sldu['party2'][i]}
    upper_result.append(d)
    
lower_result = []
for i in sldl.index:
    d = {'id': sldl['ID'][i], 'party': sldl['party2'][i]}
    lower_result.append(d)
    
# convert to JSON and output final files
with open('state_upper_houses.json', 'w') as f:
    json.dump(upper_result, f)

with open('state_lower_houses.json', 'w') as f:
    json.dump(lower_result, f)



# create JSON objects for the force layout 
upper_result2 = []
for i in sldu.index:
    d = {'state': sldu['state'][i], 'state_index': sldu['state_index'][i],
         'id': sldu['ID'][i], 'party': sldu['party2'][i], 'sequence': sldu['sequence'][i]}
    upper_result2.append(d)
    
lower_result2 = []
for i in sldl.index:
    d = {'state': sldl['state'][i], 'state_index': sldl['state_index'][i],
         'id': sldl['ID'][i], 'party': sldl['party2'][i], 'sequence': sldl['sequence'][i]}
    lower_result2.append(d)

# add on DC and Nebraska to the lower houses JSON so the state name still renders 
# in the force layout
dc = {'state': 'District of Columbia', 'state_index': '8', 'id': '', 'party': '', 'sequence': '0'}
nebraska = {'state': 'Nebraska', 'state_index': '27', 'id': '', 'party': '', 'sequence': '0'}
lower_result2.append(dc)
lower_result2.append(nebraska)
 
# convert to JSON and output final files
with open('state_upper_houses2.json', 'w') as f:
    json.dump(upper_result2, f)

with open('state_lower_houses2.json', 'w') as f:
    json.dump(lower_result2, f)