import streamlit as st
import asyncio
import graphviz

from ml.inference import analyze
from ml.training import train
from ml.constants import FISHBONE

# --------------------------------------------------
# HIERARCHY OF CONTROLS MAPPING
# --------------------------------------------------
CONTROL_TYPE = {
    "People": "Administrative Control",
    "Process": "Engineering Control",
    "Material": "Administrative Control",
    "Measurement": "Administrative Control",
    "Equipment": "Engineering Control",
    "Environment": "Administrative Control"
}

# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("🐟 Fishbone RCA AI (Learning System)")
st.caption(
    "AI suggests causes & descriptions. "
    "Categories are mapped to Hierarchy of Controls. "
    "System learns on save."
)

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
if "ai" in st.session_state:

    left, right = st.columns([3, 2])

    # ================= LEFT =================
    # Causes + descriptions + Hierarchy label
    # =======================================
    with left:
        st.subheader("🧠 Root Causes (Editable)")

        for category, items in st.session_state.ai.items():

            st.markdown(
                f"### {category} — **{CONTROL_TYPE[category]}**"
            )

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
            st.success(
                "RCA saved. Model learned from this incident."
            )

    # ================= RIGHT =================
    # Fishbone diagram + Summary Panel
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

            dot.node(
                category,
                f"{category}\n({CONTROL_TYPE[category]})"
            )
            dot.edge(category, "Effect")

            for item in items:
                node_id = f"{category}_{item['cause']}"
                dot.node(node_id, item["cause"])
                dot.edge(node_id, category)

        st.graphviz_chart(dot)

        # --------------------------------------------------
        # NEW: Hierarchy of Controls Summary Panel
        # --------------------------------------------------
        st.subheader("🛡️ Hierarchy of Controls Summary")

        engineering = []
        administrative = []

        for category, items in st.session_state.final.items():
            for item in items:
                if CONTROL_TYPE[category] == "Engineering Control":
                    engineering.append(f"- **{category}**: {item['cause']}")
                else:
                    administrative.append(f"- **{category}**: {item['cause']}")

        st.markdown("### 🔧 Engineering Controls")
        if engineering:
            st.markdown("\n".join(engineering))
        else:
            st.info("No engineering controls selected yet.")

        st.markdown("### 📋 Administrative Controls")
        if administrative:
            st.markdown("\n".join(administrative))
        else:
            st.info("No administrative controls selected yet.")

# --------------------------------------------------
# Output preview (optional)
# --------------------------------------------------
if "final" in st.session_state:
    st.subheader("✅ Final RCA Output (Preview)")
    st.json(st.session_state.final)
