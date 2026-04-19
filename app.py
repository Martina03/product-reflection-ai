import streamlit as st
import pandas as pd
from openai import OpenAI

from prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    REFLECTION_MODES
)
client = OpenAI()

# -----------------------------
# Helper functions
# -----------------------------

def dataframe_to_text(df, max_rows=10):
    """
    Convert a dataframe into a readable text block
    for reflection purposes.
    """
    if df is None or df.empty:
        return "No data provided."

    return df.head(max_rows).to_string(index=False)


# -----------------------------
# Page setup
# -----------------------------

st.set_page_config(
    page_title="Product Reflection",
    layout="centered"
)

st.title("🌱 Product Reflection")
st.caption("A quiet space to reflect on product signals.")

st.divider()

# -----------------------------
# Reflection mode
# -----------------------------

st.subheader("Reflection mode")

reflection_mode = st.selectbox(
    "Choose the context for reflection",
    list(REFLECTION_MODES.keys())
)

st.info(REFLECTION_MODES[reflection_mode])

st.divider()

# -----------------------------
# Inputs
# -----------------------------

# Notes
st.subheader("Product notes")

notes = st.text_area(
    "Paste meeting notes, context, or observations",
    height=200,
    placeholder="What happened this week? What feels unclear?"
)

# Metrics
st.subheader("Metrics")

metrics_file = st.file_uploader(
    "Upload metrics CSV (optional)",
    type=["csv"]
)

metrics_df = None
if metrics_file:
    metrics_df = pd.read_csv(metrics_file)
    st.caption("Preview")
    st.dataframe(metrics_df.head())

# Tickets / qualitative signals
st.subheader("Tickets / Qualitative signals")

tickets_file = st.file_uploader(
    "Upload tickets or feedback CSV (optional)",
    type=["csv"]
)

tickets_df = None
if tickets_file:
    tickets_df = pd.read_csv(tickets_file)
    st.caption("Preview")
    st.dataframe(tickets_df.head())

st.divider()

# -----------------------------
# Reflection generation
# -----------------------------

st.subheader("Reflection")

if st.button("Generate reflection"):
    metrics_text = dataframe_to_text(metrics_df)
    tickets_text = dataframe_to_text(tickets_df)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        reflection_mode=reflection_mode,
        mode_guidance=REFLECTION_MODES[reflection_mode],
        metrics=metrics_text,
        tickets=tickets_text,
        notes=notes or "No notes provided."
    )

    with st.spinner("Reflecting on signals..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

    reflection_text = response.choices[0].message.content

    st.text_area(
        "Reflective narrative",
        reflection_text,
        height=400
    )