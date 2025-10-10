import streamlit as st
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

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
            date = entry["dt_txt"].split(" ")[0]  # only keep YYYY-MM-DD
            temp = entry["main"]["temp"]
            rain = entry.get("rain", {}).get("3h", 0)
            forecast.append({"date": date, "temperature": temp, "rain": rain})

        df = pd.DataFrame(forecast)
        # aggregate: mean temp, total rain per day
        daily_df = df.groupby("date").agg({"temperature": "mean", "rain": "sum"}).reset_index()
        return daily_df

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

                # interactive forecast chart 
                if forecast_df is not None and not forecast_df.empty:
                    st.subheader("📊 5-Day Forecast (Temperature & Rain)")

                    # Interactive dual-axis style: two traces (line + bar)
                    fig = px.bar(
                        forecast_df,
                        x="date",
                        y="rain",
                        labels={"rain": "Rain (mm)", "date": "Date"},
                        opacity=0.5,
                        title=f"5-Day Forecast for {city.title()}",
                    )

                    fig.add_scatter(
                        x=forecast_df["date"],
                        y=forecast_df["temperature"],
                        mode="lines+markers",
                        name="Temperature (°C)",
                        yaxis="y2",
                        line=dict(color="firebrick", width=2),
                        line_shape="spline",
                    )

                    # Add secondary y-axis
                    fig.update_layout(
                        yaxis=dict(title="Rain (mm)", side="left"),
                        yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right"),
                        xaxis=dict(title="Date", tickangle=45),
                        legend=dict(x=0.02, y=0.98),
                        template="plotly_dark",
                        bargap=0.3,
                        margin=dict(l=40, r=40, t=60, b=60),
                        height=500,
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # --- Data Table & Download Section ---
                st.subheader("📋 Forecast Data Table")

                # Format DataFrame for display (optional)
                display_df = forecast_df.copy()
                display_df["date"] = pd.to_datetime(display_df["date"]).dt.strftime("%Y-%m-%d")

                st.dataframe(display_df, use_container_width=True)

                # Convert to CSV
                csv = display_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="⬇️ Download forecast data as CSV",
                    data=csv,
                    file_name=f"{city.lower().replace(' ', '_')}_forecast.csv",
                    mime="text/csv",
                )


            else:
                st.error("Could not fetch weather data. Try another city.")
        else:
            st.warning("Please enter a city name.")


if __name__ == "__main__":
    main()
