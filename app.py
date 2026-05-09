import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.title("🏢 Leave Management System")

if "user_id" not in st.session_state:
    menu = st.sidebar.selectbox("Menu", ["Register", "Login"])
else:
    menu = st.sidebar.selectbox(
        "Menu",
        ["Apply Leave", "View Leaves", "Admin Panel", "Dashboard"]
    )
#------------------ REGISTER ----------------
if menu == "Register":
    st.subheader("Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        data = {
            "name": name,
            "email": email,
            "password": password
        }

        res = requests.post(f"{BASE_URL}/register", json=data)

        # 🔍 ADD THESE TWO LINES
        st.write("Status:", res.status_code)
        st.write("Response:", res.text)

        if res.status_code == 200:
            st.success("Registered Successfully")
        else:
            st.error("Registration Failed")
#-------------------LOGIN----------------
elif menu == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        data = {
            "email": email,
            "password": password
        }

        res = requests.post(f"{BASE_URL}/login", json=data)

        if res.status_code == 200:
            st.success("Login successful")

            # ✅ STORE USER ID
            st.session_state["user_id"] = res.json()["user_id"]

        else:
            st.error(res.text)
#-----------------DSHboard--------------            
elif menu == "Dashboard":
    st.title("📊 Leave Management Dashboard")

    res = requests.get(f"{BASE_URL}/leaves")
    data = res.json()

    if not data:
        st.warning("No leave data available")
        st.stop()

    # -----------------------------
    # 📊 CALCULATIONS
    # -----------------------------
    total = len(data)
    pending = len([l for l in data if l["status"] == "Pending"])
    approved = len([l for l in data if l["status"] == "Approved"])
    rejected = len([l for l in data if l["status"] == "Rejected"])

    # -----------------------------
    # 🎯 METRICS (TOP CARDS)
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Leaves", total)
    col2.metric("Pending", pending)
    col3.metric("Approved", approved)
    col4.metric("Rejected", rejected)

    st.divider()

   
    # 📋 RECENT LEAVES TABLE
    # -----------------------------
    import pandas as pd

    df = pd.DataFrame(data)

    st.subheader("📋 Recent Leave Requests")
    st.dataframe(df.tail(5))

# ---------------- ADD EMPLOYEE ----------------
if menu == "Add Employee":
    st.subheader("Add Employee")

    name = st.text_input("Name")
    email = st.text_input("Email")

    if st.button("Add"):
        data = {
            "name": name,
            "email": email
        }

        res = requests.post(f"{BASE_URL}/employee/", json=data)

        if res.status_code == 200:
            st.success(res.json())
        else:
            st.error(res.text)

# ---------------- APPLY LEAVE ----------------
elif menu == "Apply Leave":
    st.subheader("Apply Leave")

    emp_id = st.session_state.get("user_id")

    if not emp_id:
        st.warning("Please login first")
        st.stop()

    leave_type = st.text_input("Leave Type")
    start = st.date_input("Start Date")
    end = st.date_input("End Date")
    reason = st.text_input("Reason")

    if st.button("Apply"):
        data = {
            "employee_id": emp_id,
            "leave_type": leave_type,
            "start_date": start.strftime("%Y-%m-%d"),   
            "end_date": end.strftime("%Y-%m-%d"),       
            "reason": reason
        }

        res = requests.post(f"{BASE_URL}/apply-leave", json=data)

        # 🔍 DEBUG OUTPUT
        st.write("Status:", res.status_code)
        st.write("Response:", res.text)

        if res.status_code == 200:
            st.success("Leave Applied Successfully")
        else:
            st.error("Error applying leave")
# ---------------- VIEW LEAVES ----------------
elif menu == "View Leaves":
    st.subheader("All Leaves")

    res = requests.get(f"{BASE_URL}/leaves/")
    leaves = res.json()

    for l in leaves:
        st.write(l)

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Approve {l['id']}", key=f"ap_{l['id']}"):
                requests.put(f"{BASE_URL}/approve/{l['id']}")
                st.success("Approved")

        with col2:
            if st.button(f"Reject {l['id']}", key=f"re_{l['id']}"):
                requests.put(f"{BASE_URL}/reject/{l['id']}")
                st.error("Rejected")
#------------------ ADMIN PANEL ----------------
elif menu == "Admin Panel":
    st.subheader("Admin Panel")

    res = requests.get(f"{BASE_URL}/leaves")
    leaves = res.json()

    import pandas as pd
    df = pd.DataFrame(leaves)

    st.dataframe(df)

    for l in leaves:
        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Approve {l['id']}"):
                requests.put(f"{BASE_URL}/approve/{l['id']}")
                st.success("Approved")
                st.rerun()

        with col2:
            if st.button(f"Reject {l['id']}"):
                requests.put(f"{BASE_URL}/reject/{l['id']}")
                st.error("Rejected")
                st.rerun()
#------------------------LOGOUT-------------
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.success("Logged out")
    st.rerun()                