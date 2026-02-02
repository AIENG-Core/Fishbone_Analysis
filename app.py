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
st.title(" Fishbone RCA AI (Learning System)")
st.caption("AI suggests causes & descriptions. Human edits. System learns on save.")

# --------------------------------------------------
# Incident input
# --------------------------------------------------
incident = st.text_area(
    "📝 Incident Description",
    height=140,
    placeholder="Write your incident..."
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
if "ai" in st.session_state:

    left, right = st.columns([3, 2])

    # ================= LEFT =================
    # Causes + descriptions
    # =======================================
    with left:
        st.subheader("🧠 Root Causes (Editable)")

        for category, items in st.session_state.ai.items():
            st.markdown(f"### {category}")
            st.session_state.final[category] = []

            for item in items:
                cause = item["cause"]

                checked = st.checkbox(
                    cause,
                    value=True,
                    key=f"{category}_{cause}"
                )

                desc = st.text_area(
                    "Description",
                    value=item["description"],
                    key=f"{category}_{cause}_desc"
                )

                if checked:
                    st.session_state.final[category].append({
                        "cause": cause,
                        "description": desc
                    })

            # -------- Manual add dropdown --------
            existing = {i["cause"] for i in st.session_state.final[category]}
            remaining = [c for c in FISHBONE[category] if c not in existing]

            new_cause = st.selectbox(
                f"Add more causes under {category}",
                options=["-- Select --"] + remaining,
                key=f"{category}_add"
            )

            if new_cause != "-- Select --":
                st.session_state.final[category].append({
                    "cause": new_cause,
                    "description": ""
                })

            st.divider()

        # Save & train
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
    # Fishbone diagram
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

            for item in items:
                node_id = f"{category}_{item['cause']}"
                dot.node(node_id, item["cause"])
                dot.edge(node_id, category)

        st.graphviz_chart(dot)

# --------------------------------------------------
# Output preview (optional)
# --------------------------------------------------
if "final" in st.session_state:
    st.subheader("✅ Final RCA Output (Preview)")
    st.json(st.session_state.final)


#just to see if it is updated or not