import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- Gemini API Setup ---
GEMINI_API_KEY = "AIzaSyAmZt-Pa31lf6TAZ_8p3S6qT2L8dNi-S1c"  # Replace this with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# --- Streamlit UI ---
st.set_page_config(page_title="Resource Utilization Plan", layout="wide")
st.title("📊 Project Resource Utilization Plan Generator")
st.markdown("Upload a task sheet (CSV) and generate a resource-wise hours allocation plan using Gemini AI.")

# --- File Upload ---
uploaded_file = st.file_uploader("📁 Upload Task Sheet (CSV format)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Task Sheet")
    st.dataframe(df)

    required_columns = {"Task", "Assignee", "Estimated Hours"}
    if not required_columns.issubset(df.columns):
        st.error("CSV must contain the following columns: Task, Assignee, Estimated Hours")
    else:
        # --- Prepare CSV data for prompt ---
        tasks_text = df.to_csv(index=False)

        prompt = f"""
        You are a project planner. Below is a CSV of tasks with their assignees and estimated hours:

        {tasks_text}

        Create a Resource Utilization Plan that includes:
        1. A summary table with: Assignee, Total Hours, Task Split-up (Task: Hours)
        2. Proper formatting in markdown for a clean table.

        Ensure that each assignee's total allocated hours are summed correctly.
        """

        # --- Generate Plan with Gemini ---
        if st.button("🧠 Generate Resource Plan"):
            with st.spinner("Generating resource plan using Gemini..."):
                response = model.generate_content(prompt)
                result_text = response.text

                st.subheader("✅ Generated Resource Utilization Plan")
                st.markdown(result_text)

                # --- Optional: Download as CSV ---
                import re
                from io import StringIO

                def markdown_table_to_df(markdown_text):
                    lines = markdown_text.strip().splitlines()
                    lines = [line.strip() for line in lines if "|" in line and not line.startswith("|---")]
                    lines = [line.strip("|").split("|") for line in lines]
                    return pd.DataFrame(lines[1:], columns=[col.strip() for col in lines[0]])

                try:
                    df_out = markdown_table_to_df(result_text)
                    csv = df_out.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download Plan as CSV", csv, "resource_utilization_plan.csv", "text/csv")
                except Exception as e:
                    st.warning("Could not convert markdown to CSV format. Please copy manually if needed.")
                    st.text_area("Raw Output", value=result_text, height=300)
