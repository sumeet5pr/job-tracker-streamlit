import streamlit as st
import pandas as pd
import os
from datetime import datetime

CSV_FILE = "portal_job_tracker.csv"

# Load or initialize data
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["Portal Name", "Portal Link", "Company Name", "Role", "Status", "Notes", "Last Updated"])

st.set_page_config(layout="wide", page_title="Job Application OS")

# --- HEADER & SIDEBAR ---
st.title("🎯 Job Application OS")

st.sidebar.header("📄 Resume & Assets")
resume_link = st.sidebar.text_input("Drive/Cloud Link to Resume")
if resume_link:
    st.sidebar.markdown(f"[**🔗 Open Active Resume**]({resume_link})")

st.sidebar.markdown("---")
st.sidebar.header("➕ Quick Add")

with st.sidebar.form("add_form", clear_on_submit=True):
    p_name = st.text_input("Portal Name (e.g., Workday)")
    p_link = st.text_input("Portal URL")
    c_name = st.text_input("Company Name")
    role = st.text_input("Role (e.g., Cyber Security Intern)", value="Cyber Security Intern")
    status = st.selectbox("Status", ["To Apply", "Applied", "Assessment", "Interviewing", "Offer", "Rejected"])
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Add Application")

    if submitted and p_name and c_name:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_row = pd.DataFrame([[p_name, p_link, c_name, role, status, notes, timestamp]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success(f"Added {c_name}!")
        st.rerun()

# --- MAIN INTERFACE (TABS) ---
if df.empty:
    st.info("System is empty. Use the sidebar to add entries or upload a CSV in the Data Manager tab.")
else:
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🌐 Portal Tracker", "⚙️ Data Manager"])

    # TAB 1: DASHBOARD
    with tab1:
        st.subheader("Application Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Applications", len(df))
        col2.metric("Active (Applied/Assessment)", len(df[df["Status"].isin(["Applied", "Assessment"])]))
        col3.metric("Interviews", len(df[df["Status"] == "Interviewing"]))
        col4.metric("Offers", len(df[df["Status"] == "Offer"]))

        st.markdown("---")
        st.subheader("Recent Activity")
        st.dataframe(df.sort_values(by="Last Updated", ascending=False).head(5), use_container_width=True)

    # TAB 2: PORTAL TRACKER
    with tab2:
        unique_portals = df["Portal Name"].unique()
        st.write(f"Tracking **{len(unique_portals)}** active portals.")
        
        for portal in unique_portals:
            portal_data = df[df["Portal Name"] == portal]
            link = portal_data["Portal Link"].iloc[0] if not portal_data["Portal Link"].isna().all() else "#"
            
            with st.expander(f"🌐 {portal} ({len(portal_data)} Apps)", expanded=False):
                st.markdown(f"**Login:** [{link}]({link})")
                
                # Editable dataframe
                edit_cols = ["Company Name", "Role", "Status", "Notes"]
                edited_df = st.data_editor(
                    portal_data[edit_cols], 
                    num_rows="dynamic", 
                    use_container_width=True, 
                    key=f"ed_{portal}"
                )
                
                if st.button(f"Save {portal} Updates", key=f"btn_{portal}"):
                    # Drop old portal rows, append new ones, update timestamp
                    df = df[df["Portal Name"] != portal]
                    edited_df["Portal Name"] = portal
                    edited_df["Portal Link"] = link
                    edited_df["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # Reorder columns to match original
                    edited_df = edited_df[df.columns]
                    df = pd.concat([df, edited_df], ignore_index=True)
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Changes saved!")
                    st.rerun()

    # TAB 3: DATA MANAGER (Bulk actions for your 35 links)
    with tab3:
        st.subheader("Bulk Operations")
        st.markdown("Download your current tracker, edit it in Excel to quickly add your 35 portals, and re-upload it.")
        
        # Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Current Data (CSV)", data=csv, file_name="job_tracker_backup.csv", mime="text/csv")
        
        # Upload
        uploaded_file = st.file_uploader("⬆️ Upload Updated CSV", type=["csv"])
        if uploaded_file is not None:
            if st.button("Overwrite Database with Upload"):
                new_df = pd.read_csv(uploaded_file)
                new_df.to_csv(CSV_FILE, index=False)
                st.success("Database overwritten successfully!")
                st.rerun()