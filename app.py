import os
import streamlit as st
import unicodedata
import re
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.memory import ConversationBufferMemory
from yelpapi import YelpAPI
import urllib.parse

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
YELP_API_KEY = os.getenv("YELP_API_KEY")

if not GROQ_API_KEY or not SERPER_API_KEY or not YELP_API_KEY:
    st.error("❗ Missing one or more required API keys in .env file")

ALLOWED_TOPICS = [
    "restaurant", "grocery", "cheap", "budget", "food", "market", "store", "cuisine", "eat", "dine",
    "place", "dosa", "sushi", "indian", "mexican", "thai", "italian", "chinese", "biryani",
    "snacks", "meal", "lunch", "dinner", "breakfast", "veg", "nonveg", "halal", "buffet", "fast food",
    "korean", "african", "asian", "japanese", "ethiopian", "pakistani", "bangladeshi", "vegetarian"
]

def is_allowed_query(query: str) -> bool:
    return any(keyword in query.lower() for keyword in ALLOWED_TOPICS)

def clean_surrogates(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')

def extract_limit(query: str, default: int = 5) -> int:
    match = re.search(r'\b(\d{1,2})\b', query)
    return int(match.group(1)) if match else default

def extract_location(query: str) -> str:
    match = re.search(r'(in|near)\s+([\w\s,.]+)', query.lower())
    return match.group(2).strip() if match else "USA"

CATEGORY_KEYWORDS = {
    "afghan": "afghani", "indian": "indpak", "halal": "halal",
    "grocery": "grocery", "asian": "asianfusion", "korean": "korean",
    "ethiopian": "ethiopian", "caribbean": "caribbean", "japanese": "japanese",
    "vegetarian": "vegetarian"
}

yelp = YelpAPI(YELP_API_KEY)

def infer_yelp_category(query: str) -> str:
    for key, category in CATEGORY_KEYWORDS.items():
        if key in query.lower():
            return category
    return None

def yelp_search(query: str, location: str = "USA", limit: int = 5) -> str:
    category = infer_yelp_category(query)
    try:
        results = yelp.search_query(
            term=query, location=location, sort_by='best_match',
            limit=limit, categories=category
        )
    except Exception:
        return None

    if not results.get("businesses"):
        return None

    formatted = "\U0001F37D️ **Top Yelp Recommendations:**\n"
    for i, biz in enumerate(results["businesses"], start=1):
        name = biz.get("name", "Unknown")
        price = biz.get("price", "N/A")
        address = ", ".join(biz.get("location", {}).get("display_address", []))
        url = biz.get("url", "#")
        safe_url = urllib.parse.quote(url, safe=':/?&=%')

        formatted += (
            f"\n**{i}. {name}**\n"
            f"- \U0001F4B2 **Price:** {price}\n"
            f"- \U0001F4CD **Address:** {address}\n"
            f"- \U0001F517 [Visit Yelp]({safe_url})\n"
        )
    return formatted.strip()

search = GoogleSerperAPIWrapper(serper_api_key=SERPER_API_KEY)

def serper_search(query: str, limit: int = 5) -> str:
    results = search.results(query)
    organic = results.get("organic", [])
    if not organic:
        return None

    formatted = "\U0001F310 **Top Web Results:**\n\n"
    count = 0
    for item in organic:
        title = item.get("title", "").split(" - ")[0].strip()
        snippet = item.get("snippet", "No description available.").strip()
        link = item.get("link", "#")
        if not title or any(site in link for site in ["reddit", "tripadvisor", "youtube", "facebook"]):
            continue

        price = "$" if any(word in snippet.lower() for word in ["cheap", "budget", "affordable"]) else "$$"

        formatted += (
            f"{count + 1}. **{title}**\n"
            f"\U0001F4B2 Price: {price}\n"
            f"📜 {snippet[:100]}...\n"
            f"\U0001F517 [More Info]({link})\n\n"
        )
        count += 1
        if count >= limit:
            break
    return formatted.strip()

def hybrid_tool(query: str) -> str:
    limit = extract_limit(query)
    location = extract_location(query)
    yelp_result = yelp_search(query, location=location, limit=limit)
    if yelp_result:
        return yelp_result
    web_result = serper_search(query, limit=limit)
    if web_result:
        return web_result
    return "🚫 Sorry, I couldn't find any relevant results."

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192",
    temperature=0.7
)

hybrid_search_tool = Tool(
    name="Smart Web+Yelp Search",
    func=hybrid_tool,
    description="Smartly searches Yelp and the web for restaurant or grocery store recommendations."
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

agent = initialize_agent(
    tools=[hybrid_search_tool],
    llm=llm,
    agent="chat-conversational-react-description",
    memory=memory,
    verbose=False
)

st.set_page_config(page_title="F1Buddy", layout="centered")
st.title("🤐 F1Buddy – Budget Chatbot for International Students")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.chat_input("Ask me about budget restaurants or groceries...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    if is_allowed_query(user_input):
        try:
            response = hybrid_tool(user_input)
        except Exception as e:
            response = f"❌ Error: {e}"
    else:
        response = "❌ Sorry, I can only help with budget-food or grocery-related questions."
    st.session_state.history.append({"role": "assistant", "content": response})

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(clean_surrogates(msg["content"]), unsafe_allow_html=True)
