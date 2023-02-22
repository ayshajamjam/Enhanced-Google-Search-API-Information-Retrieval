# Google Search API Information Retrieval Project

**Goal:** develop an information retrieval system that takes user relevance feedback to improve search results. We needed to disambiguate queries and improve the relevance of the query results. For example, given the query 'milky way', Google provides all sorts of results including about chocolates, space, and restaurants. After getting feedback from the user, the program determines the next best query based on the relevant results to be 'milky way galaxy'.

[Demo video of application in action](https://youtu.be/auG58f2L7qs)

### Setting Up the Project Locally
1. pip3 install virtualenv
2. virtualenv <your-env>
3. source <your-env>/bin/activate
4. <your-env>/bin/pip install google-api-python-client
5. Pip3 install nltk
6. python3 -m nltk.downloader stopwords
7. python3 -m nltk.downloader punkt

[Other Project Info (for owner only)](https://docs.google.com/document/d/1lArA6P5Gs4dNPR393hlErKmaceMZKUSeBGF_MEwbVd0/edit?usp=sharing)

**Run this and download the packages when you first run the program (if the above commands don't work)**

```
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download()
```

query URL = python main.py &lt;google api developer key&gt; &lt;google engine id&gt; &lt;precision&gt; &lt;query&gt;


###High-Level Project Design Description: 

All of our code is contained inside main.py. We initially import a few libraries. We then include helper functions to assist with computing log_frequencies and inverse_document_frequencies which are used to calculate the tf-idf values later on. The helper functions also include methods for commuting n-gram probabilities which are used for word ordering.

Within main, we check for the correct number of arguments passed and save those arguments in appropriate values (developer key, engine key, query, precision).

Using the Google Search API, we retrieved 10 search results for our query, which is passed by the user in the terminal.

We then create a set of vocabulary words based on the titles and snippets  (summaries) returned by each result. We clean the titles and snippets to remove non-alphanumeric characters. We also remove stop words using the NLTK text processing library.

We then iterate through the responses returned by the API and present the title, URL, and summary to the user. For each result, the user provides yes/no feedback as to whether or not the result is relevant.

For each result, we iterate over each term in the vocabulary to calculate the term frequencies of each word within the title and snippet of that particular result. We convert the term frequencies to log frequencies to account for the fact that relevance does not grow linearly with term frequency. This way, we don't give too many points to documents that contain high frequencies of query words because they aren't necessarily more relevant to what we intended for our query.
We also maintain a tally of the document frequency for each term in the vocabulary. For each result, we calculate the inverse document frequency to give a higher weight for rare terms.
Once we have parsed through all the results and gathered feedback, we calculate the tf_idf weight for each word using the log-frequency weights and inverse document frequencies.
We then calculate the resulting precision based on the feedback and number of HTML documents returned to determine the next steps. The precision was defined by the user as an argument. If the resulting precision is above 0.9, for example, then the task is complete. If it is 0.0, we just return since the results are not fruitful and there is nowhere to go from here. If neither of these cases occur, we use the user's feedback to determine an augmented query for the next iteration. To do so, we use Rocchio's algorithm which makes use of the tf_idf values for each term in the vocabulary as well as the relevant and non-relevant document results. Please see “Query Expansion” below for more details.

From the results of Rocchio’s algorithm, we then determine the top-2 words we could add to our query. We then determine the word ordering and number of words to add by considering the different permutations and using n-grams. Please see “Query Ordering” below for more details.

We repeat this process until the desired precision is met.

Libraries used: we used some basic libraries like math for logarithmic calculations. We also use the NLTK text processing for tokenization and eliminating stop words when building our vocabulary. We had to include the ssl library in order to download the packages for NLTK when we first ran the program. We used the re library to handle regex operations which eliminated non-alphanumeric characters. We used itertools to create permutations of the query to figure out which ordering is best.

How we handled non-HTML documents: When iterating through each search result, the first check we do is to see if the result has a “fileFormat” field. If it does, then it is not an HTML file. If it doesn’t include this field, then it is an HTML file and we increment the value for html_docs_returned. We use this value to determine the inverse document frequency and result precision.

We also noticed that there were occasions when a result didn’t have a snippet or title which would throw a keyError. For this reason, if we came across a result like this, we chose to skip it.

###Query Expansion: 

If we determined that the precision of the result returned by Google was less than 0.9, we used Rochhio’s algorithm to calculate which words can be appended to the query. We set the alpha=1, beta=0.5, and gamma=0.25. We then calculate the q_0 vector by iterating over each term in the vocabulary and checking if it is in the query. This q_0 vector consists of a 1 for each value in the query and 0 for each value that is not.

We then calculated the relevant and non-relevant sums. We iterated over each html document returned and checked if that document was relevant or not. If it was, then for each word in the vocabulary, we added the tf-idf value for that word to relevant_sum. Otherwise, we added the tf-idf value for that word in nonrelevant_sum. This way, relevant_sum consists of the sum of all tf-idf values for the words in relevant documents and nonrelevant_sum contains the sum of all tf-idf values for the word in irrelevant documents.

Then for each word in the vocabulary we iterated through the q_0 vector, multiplying it by alpha, the relevant_sum vector, multiplying it by beta/relevance_count, and the nonrelevant_sum vector, multiplying it by gamma/nonrelevant_doc_count.

We then declared a dictionary q_tplus1. In this vector we stored the final weight of each word determined by q_0[word] + relevant_sum[word] - nonrelevant_sum[word].

We sorted the words contained in q_tplus1 and determined which two words had the highest values. In query ordering, we decided whether it is best to append the term with the highest tf-idf value, or to append both terms to the old query.

###Query Ordering:

After calculating the top two words we can augment our query with, we calculated two sets of permutations. Permutations1 consists of all the permutations of the old query and the term from the new query with the highest tf-idf value. Permutations3 consists of all the permutations of the old query and both the terms from the augmented options list.

For each permutation combination in permutations1, we compute the sentence_logprob (see explanation below). If the result is greater than the highest probability seen so far, then we update highest_prob and update our best_query to be this particular permutation.

We do the same calculation for permutations3. In order to decide if a two word expansion is greater than a one word expansion, we check if the permutation probability for any given permutation plus five is greater than the highest probability calculated from permutations1. This number five was empirically decided based on the results we were seeing.

####N-grams:

To decide the ordering of the terms in our new query, we used n-gram probabilities. We did not use any particular publication. Instead, we built on the knowledge from the NLP class we are taking this semester. We use get_ngrams() to split the sentences into one or two word ngrams. We use count_ngrams() to count the number of times each unigram and each bigram is seen. We use raw_bigram_probability to calculate the probability of a bigram, which is the number of times a bigram is seen divided by the number of times the first word’s unigram is seen. To calculate raw_unigram_probability, we divide the number of times the unigram is seen by the total number of words seen. In sentence_logprob(), we add the probabilities of all smoothed bigrams in the sentence to calculate the likelihood of that sentence. In our project, we use this to determine the order of words in the query. For example, sergey brin would have a much higher sentence probability than brin sergey because the probability of brin given sergey is higher than that of sergey given brin. 

###Test Cases: (see attached pages for full transcripts)

| Query         | Our Second Iteration         | Professor’s Second Iteration |
| ------------- | ---------------------------- | ---------------------------- |
| “per se”      | “per se michelin restaurant” | “per se york thomas”         |
| “brin”        | “sergey brin”                | “brin google sergey”         |
| “cases”       | “cases deaths data”          | ‘cases death coronavirus“    |
| “a gentleman” | “a gentleman moscow”         | “a gentleman moscow novel”   |
| “spears”      | “britney spears”             | “spears britney day”         |

**Challenge:** we wanted words like 'death' and 'deaths' to be equivalent but opted against using stemming and lemmatization tools because we didn't want words like 'building' and 'build' to equate since they would provide very different query results.
