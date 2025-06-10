import streamlit as st
import pandas as pd
import io
import google.generativeai as genai

# --- Gemini API Setup ---
GEMINI_API_KEY = "AIzaSyAmZt-Pa31lf6TAZ_8p3S6qT2L8dNi-S1c"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

# --- App Layout ---
st.title("📊 Resource Utilization Plan Generator")
st.write("Provide the details below to generate a downloadable project resource plan.")

# --- User Inputs ---
resources = st.text_area("👥 Enter Resource Names (comma-separated)", placeholder="Alice, Bob, Charlie")
util_percent = st.slider("⚙️ Planned Utilization per Resource (%)", 10, 100, 80, step=5)
num_tasks = st.number_input("🧩 Total Number of Tasks", min_value=1, step=1)

if st.button("Generate Plan"):
    if not resources:
        st.warning("Please enter at least one resource name.")
    else:
        resource_list = [r.strip() for r in resources.split(",")]
        
        # --- Gemini Prompt ---
        prompt = f"""
        Create a task allocation plan for a project using the following data:
        - Resources: {', '.join(resource_list)}
        - Planned Utilization: {util_percent}%
        - Total Tasks: {num_tasks}
        
        Output a table in CSV format with columns: Resource Name, Task Name, Task Number, Planned Utilization (%).
        Distribute tasks proportionally based on utilization.
        """

        response = model.generate_content(prompt)
        csv_data = response.text.strip().split("```")[-2]  # Extract CSV portion
        
        # Convert CSV to DataFrame
        try:
            df = pd.read_csv(io.StringIO(csv_data))
            st.dataframe(df)

            # Download link
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Utilization Plan')
                writer.save()
                st.download_button(
                    label="📥 Download Excel Plan",
                    data=buffer,
                    file_name="resource_utilization_plan.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error("Failed to parse Gemini response. Please try again.")
            st.exception(e)
