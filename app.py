#app.py
import streamlit as st
import asyncio
import graphviz

from ml.inference import analyze
from ml.training import train
from ml.constants import FISHBONE


# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("🐟 Fishbone RCA AI (Learning System)")
st.caption(
    "AI suggests causes & descriptions. "
    "Edit selections and save to train the system."
)

# --------------------------------------------------
# Initialize session state
# --------------------------------------------------
if "ai" not in st.session_state:
    st.session_state.ai = None

if "final" not in st.session_state:
    st.session_state.final = {}


# --------------------------------------------------
# Incident input
# --------------------------------------------------
incident = st.text_area(
    "📝 Incident Description",
    height=140,
    placeholder="Flammable liquid leaked from a storage vessel..."
)

# --------------------------------------------------
# Generate AI output
# --------------------------------------------------
if st.button("⚡ Generate Fishbone") and incident.strip():
    st.session_state.ai = asyncio.run(analyze(incident))
    st.session_state.final = {}


# --------------------------------------------------
# Display results
# --------------------------------------------------
if st.session_state.ai:

    left, right = st.columns([3, 2])

    # ================= LEFT =================
    # Editable causes
    # =======================================
    with left:
        st.subheader("🧠 Root Causes (Editable)")

        for category, items in st.session_state.ai.items():

            st.markdown(f"### {category}")

            updated_items = []

            for i, item in enumerate(items):
                cause = item["cause"]

                # ✅ UNIQUE KEYS using index
                checked = st.checkbox(
                    cause,
                    value=True,
                    key=f"{category}_chk_{i}"
                )

                desc = st.text_area(
                    "Description",
                    value=item["description"],
                    key=f"{category}_desc_{i}"
                )

                if checked:
                    updated_items.append({
                        "cause": cause,
                        "description": desc
                    })

            # -------- Manual add dropdown --------
            existing = {i["cause"] for i in updated_items}
            remaining = [c for c in FISHBONE[category] if c not in existing]

            new_cause = st.selectbox(
                f"Add more causes under {category}",
                options=["-- Select --"] + remaining,
                key=f"{category}_add"
            )

            if new_cause != "-- Select --":
                updated_items.append({
                    "cause": new_cause,
                    "description": ""
                })

            # Save updated category state
            st.session_state.final[category] = updated_items

            st.divider()

        # -------- Save & Train --------
        if st.button("💾 Save RCA & Train Model"):
            train(
                st.session_state.ai,
                {
                    cat: [i["cause"] for i in items]
                    for cat, items in st.session_state.final.items()
                }
            )
            st.success("RCA saved. Model learned from this incident.")


    # ================= RIGHT =================
    # Fishbone Diagram
    # ========================================
    with right:
        st.subheader("📊 Fishbone Diagram")

        dot = graphviz.Digraph(
            graph_attr={"rankdir": "LR"},
            node_attr={"shape": "box"}
        )

        dot.node("Effect", "Incident")

        for category, items in st.session_state.final.items():
            if not items:
                continue

            dot.node(category, category)
            dot.edge(category, "Effect")

            for i, item in enumerate(items):
                node_id = f"{category}_{i}"
                dot.node(node_id, item["cause"])
                dot.edge(node_id, category)

        st.graphviz_chart(dot)


# --------------------------------------------------
# Output preview
# --------------------------------------------------
if st.session_state.final:
    st.subheader("✅ Final RCA Output (Preview)")
    st.json(st.session_state.final)
