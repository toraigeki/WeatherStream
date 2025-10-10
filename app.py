import streamlit as st
import time
import requests

st.set_page_config(page_title="WeatherStream", page_icon="🌤️", layout="centered")

# Load API key from Streamlit secrets
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)
        data = response.json()

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
        st.info(f"Error fetching weather: {e}")
        return None


def main():
    st.title("🌦️ WeatherStream")
    st.write("Get the weather anywhere in the world!")

    city = st.text_input("Enter city name:")

    if st.button("Get Weather"):
        if city:
            with st.spinner("Fetching weather data..."):
                time.sleep(2)
                weather_data = get_weather(city)
            if weather_data:
                # Display in a "card"
                st.markdown(
                    f"""
                    <div style="background-color:#2d2d2d;padding:20px;border-radius:10px;margin-top:20px">
                        <h3 style="text-align:center;">🌍 {weather_data['city']}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(
                    f"""
                    <div style="background-color:#2d2d2d;padding:20px;border-radius:10px;margin-top:20px">
                        <p style="text-align:center;">🌡️ <b>{weather_data['temperature']}°C</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c2.markdown(
                    f"""
                    <div style="background-color:#2d2d2d;padding:20px;border-radius:10px;margin-top:20px">
                        <p style="text-align:center;">☁️ {weather_data['description'].title()}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c3.markdown(
                    f"""
                    <div style="background-color:#2d2d2d;padding:20px;border-radius:10px;margin-top:20px">
                        <p style="text-align:center;">💧 Humidity: {weather_data['humidity']}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c4.markdown(
                    f"""
                    <div style="background-color:#2d2d2d;padding:20px;border-radius:10px;margin-top:20px">
                        <p style="text-align:center;">🌬️ Wind Speed: {weather_data['wind_speed']} m/s</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
            else:
                st.error("Could not fetch weather data. Try another city.")
        else:
            st.warning("Please enter a city name.")


if __name__ == "__main__":
    main()
