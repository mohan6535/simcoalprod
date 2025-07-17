import streamlit as st
import pandas as pd
import random
from datetime import datetime
import plotly.graph_objects as go

# Initialize state
if "trucks" not in st.session_state:
    st.session_state.trucks = [
        {"id": f"T{str(i+1).zfill(2)}", "status": "empty", "progress": 0, "weight": 0.0, "speed": 0, "shovel_id": "SH-1"}
        for i in range(14)
    ]
    st.session_state.logs = []
    st.session_state.shift_id = "WS1"
    st.session_state.shift_incharge = "Incharge A"

# Truck simulation logic
def update_trucks():
    for truck in st.session_state.trucks:
        truck["progress"] += random.uniform(3, 7)
        if truck["progress"] < 10:
            truck["status"] = "loading"
            truck["weight"] = round(random.uniform(5.0, 15.0), 2)
            truck["speed"] = 0
        elif truck["progress"] < 60:
            truck["status"] = "loaded"
            truck["weight"] = 19.59
            truck["speed"] = random.randint(18, 25)
        elif truck["progress"] < 90:
            truck["status"] = "empty"
            truck["weight"] = 0
            truck["speed"] = random.randint(18, 25)
        else:
            truck["progress"] = 0

        st.session_state.logs.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Truck ID": truck["id"],
            "Status": truck["status"],
            "Weight (T)": truck["weight"],
            "Speed (km/h)": truck["speed"],
            "Shovel ID": truck["shovel_id"],
            "Shift ID": st.session_state.shift_id
        })

# Draw truck movement on mine profile
def draw_mine_profile():
    fig = go.Figure()
    colors = {"loading": "orange", "loaded": "green", "empty": "yellow"}
    for i, truck in enumerate(st.session_state.trucks):
        fig.add_trace(go.Scatter(
            x=[truck["progress"]],
            y=[i],
            mode="markers+text",
            marker=dict(size=18, color=colors.get(truck["status"], "gray")),
            text=[truck["id"]],
            textposition="top center"
        ))
    fig.update_layout(title="🛣️ Mine Profile - Truck Movement",
                      xaxis_title="Route Progress (%)",
                      yaxis_title="Truck Lanes",
                      showlegend=False,
                      xaxis=dict(range=[0, 100]),
                      yaxis=dict(range=[-1, 14]),
                      height=500)
    st.plotly_chart(fig, use_container_width=True)

# App UI
st.set_page_config(layout="wide")
st.title("⛏️ Real-Time Coal Mine Simulation - Mine A")

col1, col2 = st.columns(2)
with col1:
    draw_mine_profile()
with col2:
    update_trucks()
    df = pd.DataFrame(st.session_state.logs[-14:])
    st.subheader("📋 Live Truck Data")
    st.dataframe(df, use_container_width=True)

st.markdown("---")

st.header("📊 Shift-wise Reporting")
if st.button("Shift Over"):
    shift_logs = pd.DataFrame([log for log in st.session_state.logs if log["Shift ID"] == st.session_state.shift_id])
    total_qty = shift_logs["Weight (T)"].sum()
    report = pd.DataFrame([{
        "Serial No": 1,
        "Mine Name": "Mine A",
        "Shift ID": st.session_state.shift_id,
        "Total Quantity (T)": round(total_qty, 2),
        "Shift Incharge": st.session_state.shift_incharge,
        "Grade": "W-IV"
    }])
    st.success("✅ Shift Report Generated:")
    st.dataframe(report)
    csv = report.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Report CSV", data=csv, file_name="shift_report.csv")
