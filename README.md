# JobYaari AI Assistant

## Overview

JobYaari AI Assistant is a Streamlit-based chatbot designed to help users query job listings scraped from [JobYaari.com](https://jobyaari.com). The chatbot uses LangChain's Pandas DataFrame Agent and Groq LLM to provide intelligent responses to job-related queries.

## Features

* Scrapes job listings from JobYaari.com across multiple categories (Engineering, Science, Commerce, Education)
* Extracts detailed information including:

  * Organization Name
  * Vacancies
  * Salary
  * Age Limit
  * Experience
  * Qualification
  * Post URL
* Stores data in a structured CSV file (`jobyaari_knowledge_base.csv`)
* Interactive chat interface via Streamlit
* Allows refreshing the dataset dynamically from the sidebar
* Maintains session-based chat history

## Architecture

The chatbot follows this workflow:

1. **Web Scraping:** Scrapes JobYaari.com using Python, Requests, and BeautifulSoup.
2. **Data Storage:** Stores scraped data in a Pandas DataFrame and CSV.
3. **LLM Integration:** LangChain agent queries the DataFrame using Groq's LLM.
4. **Frontend:** Streamlit provides a chat interface and sidebar controls.
5. **User Interaction:** Users ask queries; the agent fetches relevant job data and responds.

## Requirements

* Python 3.9+
* Streamlit
* pandas
* requests
* beautifulsoup4
* langchain-groq
* langchain\_experimental

## Installation

1. Clone this repository:

```bash
git clone https://github.com/Vansh160205/Jobyaari_chatbot.git
cd Jobyaari_chatbot
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add your Groq API key in `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY="YOUR_API_KEY_HERE"
```

## Usage

1. Run the Streamlit app:

```bash
streamlit run jobyaari_chatbot.py
```

2. Use the sidebar to refresh job data.
3. Type your job-related query in the chat input box.

## Example Queries

* "Show engineering jobs with experience under 5 years"
* "List jobs in commerce category with salary above 5 LPA"
* "Find jobs with age limit under 30 years"

## Folder Structure

```
jobyaari-ai-assistant/
│
├── jobyaari_chatbot.py           # Main Streamlit app
├── jobyaari_knowledge_base.csv   # Scraped job data
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── JobYaari_AI_Assistant_Architecture.pdf  # Architecture PDF
└── .streamlit/
    └── secrets.toml              # API keys
```

## License

This project is licensed under the MIT License.
