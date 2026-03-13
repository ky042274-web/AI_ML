import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import requests
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# ---------------- Page Config ----------------
st.set_page_config(page_title="Flight Travel Planner", layout="wide")

# ---------------- Background & Text Style ----------------
page_style = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("https://cdn.pixabay.com/photo/2021/12/02/02/25/fly-6839472_640.jpg");
background-size: cover;
background-position: center;
}

.dark-box{
background-color: rgba(0,0,0,0.80);
padding:20px;
border-radius:12px;
margin-bottom:15px;
color:white;
}

h1{
color:#FFD700;
font-weight:bold;
}

h3{
color:#00FFFF;
font-weight:bold;
}

label{
color:white !important;
font-weight:bold;
}

.stButton>button{
background-color:#FF4B4B;
color:white;
font-weight:bold;
border-radius:8px;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# ---------------- App Title ----------------
st.markdown("""
<div class="dark-box">
<h1>✈ Flight Price Analysis & Travel Planner</h1>
</div>
""", unsafe_allow_html=True)

# ---------------- Columns: Upload Dataset & Flight Arrival Time ----------------
col_upload, col_arrival = st.columns(2)

with col_upload:
    st.markdown("<div class='dark-box'><h3>📂 Upload Flight Dataset</h3></div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.markdown("<div class='dark-box'><h3>📊 Dataset Preview</h3></div>", unsafe_allow_html=True)
        st.dataframe(df.head())

        if "airline" in df.columns and "price" in df.columns:
            st.markdown("<div class='dark-box'><h3>✈ Airline vs Average Price</h3></div>", unsafe_allow_html=True)
            airline_avg = df.groupby("airline")["price"].mean()
            fig, ax = plt.subplots()
            airline_avg.plot(kind="bar", color="orange", ax=ax)
            st.pyplot(fig)

        if "stops" in df.columns:
            st.markdown("<div class='dark-box'><h3>🛑 Stops vs Price</h3></div>", unsafe_allow_html=True)
            fig2, ax2 = plt.subplots()
            sns.boxplot(x="stops", y="price", data=df, ax=ax2)
            st.pyplot(fig2)

        if "duration" in df.columns:
            st.markdown("<div class='dark-box'><h3>⏳ Duration vs Price</h3></div>", unsafe_allow_html=True)
            fig3, ax3 = plt.subplots()
            sns.scatterplot(x="duration", y="price", data=df)
            st.pyplot(fig3)

        if "days_left" in df.columns:
            st.markdown("<div class='dark-box'><h3>🔮 Ticket Price Prediction</h3></div>", unsafe_allow_html=True)
            X = df[["days_left"]]
            y = df["price"]
            model = LinearRegression()
            model.fit(X, y)

            days = st.slider("Days before departure", 1, 60, 10)
            prediction = model.predict(np.array([[days]]))
            st.success(f"💰 Estimated Ticket Price: ₹ {int(prediction[0])}")

# ---------------- Arrival Time ----------------
with col_arrival:
    st.markdown("<div class='dark-box'><h3>🕑 Flight Arrival Time Calculator</h3></div>", unsafe_allow_html=True)

    departure_time = st.time_input("Departure Time")
    duration = st.number_input("Flight Duration (hours)", 1, 24, 2)

    if st.button("Calculate Arrival Time"):
        departure_datetime = datetime.combine(datetime.today(), departure_time)
        arrival = departure_datetime + timedelta(hours=duration)
        st.success(f"🛬 Estimated Arrival Time: {arrival.strftime('%H:%M')}")

# ---------------- Weather & Route ----------------
col_weather, col_route = st.columns(2)

with col_weather:
    st.markdown("<div class='dark-box'><h3>🌍 Global Temperature Checker</h3></div>", unsafe_allow_html=True)

    city = st.text_input("Enter City Name")
    API_KEY = "YOUR_API_KEY"

    if st.button("Check Weather"):

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": API_KEY, "units": "metric"}

        response = requests.get(url, params=params)

        if response.status_code == 200:

            data = response.json()

            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            country = data["sys"]["country"]

            st.success(f"{city}, {country}")
            st.write(f"Temperature: {temp} °C")
            st.write(f"Weather: {weather}")

        else:
            st.error("City not found")

# ---------------- Route Selection ----------------
with col_route:

    st.markdown("<div class='dark-box'><h3>✈ Select Flight Route</h3></div>", unsafe_allow_html=True)

    cities = ["Delhi","Mumbai","Lucknow","Bangalore","Hyderabad","Chennai","Kolkata"]

    source = st.selectbox("Departure City", cities)
    destination = st.selectbox("Destination City", cities)

    st.markdown("<div class='dark-box'><h3>👤 Passenger Details</h3></div>", unsafe_allow_html=True)

    passenger_name = st.text_input("Passenger Name", "Komal")
    travel_date = st.date_input("Travel Date")

    ticket_type = st.selectbox("🚨 Emergency Ticket Type",
                               ["Normal",
                                "Medical Emergency",
                                "Family Emergency",
                                "Business Emergency"])

# ---------------- Smart Price Prediction ----------------
st.markdown("<div class='dark-box'><h3>🧠 Smart Ticket Price Prediction</h3></div>", unsafe_allow_html=True)

route_prices = {
    ("Delhi","Mumbai"):7000,
    ("Delhi","Bangalore"):9000,
    ("Delhi","Lucknow"):4000,
    ("Mumbai","Bangalore"):8000,
    ("Lucknow","Hyderabad"):7500,
    ("Chennai","Kolkata"):8500
}

base_price = route_prices.get((source,destination),6500)

days_before = (travel_date - datetime.today().date()).days

if days_before < 1:
    days_before = 1

predicted_price = base_price + (20*(30-days_before))

if "Emergency" in ticket_type:
    predicted_price += 4000

# ---------------- Seat Availability ----------------
total_seats = 120
booked_seats = np.random.randint(70,120)
available_seats = total_seats - booked_seats

st.info(f"💰 Predicted Ticket Price: ₹ {int(predicted_price)}")

if available_seats > 0:
    st.success(f"🟢 Seats Available: {available_seats}")
else:
    st.error("❌ No Seats Available")

# ---------------- Booking ----------------
if st.button("✈ Book Flight Ticket"):

    if available_seats > 0:

        confirmation = np.random.randint(2,10)

        st.markdown(f"""
        <div class="dark-box">
        <h3>🎟 Ticket Confirmed</h3>

        Passenger: {passenger_name}<br>
        Route: {source} ➝ {destination}<br>
        Travel Date: {travel_date}<br>

        <b style="color:#FFD700;">Ticket Price: ₹ {int(predicted_price)}</b><br>
        <b style="color:#00FFFF;">Seats Left: {available_seats-1}</b><br>
        Confirmation Time: {confirmation} minutes

        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("Flight Full. Choose another date.")

# ---------------- Security Check ----------------
st.markdown("<div class='dark-box'><h3>🛂 Airport Security Document Check</h3></div>", unsafe_allow_html=True)

password = st.text_input("Enter Security Officer Password", type="password")

if password == "airport123":

    st.markdown("""
    <div class="dark-box">
    Passport (International Flights)<br>
    Aadhaar Card / Driving License<br>
    Flight Ticket<br>
    Boarding Pass<br><br>

    Airport Security Checks<br>
    Baggage scanning<br>
    Identity verification<br>
    Boarding gate check<br>
    Immigration
    </div>
    """, unsafe_allow_html=True)



