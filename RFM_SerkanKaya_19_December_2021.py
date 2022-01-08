############################################################################################
#    CUSTOMER SEGMENTATION WITH RFM
#    Serkan KAYA , 19 December 2021
############################################################################################

# Business Problem:
#
# An e-commerce company wants to segment its customers and determine marketing strategies according to
# these segments. The company believes that marketing activities specific to customer segments that
# exhibit common behaviors will increase revenue.
#
# For example, it is desired to organize different campaigns for new customers and different campaigns to
# retain customers, which are very profitable for the company.
#
# Segment customers with the RFM method.
#
############################################################################################
#   History of Dataset
############################################################################################
# The dataset named Online Retail II includes the sales of an UK-based online store between
# 01/12/2009 - 09/12/2011. The product catalog of this company includes souvenirs, small items,
# and etc. The vast majority of the company's customers are corporate customers.
#
############################################################################################
#   Variables
############################################################################################
# InvoiceNo – Invoice Number, If this code starts with C, it indicates that the transaction has been cancelled.
# StockCode – Product code, unique number for each product.
# Description – Product name or derscription
# Quantity – Product quantity
# InvoiceDate –Invoice Date
# UnitPrice – Unit price (Currency: GBP)
# CustomerID – Customer ID number
# Country – Country name

###########################################################################################
#   PROJECT TASKS
############################################################################################
#                                       TASK 1
############################ LOADING THE DATASET ##########################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)


######################## 1) UNDERSTANDING AND PREPARATION THE DATASET #####################

##### 1.1) Read the dataset and make a copy of it #########################################

df_=pd.read_excel('/Users/mac/PycharmProjects/Veri_Okulu/Hafta 03/online_retail_II.xlsx',sheet_name='Year 2010-2011')
df=df_.copy()

#### 1.2) Examine the descriptive statistics of the dataset #########################################

df.shape  # There are 541910 observations and 8 variables
df.columns
df.info() # Quantity is integer, Price and Customer ID are floats, InvoiceDate is datetime and the rest are objects
df.describe().T  # There are some problems in 'Quantity' and 'Price' as they should not be negative
                 # There are some outliers

#### 1.3) Are there any null values? If so, in which variables #########################################
df.isnull().values.any()
df.isnull().sum() # There are 1454 null observations in 'Description' and 135080 in 'Customer ID'

#### 1.4) Are there any null values? If so, in which variables #########################################
df.dropna(inplace=True)

##### 1.5) How many unique products are there in the dataset? ##########################################
df['Description'].nunique()  # There are 3896 unique values

##### 1.5) How many unique products are there for each item? ##########################################
df['Description'].value_counts()

##### 1.6) Rank the most ordered products from most to least ##########################################
df.groupby('Description').agg({'Quantity':'sum'}).sort_values(by='Quantity',ascending=False)

##### 1.7) Remove the cancelled products from the dataset #############################################
df.shape # To check the number of observations before removing ,(406830,8)
df=df[~df['Invoice'].str.contains('C',na=False)] # Removed cancelled items, alt+n : tilde
df.shape # To check the number of observations after removing , (397925,8)

##### 1.8) Creat a total price variable in the dataset ###############################################
df['Total_Price']=df['Price']*df['Quantity']


############################################################################################
#                           TASK 2 - Calculation of the RFM Metrics
############################################################################################

##### 2.1) Definition of the RFM Metrics ##################################################

# RECENCY : Time elapsed from customer's last purchase to the current date

# FREQUENCY: Total number of purchases by the customer

# MONETARY (Money Value°: Total spends by the customer

##### 2.1, 2.2, 2.3 and 2.4 Calculation of the RFM Metrics ####################################################

df['InvoiceDate'].max()   # Max date in the dataframe: 2010/12/09 , 9 Dec 2010
today_date=dt.datetime(2011, 12, 11) # Let us assume that I make this analysis two days after the last date in the data

df.columns

# We define rfm dataframe which we will be dealing with this hereafter
rfm = df.groupby('Customer ID'). agg({'InvoiceDate':lambda InvoiceDate:(today_date-InvoiceDate.max()).days, # Recency
                       'Invoice':lambda Invoice:Invoice.nunique(),   # Frequency
                       'Total_Price':lambda Total_Price:Total_Price.sum()}) # Monetary

rfm.head()
rfm.columns=['recency','frequency','monetary']

rfm=rfm[rfm['monetary']>0]

#########################################################################################################
#                TASK 3 - Creation of the RFM Scores and transform into one variable
#########################################################################################################
rfm.head() # What we have so far

rfm['receny_score']=pd.qcut(rfm['recency'],5,labels=[5,4,3,2,1])

rfm['frequency_score']=pd.qcut(rfm['frequency'].rank(method='first'),5,labels=[1,2,3,4,5])

rfm['monetary_score']=pd.qcut(rfm['monetary'],5,labels=[1,2,3,4,5])

rfm['RFM_SCORE']=(rfm['receny_score'].astype(str)+rfm['frequency_score'].astype(str))
# converting string via astype

rfm.head()

#########################################################################################################
#      TASK 4 - Creation and analyses of RFM Segments (RFM Segments olusturulmasi ve analiz edilmesi
#########################################################################################################

# Creating RFM segments; RFM isimlendirmesi
# There are related to 'Regular expression subject'

seg_map = {
    r'[1-2][1-2]': 'hibernating', # r' : regular expression ifadesi..
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment']=rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()

#########################################################################################################
#      TASK 5 - Action Time :)
#########################################################################################################

# I have chosen three following segments : 1) cant_loose 2) new_customers 3) potential_loyalists
# Let's first have a look to these segments through the descriptive statistics analysis

rfm.groupby('segment')[['recency','frequency','monetary']].agg(['mean','count'])

# Comments on the segment 'cant_loose':
# There are 63 customer in this segment. They spent quite significant amount of money £2796.
# I need to save these clients so I can send some discounts to them keep them doing the shopping on our shop.

# Comments on the segment 'new_customers':
# There are 42 customer in this segment. They done shopping very recently 7 days ago.
# They spent £388. I can also send some offers via email to stick them to our shop.

#Comments on the segment 'potential_loyalists':
# There are 484 customer in this segment.There done shopping  recently 17 days ago.
# They spent £1041. My aim would be to switch them to loyal customers segment.
# I can send them an application form for the loyal customer club card.


##### 5.2) Export 'Loyal Customers' to an excel file ##################################################

new_df=pd.DataFrame()
new_df['Loyal Customers']=rfm[rfm['segment']=='loyal_customers'].index
new_df.head()
new_df.to_excel('Loyal_Customers.xlsx')