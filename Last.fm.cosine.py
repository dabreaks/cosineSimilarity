# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# <h3><u> Overview</u></h3>
# 
# Given the goal, resources, and deliverables, we want to initially complete two primary tasks:
# <ol>
#     <li>obtain a dataset which relates a set of top tags to popular artists
#     <li>create a metric comparing 'how strongly associated the tags are to each other'
#     </ol>
# This python script looks to address the second goal.
# The script 'Last.fm.py' looks to address the first goal, and should be run prior to this script's implementation

# <markdowncell>

# <h3> Summary </h3>
# At the completion of 'Last.fm.py', a dataset of the number of times an artist has been tagged was exported to csv. In this script, we look to load that dataset, and generate the cosine similarity for all tags.

# <codecell>

# General
from os import *
from pprint import pprint

# Data reshaping
import numpy as np
from pandas import *

# <codecell>

# change working directory
chdir('/Users/kylederosa/Documents/IPython notebooks/Last.fm')

# <codecell>

# import dataframe from csv
df = DataFrame.from_csv('Lastfm.raw.csv', sep=',', encoding='utf-8')

# <markdowncell>

# <h4></i> Cosine Similarity</i></h4>
# 
# Now that we've got our environment set up, let's look a bit more into cosine similarity. Formally, we define similarity as the cosine measure of the innner product space between two vectors:
# 
# $$\text{similarity} = \cos(\theta) = {A \cdot B \over \|A\| \|B\|} = \frac{ \sum\limits_{i=1}^{n}{A_i \times B_i} }{ \sqrt{\sum\limits_{i=1}^{n}{(A_i)^2}} \times \sqrt{\sum\limits_{i=1}^{n}{(B_i)^2}} }$$
# 
# and graphically below:

# <markdowncell>

# ![my_image](https://engineering.aweber.com/wp-content/uploads/2013/02/4AUbj.png)

# <markdowncell>

# Informally, we're stating that each of our tags can be represented in the multidimensional world of artists by a vector of their tag counts. By comparing cosine similarity between two tag vectors, we can get a sense of how close these vectors 'overlap'. The cosine of an angle is bounded by $[-1, 1]$, where $1$ indicates perfect similarity (the vectors overlap), $-1$ indicates perfect dis-similarity (the vectors point in opposite directions, and $0$ indicates orthoganal angles (the vectors share almost no similarity or dissimilarity). 

# <markdowncell>

# As far as why we're choosing cosine similarity:
# 
# Well we know our data is fairly sparse - it's much more likely that an artist has a small number of tags (relative to the total number of tags), and so much of our data is zeros. In fact:

# <codecell>

print( df.stack().value_counts(0))

# <markdowncell>

# Zeros occur more frequently than any other number in our dataset by a few orders of magnitude.
# 
# While that's all well and good, I'm relying on cosine similarity because of it's popularity regarding text clustering and from earlier data mining work. Upon testing our performance against the validation set, we'll evaluate further from there. More importantly, it's important just to do *something* and then spend time validating afterwards after establishing time/effort/performance. 

# <markdowncell>

# <h4><i> (Some) Performance choices </i></h4>
# 
# Performance! So we've got a fair number of observations, and looking at the formula for cosine similarity:
# 
# $$\text{similarity} = \cos(\theta) = {A \cdot B \over \|A\| \|B\|} = \frac{ \sum\limits_{i=1}^{n}{A_i \times B_i} }{ \sqrt{\sum\limits_{i=1}^{n}{(A_i)^2}} \times \sqrt{\sum\limits_{i=1}^{n}{(B_i)^2}} }$$
# 
# The complexity for calculating one pair of similarity between $A$ and $B$ is $O(n)$, and would need to be updated for all such pairs (in our case, pairs of tags, so $n^2$ pairs), resulting in $O(n^3)$. 
# 
# That's a bit too slow for an implementation of this size, so we'll be making a shift towards numpy and pandas's linear algebra for matrix manipulation.

# <markdowncell>

# We'll look to create a matrix of size $n$ by $n$ containing the dot product of all pairs of tags,
# and then another matrix of size $n$ by $n$ containing the product of the square root sum of squares for all pairs of tags.
# 
# Then, we simply element-wise divide the numerator matrix by the denominator matrix to obtain a matrix of cosine similarity for all pairs of tags.
# 
# Label, export, and then on to validation!

# <codecell>

# create cosine similarity matrix for tags

n = len(df.columns)                    # number of tags
tags = df.columns.values.tolist()      # list of tag names, where the index matches the dataframe columns

# gen a df of the sum of squares for each tag
squares = df ** 2
ss = squares.sum(axis=0)
ss_rt = (ss.apply(np.sqrt)).reshape(n,1)

cs_denom = ss_rt * ss_rt.transpose()
cs_denom = DataFrame(cs_denom, index = tags, columns = tags)

# <codecell>

# gen a df of the dot product for each tag
cs_num = np.dot(df.transpose(), df)

cs_num = DataFrame(cs_num, index = tags, columns = tags)

# <codecell>

# gen a df of cosine similiarity

tag_cs = np.divide(cs_num, cs_denom)
tag_cs = DataFrame(tag_cs, index=tags, columns=tags)

print(tag_cs.shape)
print(tag_cs.iloc[:5, :10])

# <codecell>

# export dataframe to csv
tag_cs.to_csv('Lastfm.cosine_similarity.csv', sep=",", encoding='utf-8')

# <markdowncell>

# <h4><i> Next Steps </i></h4>
# 
# There are few next steps that come to mind given the set of extra credit assignments. In order:
# 
# 
# <ul>
#     <li> use the similar tag API to validate our data. This would involve utilizing our cosine similarity dataframe to create a new dataframe. I'd likely create one where we have tags as our rows, the rank order of similarity as columns (0 to len(tags)-1), and each field would be the index number of the similar tag. I'm less familiar with validating the rank order of items, but a couple of things come to mind:</li>
#         <ul>
#             <li> evaluating if we have a complete match in similarity</li>
#             <li> evaluate if our first similar tag matches their first similar tag</li>
#             <li> evaluate if any of our first $k$ similar tags are within their similar tag matches</li>
#             <li>I'd want to do more research on appropriate rank order validation and test set methodology</li></ul>
# 
# </ul>
# <ul>    <li> assess our validation. How did we perform? Where did we perform well? Where did we not perform well? What are these characteristics?</li>
#     <li> tune cosine similarity (probably mean normalize by the number of tags, because we have evidence of artists who have less than 100 tags), or adopt other similarity method. </li>
#             </ul>

