# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# Goal: Construct a data set that relates Last.fm tags to each other, revealing which genres (and other tags) are most associated.

# <markdowncell>

# Details: Using the Last.fm API, collect the top tags among a large set of popular artists (1000 or more). 
# 
# This data should be structured and stored in whatever format you deem most efficient. From this raw data, create a metric that compares how strongly associated the tags are to each other. Feel free to include any weighting or balancing in your metric, as long as you can explain it.

# <markdowncell>

# Resources:
# <ul>
# <li>API details: http://www.last.fm/api/intro
# <li>Top Artists method: http://www.last.fm/api/show/chart.getTopArtists
# <li>Top Tags method: http://www.last.fm/api/show/artist.getTopTags
# </ul>

# <markdowncell>

# Deliverables:
# <ul>
# <li>Your clean, commented code — Python or Node.js strongly preferred.
# <li>Your data sets, both intermediate steps and the final output.
# <li>Short explanation of process and outcomes.
#     </ul>

# <markdowncell>

# <h3><u> Overview</u></h3>
# 
# Given the goal, resources, and deliverables, we want to initially complete two primary tasks:
# <ol>
# <li>obtain a dataset which relates a set of top tags to popular artists
# <li>create a metric comparing 'how strongly associated the tags are to each other'
#     </ol>
# 
# This python script looks to address the first goal.

# <markdowncell>

# <h3> Summary </h3>
# This script will call two API's to obtain the set of Top Artists and the set of tags that each of those artists has been tagged with. Those two sets of data are to be merged to create a dataset indicating the number of times a particular top artist has been tagged by a particular tag. 

# <codecell>

# Import packages

# General
from os import *
from pprint import pprint

# API usage
from requests import get

# data reshaping
from collections import defaultdict
import numpy as np
from pandas import *

# visualization
from matplotlib import pyplot as plt

# <codecell>

# display plots inline in python notebook
%matplotlib inline

# <markdowncell>

# <h4><i>Declaration of Objects</i></h4>
# 
# Two objects are declared: an Artist object, which contains artist characteristics; and an ArtistTag object, which contains tag information. 
# 
# <i>(The API carries alot of information with it, and sometimes the resulting dictionary references become too complex for others to grasp readily. It's definitely a choice favoring readibility over complexity.)</i>

# <codecell>

# Declare objects
class Artist:
    name = ""     # name of artist
    mbid = ""     # musicbrainz id
    playcount = 0 
    listeners = 0
    index = 0
    tag_count = 0
    tags = []
    
    def __init__(self, name, mbid, playcount, listeners, index):
        self.name = name;    
        self.mbid = mbid;
        self.playcount = playcount;
        self.listeners = listeners;
        self.index = index;
        self.tag_count = 0;
        tags = [];
        
    def addTag(self, artisttag):
        self.tag_count += 1;
        self.tags.append(artisttag)
        
    def maxTagCount(self):
        return max(x.count for x in self.tags)

class ArtistTag:
    name = ""     # name of artist
    tag = ""      # name of tag
    count = 0     # count of tags for the artist
    
    def __init__(self, name, tag, count):
        self.name = name;
        self.tag = tag;
        self.count = count;

# <codecell>

# change working directory
chdir('/Users/kylederosa/Documents/IPython notebooks/Last.fm')

# set API parameters
query_params = {
                'api_key': '',    ### add valid api key
                'format': 'json',
                }

# set API address
endpoint = 'http://ws.audioscrobbler.com/2.0/'

# <markdowncell>

# <h4><i>Using the API to get top artist info</i></h4>
# 
# We first submit a get method to Last.fm's 'chart.gettopartists' API. Our interest is obtaining a unique key to identify artists, as well as some definition of what 'top' entails. 
# 
# After exploring some of the data, we choose 'name' over 'mbid' (music brainz id) as a unique artist identifier. A bit unintuitive, as one would expect the potential of non-unique 'name''s, but a short query into 'mbid' revealed that about 2% of our artists had no value for 'mbid'.
# 
# Additionally, we chose to retain the 'playcount' and 'listeners' data for each artists, as it seemed intuitive that these data may provide the metric by which 'top artist' is measured.

# <codecell>

#query API for top artist data
top_artist_params = query_params
top_artist_params['method'] = 'chart.gettopartists'
top_artist_params['limit'] = 1000

response = get( endpoint, params=top_artist_params)
top_artists = response.json()

# <codecell>

# there is one element in the list, a dictionary element named 'artists', which contains page metadata and artist information
# retain only artist information

top_artists = top_artists['artists']['artist']

# <codecell>

# Generate a list of Artist objects
# Generate a list of artist names by their index value
#    note, don't try using mbid (music brainz ID), mbid is missing in 2% of the data

Top_Artists = {}
top_artists_index = []
i = 0
for artist in top_artists:
    Top_Artists[artist['name']] = Artist(artist['name'], artist['mbid'], int(artist['listeners']), int(artist['playcount']), int(i))
    top_artists_index.append(artist['name'])
    i+=1

# <markdowncell>

# <h4><i>Using the API to get top artist tag info</i></h4>
# 
# At this point, we've generated a dictionary of Artist objects, keyed by the artist's name. We now look to utilize the 'artist.getTopTags' API to obtain the top tags associated with each artist. 
# 
# The nature of the API makes it challenging to obtain tag information for all of our artists, as our GET method can only be used for a single artist at a time. From an efficiency standpoint, this is probably one of the sections that should be looked at first. 
# 
# The API returns data on the number of times a tag has been applied to a particular artist (tag count). However, some of the ArtistTag data for tag count were zero. For example, if 250 tags were included for a given artist, it was likely that a majority of those tags contained a zero for their tag count. Additionally, it was later discovered that the max value was 100 for any tag count. It appears that these tag count data were scaled between 0-100 according to some normalization method. It was also discovered that artists have varying number of top tags, indicating that a zero is a meaningful value, and thus different from no tags.
# 
# If, however, the goal was to look at the unnormalized version of all artist tags, we probably look to a different API.

# <codecell>

#query API for artist top tags data, over each top Artist
top_tags_params = query_params
top_tags_params['method'] = 'artist.getTopTags'

# Generate an empty dictionary of emtpy list elements
# the dictionary will contain lists of artists and their count (# of times tagged), where the dict key is the tag name
Top_Tags = defaultdict(list)

# just to keep track of the iterations, this is the slowest process, looks like it's about 450 seconds for 1000 artists (~7.5 mins)
i = 0
for artist in Top_Artists.keys():
    top_tags_params['artist'] = unicode(artist)
    if (((i+1)%100)) == 0:
        print(artist + " is/are the " + str(i+1) + "th artist of " +str(len(Top_Artists)))
    response = get( endpoint, params=top_tags_params)
    artist_top_tags = response.json()
    
# it's plausible that a new top artist may have no tags - perhaps overkill, but we only add tags for artists who have tags
    if 'tag' in artist_top_tags['toptags']:
        for tag in artist_top_tags['toptags']['tag']:

            # we are implementing a crude solution right now for those tag counts which are zero and meaningful - see treatment below
            if (int(tag['count'])==0):
                tc = 0.1;
            else:
                tc = int(tag['count'])
            Top_Tags[tag['name']].append(ArtistTag(artist, tag['name'], tc))

            Top_Artists[artist].addTag(ArtistTag(artist, tag['name'], tc))
    if (((i+1)%100)) == 0:
        print(artist + " has " + str(Top_Artists[artist].tag_count) + " tags")
    i+=1    

# <codecell>

tag_index = []
for tag in Top_Tags.keys():
    tag_index.append(tag)

# <markdowncell>

# <h4><i>Investigating the tag count and frequency data</i></h4>
# 
# Let's charactertize some of our tag count data. First, we want to see the number of tags that all artists have.

# <codecell>

tag_count = [x.tag_count for k,x in Top_Artists.iteritems()]
plt.hist(tag_count)
plt.show()

# <markdowncell>

# Hmmm, it looks like some of our Top artists have less than 100 tags. 
# 
# What about the tag scores themselves? Let's look at the upper bound tag count for each artist who has less that 100 tags.

# <codecell>

max_tag_count = [ artist.maxTagCount() for k,artist in Top_Artists.iteritems() if artist.tag_count < 100 ]

df_max_tag_count = DataFrame(max_tag_count)
print(df_max_tag_count.shape)
print('mean: ' + str(df_max_tag_count.mean(0)))
print('standard deviation: ' + str(df_max_tag_count.std(0)))

# <markdowncell>

# And it seems like the max tag count for all artists is 100.
# 
# After some more data digging, we've confirmed the following:
# <ul>
#     <li> the artists with fewer than 100 tags also have zero tag counts, where we can then assume that all tag counts are normalized and zeros are meaningfully different than no response
#     </ul>
# 
# This is normally where I would consult with other people to figure out what they want to do. The central issue is around the zero tag counts. We can't completely infer that zero tag counts actually imply that an artist has been tagged zero times. However, we need to reshape our data into a matrix of artists and tags. When we do this for each artist, there will be two types of zeros that have different meanings:
# 
# <ol>
#     <li> zero tag counts - an artist has a tag with a zero tag count
#     <li> no tag - an artist has no tag, and therefore has a zero tag count for all tags that were not included in their top tag list
#     </ol>
# 
# We need a method for handling these two cicumstances. For now, we will simply increment all 'zero tag counts' up to 0.1, under the hypothesis that the normalized tag score is a rounded figure. For a more robust treatment, we would randomly choose a number (without replacement) between 0.01 and 0.44, the range at which a number would be rounded down upon floor/ceiling rounding.
# 
# This is implemented in the section above, from the comment <i>'see treatment below'</i>.

# <markdowncell>

# <h4><i> Let's make a dataframe!</i></h4>
# 
# At this point, we have a Top Artist dictionary of 1000 artist objects, and 
# 
# <ul>
# <li>a Top Tags dictionary of $n$ lists of $k$ size, where
# <li>$n$ is the number of tags, and
# <li>$k$ is the number of artists per tag
#     </ul>
# The stage of getting data from the API and stripping it down to the 'essentials' is complete, and we look now to reshape the data into a form for analysis. 
# 
# Our immediate goal now becomes:
# 
# <ul>
#     <li>Create a dataset/dataframe/array where each record(row) is associated with one Artist, and 
# <li>each variable(column) is associated with one tag, and 
# <li>each field(cell) shall be the count, or the number of times an artist has been tagged
#     </ul>

# <codecell>

# create a pandas dataframe, where:
#    rows = artists, indexed by Top_Artists[].index
#    columns = tags, indexed by tag_index
#    each field represents the number of times an artist has been tagged

# consider recursion here

data = [ [] for i in range(len(tag_index)) ]
i = 0
for tag in tag_index:
    tag_counts = [float(0.0)] * len(Top_Artists)
    for artist in Top_Tags[tag]:
        tag_counts[Top_Artists[artist.name].index] = float(artist.count)
    data[i] = tag_counts
    i+=1

# tranpose our list of lists
data = map(list, zip(*data))

# set it to a numpy array
data = np.array(data)

# set the numpy array to pandas dataframe (we like labeling!)
df = DataFrame(data=data, columns=tag_index, index=top_artists_index)

# print some info about the dataframe for spot visual inspectation
print(df.shape)
print(df.iloc[:5, :10])

# <codecell>

# export dataframe to csv
df.to_csv('Lastfm.raw.csv', sep=",", encoding='utf-8')

