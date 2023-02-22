# Google Search API Information Retrieval Project

**Goal:** develop an information retrieval system that takes user relevance feedback to improve search results. We needed to disambiguate queries and improve the relevance of the query results. For example, given the query 'milky way', Google provides all sorts of results including about chocolates, space, and restaurants. After getting feedback from the user, the program determines the next best query based on the relevant results to be 'milky way galaxy nasa'.

### Setting Up the Project Locally
1. pip3 install virtualenv
2. virtualenv &lt;your-env&gt;
3. source &lt;your-env&gt;/bin/activate
4. &lt;your-env&gt;/bin/pip install google-api-python-client

query URL = python main.py &lt;google api developer key&gt; &lt;google engine id&gt; &lt;precision&gt; &lt;query&gt;

**Run this and download the packages when you first run the program**

```
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download()
```

## Explanation of Code

Using the Google Search API, we retrieved 10 search results for our query, which is passed by the user in the terminal.

We then had to create a set of vocabulary words seen in the title and snippet returned in each result. We cleaned the titles and summaries to remove non-alphanumeric characters. We also removed stop words using the NLTK text processing library.

Challenge: we wanted words like 'death' and 'deaths' to be equivalent but opted against using stemming and lemmatization tools because we didn't want words like 'building' and 'build' to equate since they would provide very different query results.

We then iterated through 10 of the responses returned by the API and presented the title, URL, and summary to the user. For each result, the user would provide yes/no feedback as to whether or not the result was relevant.

For each result, we iterated over each term in the vocabulary to calculate the term frequencies of each word within the title and snippet of that particular result. We converted the term frequencies to log frequencies to account for the fact that relevance does not grow linearly with term frequency. This way, we don't give too many points to documents that contain high frequencies of query words because they aren't neccessarily more relevant to what we intended for our query.

We also maintained a tally of the document frequency for each term in the vocabulary. For each result, we calculated the inverse document frequency to give a higher weight for rare terms.

Once we parsed through all the results and gathered feedback, we calculated the tf_idf weight using the log-frequncy weighting and inverse document frequency.

We then calculated the precision, which is the number of relevant documents divided by the number of valid html documents returned by the API. The precision was defined by the user as an argument. If the resulting presicion was above 0.9, for example, then the task was complete. Otherwise, we needed to use the user's feedback to determine an augmented query for the next iteration. To do so, we used Rocchio's algorithm which makes use of the tf_idf values for each term in the vocabulary as well as the relevant and non-relevant results.

We then determined the top-2 words and added them to our query to repeat the process until the desire precision is met.
