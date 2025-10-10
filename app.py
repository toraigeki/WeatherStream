import streamlit as st
import requests
import os

st.set_page_config(page_title="WeatherStream", page_icon="🌤️", layout="centered")

# make sure you store your API key as OPENWEATHER_API_KEY = "api_key_here" in your project_folder/.streamlit/secrets.toml file
API_KEY = st.secrets["OPENWEATHER_API_KEY"]

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        # this iss so i can check the returned data and api erros for testig 
        # st.warning(data)
        if data.get("cod") != 200:
            return None
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
    except Exception as e:
        st.info("Error fetching weather:", e)
        return None

def main():
    st.title("🌦️ WeatherStream")

    st.write("Get the weather anywhere in the world!")

    city = st.text_input("Enter city name:", "")

    if st.button("Get Weather"):
        if city:
            weather_data = get_weather(city)
            if weather_data:
                st.subheader(f"Weather in {weather_data['city']}")
                st.write(f"🌡️ Temperature: {weather_data['temperature']}°C")
                st.write(f"☁️ Condition: {weather_data['description'].title()}")
                st.write(f"💧 Humidity: {weather_data['humidity']}%")
                st.write(f"🌬️ Wind Speed: {weather_data['wind_speed']} m/s")
            else:
                st.error("Could not fetch weather data. Try another city.")
        else:
            st.warning("Please enter a city name.")

if __name__ == "__main__":
    main()