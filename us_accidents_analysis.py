# -*- coding: utf-8 -*-
"""US Accidents Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FR1Qk_3MP6BqSNTP2wv8Tn3VHt_x0zqq

## About Dataset

This is a countrywide car accident dataset, which covers 49 states of the USA. The accident data are collected from February 2016 to Dec 2021, using multiple APIs that provide streaming traffic incident (or event) data. These APIs broadcast traffic data captured by a variety of entities, such as the US and state departments of transportation, law enforcement agencies, traffic cameras, and traffic sensors within the road-networks. Currently, there are about 2.8 million accident records in this dataset.

## Inspiration

US-Accidents can be used for numerous applications such as real-time car accident prediction, studying car accidents hotspot locations, casualty analysis and extracting cause and effect rules to predict car accidents, and studying the impact of precipitation or other environmental stimuli on accident occurrence. The most recent release of the dataset can also be useful to study the impact of COVID-19 on traffic behavior and accidents.

## Our Purpose

The first objective of this project is to recognize key factors affecting the accident severity(i.e. **an indication of the effect the accident has on traffic**). The second one is to develop a model that can accurately predict accident severity. To be specific, for a given accident, without any detailed information about itself, like driver attributes or vehicle type, this model is supposed to be able to predict the likelihood of this accident being a severe one. The accident could be the one that just happened and still lack of detailed information, or a potential one predicted by other models. Therefore, with the sophisticated real-time traffic accident prediction solution developed by the creators of the same dataset used in this project, this model might be able to further predict severe accidents in real-time.

## Overview of dataset


#### Traffic Attributes (10):

* ID: This is a unique identifier of the accident record.

* Severity: Shows the severity of the accident, a number between 1 and 4, where 1 indicates the least impact on traffic (i.e., short delay as a result of the accident) and 4 indicates a significant impact on traffic (i.e., long delay).

* Start_Time: Shows start time of the accident in local time zone.

* End_Time: Shows end time of the accident in local time zone.

* Start_Lat: Shows latitude in GPS coordinate of the start point.

* Start_Lng: Shows longitude in GPS coordinate of the start point.

* End_Lat: Shows latitude in GPS coordinate of the end point.

* End_Lng: Shows longitude in GPS coordinate of the end point.

* Distance(mi): The length of the road extent affected by the accident.

* Description: Shows natural language description of the accident.

#### Address Attributes (9):

* Number: Shows the street number in address field.

* Street: Shows the street name in address field.

* Side: Shows the relative side of the street (Right/Left) in address field.

* City: Shows the city in address field.

* County: Shows the county in address field.

* State: Shows the state in address field.

* Zipcode: Shows the zipcode in address field.

* Country: Shows the country in address field.

* Timezone: Shows timezone based on the location of the accident (eastern, central, etc.).

#### Weather Attributes (11):

* Airport_Code: Denotes an airport-based weather station which is the closest one to location of the accident.

* Weather_Timestamp: Shows the time-stamp of weather observation record (in local time).

* Temperature(F): Shows the temperature (in Fahrenheit).

* Wind_Chill(F): Shows the wind chill (in Fahrenheit).

* Humidity(%): Shows the humidity (in percentage).

* Pressure(in): Shows the air pressure (in inches).

* Visibility(mi): Shows visibility (in miles).

* Wind_Direction: Shows wind direction.

* Wind_Speed(mph): Shows wind speed (in miles per hour).

* Precipitation(in): Shows precipitation amount in inches, if there is any.

* Weather_Condition: Shows the weather condition (rain, snow, thunderstorm, fog, etc.).

#### POI Attributes (13):

* Amenity: A Point-Of-Interest (POI) annotation which indicates presence of amenity in a nearby location.

* Bump: A POI annotation which indicates presence of speed bump or hump in a nearby location.

* Crossing: A POI annotation which indicates presence of crossing in a nearby location.

* Give_Way: A POI annotation which indicates presence of give_way sign in a nearby location.

* Junction: A POI annotation which indicates presence of junction in a nearby location.

* No_Exit: A POI annotation which indicates presence of no_exit sign in a nearby location.

* Railway: A POI annotation which indicates presence of railway in a nearby location.

* Roundabout: A POI annotation which indicates presence of roundabout in a nearby location.

* Station: A POI annotation which indicates presence of station (bus, train, etc.) in a nearby location.

* Stop: A POI annotation which indicates presence of stop sign in a nearby location.

* Traffic_Calming: A POI annotation which indicates presence of traffic_calming means in a nearby location.

* Traffic_Signal: A POI annotation which indicates presence of traffic_signal in a nearby location.

* Turning_Loop: A POI annotation which indicates presence of turning_loop in a nearby location.

#### Period-of-Day (4):

* Sunrise_Sunset: Shows the period of day (i.e. day or night) based on sunrise/sunset.

* Civil_Twilight: Shows the period of day (i.e. day or night) based on civil twilight.

* Nautical_Twilight: Shows the period of day (i.e. day or night) based on nautical twilight.

* Astronomical_Twilight: Shows the period of day (i.e. day or night) based on astronomical twilight.
"""

import numpy as np
import pandas as pd
import json
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
from datetime import datetime
import glob
import seaborn as sns
import re
import os
import io
from scipy.stats import boxcox

"""# 1. Overview & Preprocessing"""

df = pd.read_csv('US_Accidents_Dec21_updated.csv')

df.head()

df.shape

df.info()

df.describe()

"""### Insights

* This tells that majority of accidents have severity ~2 means not much higher impact on traffic.
* In approx 75% cases no precipitation was recorded so this could mean rain is not the reason for accidents.
* on an avg accidents happen even while the visibility is ~9 miles so this could mean that visibility is not a reason.
* average length of the road extent affected by the accident is 7 miles

**Fixing time stamps as they are in object type**
"""

df['Start_Time'] = pd.to_datetime(df['Start_Time'])
df['End_Time'] = pd.to_datetime(df['End_Time'])
df['Weather_Timestamp'] = pd.to_datetime(df['Weather_Timestamp'])

"""**Features 'ID' doesn't provide any useful information about accidents themselves. 'Distance(mi)', 'End_Time' (we have start time), 'End_Lat', and 'End_Lng'(we have start location) can be collected only after the accident has already happened and hence cannot be predictors for serious accident prediction. For 'Description', the POI features have already been extracted from it by dataset creators. Let's get rid of these features first.**"""

df = df.drop(['ID','Description','Distance(mi)', 'End_Time', 'End_Lat', 'End_Lng'], axis=1)

df.shape

cat_names = ['Side', 'Country', 'Timezone', 'Amenity', 'Bump', 'Crossing',
             'Give_Way', 'Junction', 'No_Exit', 'Railway', 'Roundabout', 'Station',
             'Stop', 'Traffic_Calming', 'Traffic_Signal', 'Turning_Loop', 'Sunrise_Sunset',
             'Civil_Twilight', 'Nautical_Twilight', 'Astronomical_Twilight']
print("Unique count of categorical features:")
for i in cat_names:
    print(i,df[i].unique().size)

"""**'Country' and 'Turning_Loop' for they have only one class. So, we have to drop them otherwise we will get error at the time of splitting the dataset...**"""

df = df.drop(['Country','Turning_Loop'], axis=1)

df.Wind_Direction.unique()

df.Weather_Condition.unique()

"""**we will find some chaos in 'Wind_Direction' and 'Weather_Condition'. It is necessary to clean them up first.**"""

df.loc[df['Wind_Direction']=='Calm','Wind_Direction'] = 'CALM'
df.loc[(df['Wind_Direction']=='West')|(df['Wind_Direction']=='WSW')|(df['Wind_Direction']=='WNW'),'Wind_Direction'] = 'W'
df.loc[(df['Wind_Direction']=='South')|(df['Wind_Direction']=='SSW')|(df['Wind_Direction']=='SSE'),'Wind_Direction'] = 'S'
df.loc[(df['Wind_Direction']=='North')|(df['Wind_Direction']=='NNW')|(df['Wind_Direction']=='NNE'),'Wind_Direction'] = 'N'
df.loc[(df['Wind_Direction']=='East')|(df['Wind_Direction']=='ESE')|(df['Wind_Direction']=='ENE'),'Wind_Direction'] = 'E'
df.loc[df['Wind_Direction']=='Variable','Wind_Direction'] = 'VAR'
print("Wind Direction after simplification: ", df['Wind_Direction'].unique())

"""**According to Road Weather Management Program, most weather-related crashes happen on wet-pavement and during rainfall. Winter-condition and fog are another two main reasons for weather-related accidents. To extract these three weather conditions, we first look at what we have in 'Weather_Condition' Feature.**"""

# show distinctive weather conditions
weather ='!'.join(df['Weather_Condition'].dropna().unique().tolist())
weather = np.unique(np.array(re.split(
    "!|\s/\s|\sand\s|\swith\s|Partly\s|Mostly\s|Blowing\s|Freezing\s", weather))).tolist()
print("Weather Conditions: ", weather)

df['Clear'] = np.where(df['Weather_Condition'].str.contains('Clear', case=False, na = False), 1, 0)
df['Cloud'] = np.where(df['Weather_Condition'].str.contains('Cloud|Overcast', case=False, na = False), 1, 0)
df['Rain'] = np.where(df['Weather_Condition'].str.contains('Rain|storm', case=False, na = False), 1, 0)
df['Heavy_Rain'] = np.where(df['Weather_Condition'].str.contains('Heavy Rain|Rain Shower|Heavy T-Storm|Heavy Thunderstorms', case=False, na = False), 1, 0)
df['Snow'] = np.where(df['Weather_Condition'].str.contains('Snow|Sleet|Ice', case=False, na = False),1, 0)
df['Heavy_Snow'] = np.where(df['Weather_Condition'].str.contains('Heavy Snow|Heavy Sleet|Heavy Ice Pellets|Snow Showers|Squalls', case=False, na = False), 1, 0)
df['Fog'] = np.where(df['Weather_Condition'].str.contains('Fog', case=False, na = False), 1, 0)

df.columns

# Assign NA to created weather features where 'Weather_Condition' is null.
weather = ['Clear','Cloud','Rain','Heavy_Rain','Snow','Heavy_Snow','Fog']
for i in weather:
    df.loc[df['Weather_Condition'].isnull(),i] = df.loc[df['Weather_Condition'].isnull(),'Weather_Condition']

df.loc[:,['Weather_Condition'] + weather]

df = df.drop(['Weather_Condition'], axis=1)

df.columns

"""**The 'Weather_Timestamp' is almost as same as 'Start_Time', we can just keep 'Start_Time'. Then map 'Start_Time' to 'Year', 'Month', 'Weekday', 'Day' (in a year), 'Hour', and 'Minute' (in a day).**"""

(df.Weather_Timestamp-df.Start_Time).mean()

df = df.drop(["Weather_Timestamp"], axis=1)

df['Year'] = df['Start_Time'].dt.year
df['Month'] = df['Start_Time'].dt.month
df['Weekday']= df['Start_Time'].dt.weekday

days_each_month = np.cumsum(np.array([0,31,28,31,30,31,30,31,31,30,31,30,31]))
print(days_each_month)
nday = [days_each_month[arg-1] for arg in df['Month'].values]
nday = nday + df["Start_Time"].dt.day.values
print(nday)

df['Day'] = nday
df['Hour'] = df['Start_Time'].dt.hour
df['Minute']=df['Hour']*60.0+df["Start_Time"].dt.minute

df.loc[:4,['Start_Time', 'Year', 'Month', 'Weekday', 'Day', 'Hour', 'Minute']]

"""# 2. Handling missing data & duplicates"""

df

missing = pd.DataFrame(df.isnull().sum()).reset_index()
missing.columns = ['Feature', 'Missing_Percent(%)']
missing['Missing_Percent(%)'] = missing['Missing_Percent(%)'].apply(lambda x: x / df.shape[0] * 100)
missing.sort_values(by='Missing_Percent(%)',ascending=False )

"""**Dropping Number as it contains very much Nan values...**"""

df = df.drop(['Number'], axis=1)

df.shape

"""**Dropping Nan rows from the following columns as they have very less missing value percentage**

**Dropping those whose missing value percentage less or equal to 5%**
"""

print(missing[(missing['Missing_Percent(%)']>0) & (missing['Missing_Percent(%)']<6)]['Feature'].to_list())

df = df.dropna(subset=['Street', 'City', 'Zipcode', 'Timezone', 'Airport_Code', 'Temperature(F)',
                       'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Direction',
                       'Wind_Speed(mph)', 'Sunrise_Sunset', 'Civil_Twilight', 'Nautical_Twilight',
                       'Astronomical_Twilight', 'Clear', 'Cloud', 'Rain', 'Heavy_Rain', 'Snow',
                       'Heavy_Snow', 'Fog'])

df.isna().sum()

"""**Now we remained with 'Precipitation(in)' & 'Wind_Chill(F)' which contains high missing values and both are continuous so we can replace them by mean/median based on their distribution**"""

df['Precipitation(in)'].plot()

df['Wind_Chill(F)'].plot()

"""**Both are not normally distributed so we can replace their missing values by median...**"""

df['Precipitation(in)'] = df['Precipitation(in)'].fillna(df['Precipitation(in)'].median())
df['Wind_Chill(F)'] = df['Wind_Chill(F)'].fillna(df['Wind_Chill(F)'].median())

df.isna().sum()

"""**CHECKING DUPLICATES & DROPPING IT...**"""

df.duplicated().sum()

df.drop_duplicates(keep='first', inplace=True)
df.reset_index(drop=True, inplace=True)

df.shape

# df.to_csv('US_accidents_24lac.csv',index=False)

"""# 3. Exploratory Data Analysis

**First we'll check our target column i.e. Severity**
"""

df.Severity.value_counts()

"""## 3.1 Balancing the target

**We Know that the accidents with severity level 4 are much more serious than accidents of other levels. Therefore, I decided to focus on level 4 accidents and regroup the levels of severity into level 4 versus other levels.**
"""

df['Severity4'] = 0
df.loc[df['Severity'] == 4, 'Severity4'] = 1
df = df.drop(['Severity'], axis = 1)
df.Severity4.value_counts()

"""* 0 ---> Accidents are of normal condition
* 1 ---> Accidents are very serious in condition
"""

df1 = df[df['Severity4']==0][:110000]
df2 = df[df['Severity4']==1][:110000]
df_bl = pd.concat([df1,df2])

df_bl.shape

df_bl.Severity4.value_counts()

"""## 3.2 Time Features

### Year
"""

df_bl.Year = df_bl.Year.astype(str)
sns.countplot(x='Year', hue='Severity4', data=df_bl ,palette="Set2", order=sorted(df_bl.Year.unique()))
plt.title('Count of Accidents by Year', size=15, y=1.05)
plt.show()

"""**The number of other levels accident is totally decreased after 2017 but severity level 4 accidents are quite constant**

### Month
"""

plt.figure(figsize=(10,5))
sns.countplot(x='Month', hue='Severity4', data=df_bl ,palette="Set2")
plt.title('Count of Accidents by Month', size=15, y=1.05)
plt.show()

"""**You can see that other level accidents are quite constant from July to Feb but number of level 4 accidents rapidly increases from July to December and are constant in between January to May**

### Weekday
"""

plt.figure(figsize=(10,5))
sns.countplot(x='Weekday', hue='Severity4', data=df_bl ,palette="Set2")
plt.title('Count of Accidents by Weekday', size=15, y=1.05)
plt.show()

"""**The number of accidents was much less on weekends while the proportion of level 4 accidents was higher.**

### Period-of-Day
"""

period_features = ['Sunrise_Sunset','Civil_Twilight','Nautical_Twilight','Astronomical_Twilight']
fig, axs = plt.subplots(ncols=1, nrows=4, figsize=(13, 5))
plt.subplots_adjust(wspace = 0.5)
for i, feature in enumerate(period_features, 1):
    plt.subplot(1, 4, i)
    sns.countplot(x=feature, hue='Severity4', data=df_bl ,palette="Set2")

    plt.xlabel('{}'.format(feature), size=12, labelpad=3)
    plt.ylabel('Accident Count', size=12, labelpad=3)
    plt.tick_params(axis='x', labelsize=12)
    plt.tick_params(axis='y', labelsize=12)

    plt.legend(['0', '1'], loc='upper right', prop={'size': 10})
    plt.title('Count of Severity in\n{} Feature'.format(feature), size=13, y=1.05)
fig.suptitle('Count of Accidents by Period-of-Day',y=1.08, fontsize=16)
plt.show()

"""**Its very obvious that Accidents happen less at night but level4 accidents are higher, It means most of the serious accidents happens at night time**

### Hour
"""

plt.figure(figsize=(15,5))
sns.countplot(x='Hour', hue='Severity4', data=df_bl ,palette="Set2")
plt.title('Count of Accidents by Hour', size=15, y=1.05)
plt.show()

"""**Most accidents happened during the daytime, especially AM peak and PM peak. When it comes to night, accidents were far less but more likely to be serious.**

## 3.3 Address Features

### Timezone
"""

plt.figure(figsize=(6,5))
chart = sns.countplot(x='Timezone', hue='Severity4', data=df_bl ,palette="Set2")
plt.title("Count of Accidents by Timezone", size=15, y=1.05)
plt.show()

"""**Eastern timezone is most dangerous one...**

### State
"""

plt.figure(figsize=(25,5))
chart = sns.countplot(x='State', hue='Severity4',
                      data=df_bl ,palette="Set2", order=df_bl['State'].value_counts().index)
plt.title("Count of Accidents in State ordered by accidents count", size=15, y=1.05)
plt.show()

"""**FL, CA, and TX are the top 3 states with the most accidents.**

### Side
"""

plt.figure(figsize=(5,5))
chart = sns.countplot(x='Side', hue='Severity4', data=df_bl ,palette="Set2")
plt.title("Count of Accidents by Side", size=15, y=1.05)
plt.show()

"""**Right side of the line is much more dangerous than left side.**"""

fre_list = ['Street', 'City', 'County', 'Zipcode', 'Airport_Code','State']
for i in fre_list:
    print(i,'--->',df[i].nunique())

"""**'Street', 'City', 'County', 'Zipcode', 'Airport_Code','State'**

**These above columns contains very much categories which makes our data complex when dummy columns are created
We can do some analysis also But for time being we consider to drop these columns...**
"""

df_bl = df_bl.drop(fre_list, axis  = 1)

"""## 3.4 Weather Features

### Weather conditions
"""

fig, axs = plt.subplots(ncols=2, nrows=4, figsize=(15, 10))
plt.subplots_adjust(hspace=0.4,wspace = 0.6)
for i, feature in enumerate(weather, 1):
    plt.subplot(2, 4, i)
    sns.countplot(x=feature, hue='Severity4', data=df_bl ,palette="Set2")

    plt.xlabel('{}'.format(feature), size=12, labelpad=3)
    plt.ylabel('Accident Count', size=12, labelpad=3)
    plt.tick_params(axis='x', labelsize=12)
    plt.tick_params(axis='y', labelsize=12)

    plt.legend(['0', '1'], loc='upper right', prop={'size': 10})
    plt.title('Count of Severity in \n {} Feature'.format(feature), size=14, y=1.05)
fig.suptitle('Count of Accidents by Weather Features (resampled data)', fontsize=18)
plt.show()

"""**As seen from above, accidents are little more likely to be serious during rain or snow while less likely on a cloudy day.**"""

df_bl = df_bl.drop(['Heavy_Rain','Heavy_Snow','Fog'], axis  = 1)

df_bl.shape

"""### Wind Directions"""

plt.figure(figsize=(10,5))
chart = sns.countplot(x='Wind_Direction', hue='Severity4', data=df_bl ,palette="Set2")
plt.title("Count of Accidents in Wind Direction", size=15, y=1.05)
plt.show()

"""**Both Class of severity is performing same in every category of Wind direction... So it cant give any inference**"""

df_bl = df_bl.drop(['Wind_Direction'], axis  = 1)

df_bl.shape

"""## 3.5 Point of Interest (POI) features"""

sns.boxplot(df['Pressure(in)'])







































































