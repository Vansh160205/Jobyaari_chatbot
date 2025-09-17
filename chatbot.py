# jobyaari_chatbot.py
import os
import pandas as pd
import streamlit as st
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Import your scraper functions as-is
from bs4 import BeautifulSoup, Comment
import time, re, requests

# -----------------------------
# SCRAPER (unchanged)
# -----------------------------
def scrape_job_details(url):
    vacancies = "Not Found"
    age_limit = "Not Found"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        age_element = soup.select_one('li.age-list div.job-location')
        if age_element:
            age_limit = age_element.get_text(strip=True)

        list_items = soup.select('div.job-detail-detail ul.list li')
        for item in list_items:
            text_element = item.select_one('div.text')
            if text_element and 'Job Openings' in text_element.get_text():
                details_div = item.select_one('div.details')
                if details_div:
                    value_div = details_div.find_all('div', recursive=False)[-1]
                    vacancies = value_div.get_text(strip=True)
                    break
    except Exception as e:
        print(f"⚠️ Could not fetch details from {url}: {e}")
    return vacancies, age_limit


def scrape_jobyaari():
    base_url = "https://jobyaari.com/category/"
    categories = {
        "Engineering": "engineering",
        "Science": "science",
        "Commerce": "commerce",
        "Education": "education"
    }

    all_jobs_data = []
    for category_name, category_path in categories.items():
        url = f"{base_url}{category_path}"
        print(f"\n🔎 Scraping {category_name} jobs from {url} ...")
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            job_containers = soup.select('div.drop__container')
            print(f"   → Found {len(job_containers)} job posts in {category_name}")

            for idx, container in enumerate(job_containers, start=1):
                print(f"      • Processing job {idx}/{len(job_containers)} in {category_name}...")
                card = container.select_one('div.drop__card')
                if not card:
                    continue

                org_name = card.select_one('span.drop__profession')
                org_name = org_name.get_text(strip=True) if org_name else "Not Found"

                salary_element = card.select_one('span.salary-price')
                salary = salary_element.find_all('span')[-1].get_text(strip=True) if salary_element else "Not Found"

                exp_element = card.select_one('span.drop__exp')
                experience = exp_element.find_all('span')[-1].get_text(strip=True).replace('Years','').strip() if exp_element else "Not Found"

                qual_element = card.select_one('div.salary')
                qualification = qual_element.get_text(strip=True) if qual_element else "Not Found"

                post_url = "Not Found"
                comments = container.find_all(string=lambda text: isinstance(text, Comment))
                for comment in comments:
                    match = re.search(r'href="(https://jobyaari\.com/jobdetails/\d+)"', str(comment))
                    if match:
                        post_url = match.group(1)
                        break

                vacancies, age_limit = ("Not Found", "Not Found")
                if post_url != "Not Found":
                    print(f"         ↳ Fetching details from {post_url}")
                    vacancies, age_limit = scrape_job_details(post_url)
                    time.sleep(0.5)

                job_data = {
                    "Category": category_name,
                    "Organization Name": org_name,
                    "Vacancies": vacancies,
                    "Salary": salary,
                    "Age Limit": age_limit,
                    "Experience": experience,
                    "Qualification": qualification,
                    "Post URL": post_url
                }
                all_jobs_data.append(job_data)

            time.sleep(1)

        except Exception as e:
            print(f"⚠️ Error scraping {url}: {e}")

    df = pd.DataFrame(all_jobs_data)
    df = df[df["Organization Name"] != "Not Found"].reset_index(drop=True)
    df.to_csv("jobyaari_knowledge_base.csv", index=False)
    print(f"\n✅ Scraping complete! Total jobs collected: {len(df)}")
    return df

# -----------------------------
# STREAMLIT CHATBOT UI
# -----------------------------
st.set_page_config(page_title="JobYaari AI Assistant", page_icon="🤖", layout="wide")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Refresh Job Data"):
        with st.spinner("Scraping JobYaari..."):
            df = scrape_jobyaari()
            st.success(f"✅ Data refreshed! {len(df)} jobs extracted.")
    else:
        if os.path.exists("jobyaari_knowledge_base.csv"):
            df = pd.read_csv("jobyaari_knowledge_base.csv")
        else:
            with st.spinner("No dataset found. Scraping now..."):
                df = scrape_jobyaari()

    st.markdown("### 📊 Job Dataset Preview")
    st.dataframe(df.head(10), width='content')

# API key
os.environ["GROQ_API_KEY"] = st.secrets.get("GROQ_API_KEY", "API_KEY")

# Chat Title
st.title("🤖 JobYaari AI Assistant")

# LLM + Agent
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
agent = create_pandas_dataframe_agent(llm, df, verbose=False, allow_dangerous_code=True)

# Session state for conversation
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat like ChatGPT
for role, msg in st.session_state.chat_history:
    with st.chat_message("user" if role == "You" else "assistant"):
        st.markdown(msg)

# Input field pinned at bottom
if query := st.chat_input("Ask me anything about jobs..."):
    # User bubble
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.chat_history.append(("You", query))

    # Assistant bubble
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = agent.invoke(query)
                answer = result.get("output", "No answer generated.")
            except Exception as e:
                answer = f"⚠️ Error: {e}"
            st.markdown(answer)
    st.session_state.chat_history.append(("Bot", answer))
