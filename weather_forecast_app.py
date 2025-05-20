import streamlit as st
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from functools import lru_cache

# --- Page Configuration ---
st.set_page_config(page_title="🌈 Enhanced Weather App", layout="centered")
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title & Description ---
st.title("🌦️ Global Weather Dashboard")
st.markdown("""
Get **real-time weather**, **air quality**, and **forecast trends** for your favorite city and state.
Powered by WeatherAPI + Streamlit Magic 🌟
""")

# --- Helper Functions ---
weather_emojis = {
    "Sunny": "☀️", "Clear": "🌙", "Partly cloudy": "⛅", "Cloudy": "☁️",
    "Rain": "🌧️", "Patchy rain possible": "🌦️", "Snow": "❄️",
    "Mist": "🌫️", "Thunder": "⛈️", "Overcast": "☁️"
}

def convert_temp(c, unit):
    return c if unit == "Celsius" else round((c * 9/5) + 32, 1)

# --- Dropdowns for Country, City, Units ---
states = {
    "USA": ["New York", "Los Angeles", "Chicago"],
    "India": ["Delhi", "Mumbai", "Bangalore"],
    "UK": ["London", "Manchester", "Birmingham"],
    "Australia": ["Sydney", "Melbourne", "Brisbane"]
}

country = st.selectbox("🌍 Select a country", list(states.keys()))
city = st.selectbox("📍 Select a city", states[country])
unit = st.radio("🌡️ Temperature Unit", ["Celsius", "Fahrenheit"], horizontal=True)

# --- API Setup ---
API_KEY = "3fc5200a3cmsh3b49e3bc93e056fp177ba7jsn5217a5bac85e"
url = "https://weatherapi-com.p.rapidapi.com/forecast.json"
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "weatherapi-com.p.rapidapi.com"
}

@st.cache_data(ttl=300)
def get_weather(city):
    params = {"q": city, "days": 3, "aqi": "yes", "alerts": "no"}
    r = requests.get(url, headers=headers, params=params)
    return r.json() if r.status_code == 200 else None

# --- Main Logic ---
if st.button("🔍 Get Weather"):
    data = get_weather(city)
    if data:
        loc = data["location"]
        current = data["current"]
        forecast = data["forecast"]["forecastday"]

        condition = current["condition"]["text"]
        emoji = weather_emojis.get(condition, "🌡️")

        st.subheader(f"{emoji} Current Weather in {loc['name']}, {loc['country']}")
        st.image("https:" + current["condition"]["icon"], width=60)

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Condition:** {condition}")
            st.write(f"**Temperature:** {convert_temp(current['temp_c'], unit)}°{unit[0]}")
            st.write(f"**Humidity:** {current['humidity']}%")
        with col2:
            st.write(f"**Wind:** {current['wind_kph']} km/h")
            st.write(f"**Local Time:** {loc['localtime']}")

        # --- Air Quality ---
        if "air_quality" in current:
            aqi = current["air_quality"]
            st.markdown("### 🧪 Air Quality Index (AQI)")
            st.info(f"PM2.5: {aqi['pm2_5']:.2f} | CO: {aqi['co']:.2f} | O3: {aqi['o3']:.2f}")

        # --- Forecast ---
        st.markdown("---")
        st.subheader("📅 3-Day Forecast")

        temps_max, temps_min, days = [], [], []
        for day in forecast:
            d = day["day"]
            date = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%A")
            max_t = convert_temp(d["maxtemp_c"], unit)
            min_t = convert_temp(d["mintemp_c"], unit)
            emoji = weather_emojis.get(d["condition"]["text"], "🌡️")

            with st.expander(f"{emoji} {date}"):
                st.write(f"**Avg Temp:** {convert_temp(d['avgtemp_c'], unit)}°{unit[0]}")
                st.write(f"**Max:** {max_t}° | Min: {min_t}°")
                st.write(f"**Chance of Rain:** {d['daily_chance_of_rain']}%")

            temps_max.append(max_t)
            temps_min.append(min_t)
            days.append(date)

        # --- Temperature Chart ---
        st.markdown("### 📊 Temperature Trend")
        fig, ax = plt.subplots()
        ax.plot(days, temps_max, label="Max Temp", color="tomato", marker="o")
        ax.plot(days, temps_min, label="Min Temp", color="dodgerblue", marker="o")
        ax.set_ylabel(f"Temp (°{unit[0]})")
        ax.set_title("Daily Max & Min Temperatures")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.error("❌ Could not retrieve data. Try again later.")
