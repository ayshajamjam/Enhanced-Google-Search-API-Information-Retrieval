# Information Extraction Project

**Goal:** develop an information retrieval system that takes user relevance feedback to improve search results (disambiguate queries and improve the relevance of the query results)

### Setting Up the Project Locally
pip3 install virtualenv
virtualenv &lt;your-env&gt;
source &lt;your-env&gt;/bin/activate
&lt;your-env&gt;/bin/pip install google-api-python-client

query URL = python main.py &lt;google api developer key&gt; &lt;google engine id&gt; &lt;precision&gt; &lt;query&gt;
