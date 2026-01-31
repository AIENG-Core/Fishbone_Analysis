import streamlit as st
import asyncio
from ml.inference import analyze
from ml.training import train

st.set_page_config(layout="wide")
st.title(" Fishbone RCA AI (Learning System)")

incident = st.text_area(
    "Incident Description",
    height=140,
    placeholder="Flammable liquid leaked from a storage vessel..."
)

if st.button("Generate Fishbone"):
    st.session_state.ai = asyncio.run(analyze(incident))
    st.session_state.final = {}

if "ai" in st.session_state:
    for cat, items in st.session_state.ai.items():
        st.subheader(cat)
        st.session_state.final[cat] = []

        for item in items:
            checked = st.checkbox(item["cause"], value=True)
            desc = st.text_area(
                "Description",
                value=item["description"],
                key=f"{cat}_{item['cause']}"
            )

            if checked:
                st.session_state.final[cat].append(item["cause"])

    if st.button("Save RCA & Train"):
        train(st.session_state.ai, st.session_state.final)
        st.success("Saved. Model learned from this RCA.")
