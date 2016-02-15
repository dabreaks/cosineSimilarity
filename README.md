# cosineSimilarity

---------------------

short project on building a similarity matrix of artists and songs based on the Last.fm API tags for users and songs

---------------------

### CONTENTS OF THIS FILE

* Introduction
* Package versions
* Installation
* Configuration

---------------------

### INTRODUCTION

The Last.fm python script utilizes the Last.fm API to obtain Artist and ArtistTag data. It then reshapes the data into a matrix of size m by n, where m is the number of Artists and n is the number of tags. Each field contains the normalized (normalized by Last.fm) tag count for each i Artist and j ArtistTag. The data are stored as a pandas data frame and exported to csv.
The Last.fm.cosine python script loads the previous csv file and constructs a cosine similarity matrix for ArtistTags based on each ArtistTag vector of tag counts. The data are stored as a pandas data frame and exported to csv.

---------------------

### PACKAGE VERSIONS

These scripts run on Python 2.7.9+ and utilize the following package versions:
 
* requests==2.2.1
* pandas==0.13.1
* numpy==1.8.0

---------------

### CONFIGURATION
 
Configure the following declared variables in the following python scripts:
 
**Last.fm.py**

  * change working directory: The working directory should be set to the directory of the contents      
  * set API parameters: A valid Last.fm API_KEY needs to be included in order for the API to execute. 
