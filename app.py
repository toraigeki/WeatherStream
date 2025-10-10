import streamlit as st
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="WeatherStream", page_icon="🌤️", layout="centered")

# Load API key from Streamlit secrets
API_KEY = st.secrets["OPENWEATHER_API_KEY"]

# Base URLs
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


# --- Fetch current weather ---
def get_weather(city):
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(CURRENT_URL, params=params)
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


# --- Fetch 5-day / 3-hour forecast ---
def get_forecast(city):
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(FORECAST_URL, params=params)
        data = response.json()

        if data.get("cod") != "200":
            return None

        forecast = []
        for entry in data["list"]:
            date = entry["dt_txt"]
            temp = entry["main"]["temp"]
            rain = entry.get("rain", {}).get("3h", 0)
            forecast.append({"date": date, "temperature": temp, "rain": rain})

        return pd.DataFrame(forecast)

    except Exception as e:
        st.info(f"Error fetching forecast: {e}")
        return None


def main():
    st.title("🌦️ WeatherStream")
    st.write("Get the weather anywhere in the world!")

    city = st.text_input("Enter city name:")

    if st.button("Get Weather"):
        if city:
            with st.spinner("Fetching weather data..."):
                weather_data = get_weather(city)
                forecast_df = get_forecast(city)

            if weather_data:
                # --- Current Weather Cards ---
                st.markdown(
                    f"""
                    <div style="background-color:#2d2d2d;padding:20px;border-radius:10px;
                    display:flex;flex-direction:column;justify-content:center;align-items:center;
                    height:150px;font-size:1.5rem;color:white;">
                        <h2 style="text-align:center;">🌍 {weather_data['city']}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                c1, c2, c3, c4 = st.columns(4)
                card_style = """
                    background-color:#2d2d2d;padding:20px;border-radius:10px;margin-top:20px;
                    display:flex;flex-direction:column;justify-content:center;align-items:center;
                    height:150px;text-align:center;color:white;
                """
                c1.markdown(
                    f"""<div style="{card_style}">🌡️ <b>{weather_data['temperature']}°C</b></div>""",
                    unsafe_allow_html=True,
                )
                c2.markdown(
                    f"""<div style="{card_style}">☁️ {weather_data['description'].title()}</div>""",
                    unsafe_allow_html=True,
                )
                c3.markdown(
                    f"""<div style="{card_style}">💧 Humidity: {weather_data['humidity']}%</div>""",
                    unsafe_allow_html=True,
                )
                c4.markdown(
                    f"""<div style="{card_style}">🌬️ Wind Speed: {weather_data['wind_speed']} m/s</div>""",
                    unsafe_allow_html=True,
                )

                # --- Forecast Chart ---
                if forecast_df is not None and not forecast_df.empty:
                    st.subheader("📈 5-Day Forecast (Temperature & Rain)")

                    fig, ax1 = plt.subplots(figsize=(10, 4))

                    ax1.plot(
                        forecast_df["date"],
                        forecast_df["temperature"],
                        color="tab:red",
                        label="Temperature (°C)",
                        linewidth=2,
                    )
                    ax1.set_ylabel("Temperature (°C)", color="tab:red")
                    ax1.tick_params(axis="y", labelcolor="tab:red")

                    ax2 = ax1.twinx()
                    ax2.bar(
                        forecast_df["date"],
                        forecast_df["rain"],
                        alpha=0.3,
                        color="tab:blue",
                        label="Rain (mm)",
                    )
                    ax2.set_ylabel("Rain (mm)", color="tab:blue")
                    ax2.tick_params(axis="y", labelcolor="tab:blue")

                    plt.xticks(rotation=45)
                    plt.title(f"5-Day Forecast for {city.title()}")
                    fig.tight_layout()

                    st.pyplot(fig)

            else:
                st.error("Could not fetch weather data. Try another city.")
        else:
            st.warning("Please enter a city name.")


if __name__ == "__main__":
    main()
