# 🤖 F1Buddy – Budget Chatbot for International Students

F1Buddy is a smart AI-powered chatbot designed to help international students in the U.S. find **budget-friendly restaurants, groceries, and halal food options** based on location and cuisine. It uses live search APIs from **Yelp** and **Google Serper** combined with **LangChain + Groq** to deliver relevant and reliable recommendations in real time.

---

## 💡 Features

- 🍱 Recommends **budget-friendly restaurants** and **grocery stores**
- 📍 Location-based filtering (e.g., “Indian grocery near Chicago”)
- 🧠 Hybrid search using **Yelp API + Google Search API**
- 🗣️ Conversational interface built with **LangChain Agent + Groq LLM**
- ✅ Filters results to show **only food/grocery-related queries**
- 🌐 Web results fallback if Yelp has no data

---

## 🚀 Tech Stack

| Component         | Tech Used                         |
|------------------|------------------------------------|
| LLM              | `Groq Llama3-8b` via LangChain     |
| Search APIs      | `Yelp API`, `Google Serper API`    |
| Framework        | `Streamlit` for UI                 |
| Logic Layer      | `LangChain Agents`, `ConversationBufferMemory` |
| Utilities        | `dotenv`, `re`, `unicodedata`, `urllib.parse` |

---

## ⚙️ Installation Guide

### 1. Clone the Repo

```bash
git clone https://github.com/Kalyankaparaju/f1buddy-chatbot.git
cd f1buddy-chatbot
