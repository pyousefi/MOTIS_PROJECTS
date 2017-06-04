# [Demonetization in India Twitter Data](https://www.kaggle.com/arathee2/demonetization-in-india-twitter-data)
## Data extracted from Twitter regarding the recent currency demonetization

### Context

The **demonetization of ₹500 and ₹1000** banknotes was a step taken by the **Government of India** on 8 November 2016, ceasing the usage of all ₹500 and ₹1000 banknotes of the Mahatma Gandhi Series as a form of legal tender in India from 9 November 2016.

The announcement was made by the Prime Minister of India **Narendra Modi** in an unscheduled live televised address to the nation at 20:15 Indian Standard Time (IST) the same day. In the announcement, Modi declared circulation of all ₹500 and ₹1000 banknotes of the Mahatma Gandhi Series as invalid and announced the issuance of new ₹500 and ₹2000 banknotes of the Mahatma Gandhi New Series in exchange for the old banknotes.

### Content

The data contains 6000 most recent tweets on #demonetization. There are 6000 rows(one for each tweet) and 14 columns.

### Metadata:

* Text (Tweets)
* favorited
* favoriteCount
* replyToSN
* created
* truncated
* replyToSID
* id
* replyToUID
* statusSource
* screenName
* retweetCount
* isRetweet
* retweeted

### Acknowledgement

The data was collected using the "twitteR" package in R using the twitter API.

### Past Research

I have performed my own analysis on the data. I only did a sentiment analysis and formed a word cloud.

[Click here to see the analysis on GitHub](https://github.com/arathee2/demonetization-india/blob/master/demonetization-sentiment-analysis.md)

### Inspiration

* What percentage of tweets are negative, positive or neutral ?
* What are the most famous/re-tweeted tweets ?