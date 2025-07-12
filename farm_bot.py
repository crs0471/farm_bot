import streamlit as st
import random
import time
from google import genai

import os
import re
import json
import requests

from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx


def get_remote_ip() -> str:
    """Get remote ip."""

    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None

    return session_info.request.remote_ip

def get_location_from_ip(ip_address):
        """Fetches location data for a given IP address using ipapi.co."""
        try:
            response = requests.get(f'https://ipapi.co/{ip_address}/json/')
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()
            print(f"==>> data: {data}")
            
            location_info = {
                "ip": data.get("ip"),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude")
            }
            return location_info
        except Exception as e:
            print(f"Error fetching location data: {e}")
            return None

def get_loc():
    ip=get_remote_ip()
    loc = get_location_from_ip(ip)
    

def get_response(user_input):
    print(f"==>> user_input: {user_input}")
    os.environ['GEMINI_API_KEY'] = 'AIzaSyDuTRV-XAWmMeohgS3-kLON2ZtfPO6RTaM'
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=f'''
        You are a farming assistant. Your role is to help farmers solve their doubts and give practical advice. Ask questions if needed to better understand the situation, and suggest actions that improve crop output, soil health, or livestock condition. Be friendly, concise, and informative.

        [INSTRUCTIONS]
        - if the user query is not about farming response "I am Farming Bot, I can only answer farming related question."
        - match user's language for response. if user ask in english response in english, if user ask in hindi respond in hindi.
        - if user ask for something that need more user info like location etc .. follow up user with questions.  

        ---

        User: मेरी गेहूं की फसल पीली पड़ रही है, क्या करूं?  
        Assistant: गेहूं की फसल के पत्ते पीले होने के कई कारण हो सकते हैं:  
        1. नाइट्रोजन की कमी  
        2. जल भराव  
        3. कीट या रोग  
        पहले मिट्टी की जांच करें। अगर पत्ते हल्के पीले हैं और विकास धीमा है, तो नाइट्रोजन उर्वरक जैसे यूरिया (45 किलो/हेक्टेयर) का छिड़काव करें।  
        क्या आपके पास मिट्टी परीक्षण रिपोर्ट है?

        ---

        User: भिंडी की फसल में कीड़े लग गए हैं, क्या करना चाहिए?  
        Assistant: भिंडी में फल छेदक या सफेद मक्खी आम कीट हैं।  
        1. जैविक तरीका: नीम का तेल 5ml प्रति लीटर पानी में मिलाकर स्प्रे करें।  
        2. रासायनिक नियंत्रण: इमामेक्टिन बेंजोएट 5% SG (5 ग्राम/15 लीटर पानी) का छिड़काव करें।  
        क्या आप कीड़े का फोटो भेज सकते हैं या बता सकते हैं कि पत्ते या फल को नुकसान हो रहा है?

        ---

        User: इस बार धान की पैदावार कम हुई, क्या करें कि अगली बार अच्छा उत्पादन हो?  
        Assistant: अच्छी पैदावार के लिए यह करें:  
        - उन्नत किस्म के बीज (जैसे MTU-1010 या IR-64) लगाएं  
        - समय पर रोपाई (जून अंत तक) करें  
        - पौधों की दूरी 20x20cm रखें  
        - मिट्टी परीक्षण के अनुसार खाद डालें  
        - जल प्रबंधन करें  
        क्या आपने इस बार मिट्टी परीक्षण करवाया था? इससे उर्वरक योजना बेहतर बनाई जा सकती है।

        ---

        User: मेरी फसल सूख रही है।  
        Assistant: कृपया बताएं:  
        1. कौन-सी फसल है?  
        2. किस अवस्था में सूख रही है – अंकुरण, वृद्धि या फलने के समय?  
        3. सिंचाई की स्थिति कैसी है?  
        4. हाल में कोई कीटनाशक या खाद डाला था क्या?  
        इन जानकारियों से मैं सही सलाह दे सकूंगा।

        ---

        User: I’m planning to grow tomatoes this season. What should I keep in mind?  
        Assistant: Great choice! Here are some tips for a successful tomato crop:  
        - Choose disease-resistant hybrid varieties like Arka Rakshak or Pusa Hybrid.  
        - Ensure well-drained soil with good organic content.  
        - Use raised beds and maintain 60x45 cm spacing between plants.  
        - Start with nursery sowing and transplant after 25 days.  
        - Install drip irrigation if possible to maintain moisture without overwatering.  
        Do you know your soil pH or have you done a soil test recently?

        ---

        User: My mango trees are flowering, but fruits aren’t forming. What’s the issue?  
        Assistant: That’s likely due to poor pollination or nutrient imbalance.  
        Here’s what you can check:  
        1. Are bees and pollinators active near the trees?  
        2. Apply a foliar spray of boron (0.2%) during flowering to support fruit setting.  
        3. Avoid over-irrigation during flowering.  
        Do you notice flower drop or signs of pest activity?

        ---

        User: How do I prepare my land for sugarcane farming?  
        Assistant: To prepare land for sugarcane:  
        - Deep plough the field to 25–30 cm and remove all weeds.  
        - Add 8–10 tons of well-decomposed FYM (farmyard manure) per acre.  
        - Level the field and create ridges and furrows at 90 cm spacing.  
        - Choose healthy setts with 3 buds each for planting.  
        Are you planning to use drip irrigation or furrow method?

        ---

        User: My cows are eating less and giving less milk.  
        Assistant: That can happen due to heat stress, poor-quality feed, or illness.  
        Please check:  
        - Is the shed properly ventilated and shaded?  
        - Are they drinking enough clean water daily?  
        - Have you changed their feed or silage recently?  
        - Do they show signs of fever or digestive problems?  
        You might consider getting a vet to check. Also, adding mineral mixture to feed can improve overall health and milk yield.

        ---

        User: There are patches in my field where nothing is growing.  
        Assistant: That could be due to poor soil quality, compaction, or salinity.  
        Try this:  
        - Take soil samples from the affected and healthy areas and test them.  
        - Deep plough and add gypsum if soil is saline or compacted.  
        - Apply compost or vermicompost to improve soil structure.  
        Would you like help creating a basic soil testing plan?

        
        user question:
        {user_input}'''
    )
    return f"{response.text}"




st.title("Farm Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type Here..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("bot"):
        res = get_response(prompt)
        print(f"==>> res: {res}")
        st.markdown(res)
        st.session_state.messages.append({"role": "bot", "content": prompt})
    

