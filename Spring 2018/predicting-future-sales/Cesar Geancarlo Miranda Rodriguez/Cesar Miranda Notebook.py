
# coding: utf-8

# # Predict Future Sales

# As was stated in the proposal document, there are 4 data sets that contain the data of the sales, the list of products, the product categories and the list of stores. Furthermore, the execution of this projects was done by using the proposed methodology mentioned in the proposal document which has three steps: analyze and generate the features for each dataset, consolidate the daily information to monthly and analyze the algorithms and choose the best one. 

# In[ ]:

get_ipython().magic(u'pylab inline')


# In[10]:

#Importing the necessary libraries
import dataiku
import pandas as pd, numpy as np
from sklearn import *
from dataiku import pandasutils as pdu


# # A) Analyze and generate the features for each dataset

# In this step, I firstly analyzed the datasets shops, items and item categories and I observed that there was one common characteristic. This characteristic was that all of these datasets were basically lists of objects (store, product and category) and I believed that I needed to learn from the description of each line, so I generated more features based on the text column to get some insights. 

# For example, in the item category dataset, at the beginning I only had 2 columns which indicate the name and the ID, as it is seen in the table below.

# In[12]:

#loading the dataset
item_categories = dataiku.Dataset("item_categories")
item_categories_df = item_categories.get_dataframe()
item_categories_df.head()


# After analyzing this dataset, I added some other features such as the length of the category name, the number of words that the category name has, and some tfid columns that will help the computer to know the importance of a word among all the category names and through this way the computer learns something from them. 

# In[13]:

feature_cnt = 25 #define the maximum number of features I want to generate


# In[14]:

#Text Features for the item_categories dataset
tfidf = feature_extraction.text.TfidfVectorizer(max_features=feature_cnt)
item_categories_df['item_category_name_len'] = item_categories_df['item_category_name'].map(len)  #Lenth of Item Category Description
item_categories_df['item_category_name_wc'] = item_categories_df['item_category_name'].map(lambda x: len(str(x).split(' '))) #Item Category Description Word Count
txtFeatures = pd.DataFrame(tfidf.fit_transform(item_categories_df['item_category_name']).toarray())
cols = txtFeatures.columns
for i in range(feature_cnt):
    item_categories_df['item_category_name_tfidf_' + str(i)] = txtFeatures[cols[i]]
item_categories_df.head()


# The same principle was applied to the shops dataset and items dataset.

# In[15]:

#loading the dataset
items = dataiku.Dataset("items")
items_df = items.get_dataframe()

#Text Features for the items dataset
tfidf = feature_extraction.text.TfidfVectorizer(max_features=feature_cnt)
items_df['item_name_len'] = items_df['item_name'].map(len) #Lenth of Item Description
items_df['item_name_wc'] = items_df['item_name'].map(lambda x: len(str(x).split(' '))) #Item Description Word Count
txtFeatures = pd.DataFrame(tfidf.fit_transform(items_df['item_name']).toarray())
cols = txtFeatures.columns
for i in range(feature_cnt):
    items_df['item_name_tfidf_' + str(i)] = txtFeatures[cols[i]]
items_df.head()


# Generating the text features for the shop dataset

# In[16]:

#loading the dataset
shops = dataiku.Dataset("shops")
shops_df = shops.get_dataframe()

#Text Features for the shop dataset
tfidf = feature_extraction.text.TfidfVectorizer(max_features=feature_cnt)
shops_df['shop_name_len'] = shops_df['shop_name'].map(len)  #Lenth of Shop Name
shops_df['shop_name_wc'] = shops_df['shop_name'].map(lambda x: len(str(x).split(' '))) #Shop Name Word Count
txtFeatures = pd.DataFrame(tfidf.fit_transform(shops_df['shop_name']).toarray())
cols = txtFeatures.columns

for i in range(feature_cnt):
    shops_df['shop_name_tfidf_' + str(i)] = txtFeatures[cols[i]]
shops_df.head()


# Until this part, I have generated all the features for the shops, items and item_categories datasets and producing new datasets as it is shown in the following image.

# In[9]:

from IPython.display import Image
PATH = "/home/cemirandaro/Pictures/"
Image(filename = PATH + "items_itemscategories_shops_generated.jpg", width=600, height=200)


# Second, I observe that in the sales dataset I can extract the month and year from the date and eliminate the item price because for the purpose of this project, this column is not relevant.  

# In[20]:

train = dataiku.Dataset("sales_train_v2")
train_df = train.get_dataframe()

train_df.head()


# In[21]:

#Extracting the month and year and eliminating the item_price
#Generating the sales_train_data dataset that contains the train data I am going to use.

train_df['date'] = pd.to_datetime(train_df['date'], format='%d.%m.%Y')
train_df['month'] = train_df['date'].dt.month
train_df['year'] = train_df['date'].dt.year
train_df = train_df.drop(['date','item_price'], axis=1)

sales_train_data = dataiku.Dataset("sales_train_data")
sales_train_data.write_with_schema(train_df)

train_df.head()


# In[8]:

Image(filename = PATH + "sales_train_data_generated.jpg", width=400, height=183)


# # B) Consolidate the daily information to monthly

# Because of the prediction had to be on monthly basis and all the sales information was on daily basis, I needed to group the sales per product, store and month to obtain the total number of items per product and store. After that, I needed to get the mean of the sales and the number of items sold the previous month. 

# In[24]:

sales_train_data = dataiku.Dataset("sales_train_data")
sales_train_data_df = sales_train_data.get_dataframe()

#grouping the data per month
sales_train_data_df = sales_train_data_df.groupby([c for c in sales_train_data_df.columns if c not in ['item_cnt_day']], as_index=False)[['item_cnt_day']].sum()
sales_train_data_df = sales_train_data_df.rename(columns={'item_cnt_day':'item_cnt_month'})

#Monthly Avg
shop_item_monthly_mean = sales_train_data_df[['shop_id','item_id','item_cnt_month']].groupby(['shop_id','item_id'], as_index=False)[['item_cnt_month']].mean()
shop_item_monthly_mean = shop_item_monthly_mean.rename(columns={'item_cnt_month':'item_cnt_month_avg'})

#Add Mean Feature into the Train dataset 
sales_train_data_df = pd.merge(sales_train_data_df, shop_item_monthly_mean, how='left', on=['shop_id','item_id'])

#Get the Last Month data (Oct 2015) and then rename the column to prev_month
shop_item_prev_month = sales_train_data_df[sales_train_data_df['date_block_num'] == 33][['shop_id','item_id','item_cnt_month']]
shop_item_prev_month = shop_item_prev_month.rename(columns={'item_cnt_month':'item_cnt_prev_month'})

#Add Previous Month Feature into the Train dataset and fill the Null values with ZERO!
sales_train_data_df = pd.merge(sales_train_data_df, shop_item_prev_month, how='left', on=['shop_id','item_id']).fillna(0.)


#setting up the sales_train_data_grouped dataset 
sales_train_data_grouped = dataiku.Dataset("sales_train_data_grouped")
sales_train_data_grouped.write_with_schema(sales_train_data_df)

sales_train_data_df.head()


# I also generated from sales_train_data two other datasets containing the grouped quantity of sold items of the previous month (sales_shop_item_prev_month) and the other dataset the mean of the number of items sold per product and store (sales_shop_item_monthly). These datasets will help me in the next step to make the test dataset in the same structure than the train dataset. 

# In[25]:

#setting up the sales_shop_item_monthly_avg dataset 
sales_shop_item_monthly_avg = dataiku.Dataset("sales_shop_item_monthly_avg")
sales_shop_item_monthly_avg.write_with_schema(shop_item_monthly_mean)

#setting up the sales_shop_item_prev_month dataset 
sales_shop_item_prev_month = dataiku.Dataset("sales_shop_item_prev_month")
sales_shop_item_prev_month.write_with_schema(shop_item_prev_month)


# In[26]:

shop_item_monthly_mean.head()


# In[27]:

shop_item_prev_month.head()


# Until now, I have done this part of the flow. 

# In[28]:

Image(filename = PATH + "datasets_generated_from_monthlysales.jpg")


# # C) Analyze the algorithms and choose the best one 

# After having generated the new shops, item categories and items datasets with all the new features, I had to join them with the dataset called “sales_train_data_grouped” and start generating the possible models. This new dataset is called “sales_data_prepared”.
# 

# In[29]:

#Items features
sales_train_data_df = pd.merge(sales_train_data_df, items_df, how='left', on='item_id')
#Item Category features
sales_train_data_df = pd.merge(sales_train_data_df, item_categories_df, how='left', on='item_category_id')
#Shops features
sales_train_data_df = pd.merge(sales_train_data_df, shops_df, how='left', on='shop_id')

#setting up the prepared train dataset
sales_data_prepared = dataiku.Dataset("sales_data_prepared")
sales_data_prepared.write_with_schema(sales_train_data_df)
sales_train_data_df.head()


# Making the test dataset to the same format than the final train dataset

# In[10]:

test = dataiku.Dataset("test")
test_df = test.get_dataframe()

test_df['month'] = 11
test_df['year'] = 2015
test_df['date_block_num'] = 34
#Add Mean Feature
test_df = pd.merge(test_df, shop_item_monthly_mean, how='left', on=['shop_id','item_id']).fillna(0.)
#Add Previous Month Feature
test_df = pd.merge(test_df, shop_item_prev_month, how='left', on=['shop_id','item_id']).fillna(0.)
#Items features
test_df = pd.merge(test_df, items_df, how='left', on='item_id')
#Item Category features
test_df = pd.merge(test_df, item_categories_df, how='left', on='item_category_id')
#Shops features
test_df = pd.merge(test_df, shops_df, how='left', on='shop_id')
test_df['item_cnt_month'] = 0.


test_prepared = dataiku.Dataset("test_prepared")
test_prepared.write_with_schema(test_df)
test_df.head()


# Until now, I have generated the final train dataset (sales_data_prepared) and the final test dataset (test_prepared) having both the same format. 

# In[30]:

Image(filename = PATH + "final_train_and_test_datasets.jpg")


# After creating a new analysis and selected the possible algorithms to use, the DSS showed me that the most suitable algorithm is the Random Forest so this is the one with which I built the model. 

# In[31]:

Image(filename = PATH + "used_algorithms.jpg")


# I also tried to apply some ensemble algorithms, but the result was lower than the Random Forest.

# In[32]:

Image(filename = PATH + "ensemble_algorithm_result.jpg")


# Therefore, I can proceed to generate the model as it is shown in the following image.

# In[33]:

Image(filename = PATH + "model_generated.jpg")


# The final workflow is the one that is shown in the following image.

# In[34]:

Image(filename = PATH + "final_workflow.jpg")


# # Ethical Implications

# The unique ethical implication I could find for this project is that I, as a consultant, do not have to show or share the data of the company to any other person who does not belong to the project because of the several consequences it could bring to the customer company. For example, this data can be useful for other competitors to have the knowledge of how well or bad 1C company is going and therefore, take decisions to affect it. 

# # Future Considerations

# <strong>1. Use of external data </strong><br>
# Get the average weather conditions for each month of this dataset, the season of each month and if any special event that happened in inside a month to have a more realistic result.
# <br><br>
# <strong>2. Improve the model to make it for the whole year </strong><br>
# Currently, the model proposed can only predict one month (Nov 2015) so the improvement needed would be to modify the model in order to make it for not only a specific month. 
# 

# In[ ]:



