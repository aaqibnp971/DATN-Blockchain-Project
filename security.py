import streamlit as st
import json
import hashlib
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="DATN Secure Portal", layout="wide", page_icon="🔐")

# --- SESSION STATE INITIALIZATION ---
if 'blockchain_ledger' not in st.session_state:
    st.session_state['blockchain_ledger'] = {}

if 'student_db' not in st.session_state:
    st.session_state['student_db'] = {}

if 'employer_registry' not in st.session_state:
    st.session_state['employer_registry'] = {"Apple Inc": "APPROVED"} 

if 'logged_in_uni' not in st.session_state: st.session_state['logged_in_uni'] = False
if 'logged_in_student' not in st.session_state: st.session_state['logged_in_student'] = False
if 'logged_in_emp' not in st.session_state: st.session_state['logged_in_emp'] = False
if 'current_student_id' not in st.session_state: st.session_state['current_student_id'] = None

# --- HELPER FUNCTIONS ---
def hash_data(data):
    """Calculates SHA-256 hash of the JSON data"""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def login_block(role, password_key, success_state):
    """Reusable Login Component"""
    with st.container(border=True):
        st.markdown(f"### 🔒 {role} Login")
        pwd = st.text_input("Enter Password", type="password", key=f"pwd_{role}")
        if st.button(f"Login as {role}"):
            if pwd == password_key:
                st.session_state[success_state] = True
                st.rerun()
            else:
                st.error("Incorrect Password")

# --- MAIN UI ---
st.title("🎓 DATN: Secure Academic Portal")
st.markdown("**Phase III Demo:** Authenticated Role-Based Access")

tab1, tab2, tab3 = st.tabs(["🏛️ University Admin", "👨‍🎓 Student Portal", "🏢 Employer Access"])

# ==========================================
# TAB 1: UNIVERSITY (Pass: admin)
# ==========================================
with tab1:
    if not st.session_state['logged_in_uni']:
        login_block("University Admin", "admin", "logged_in_uni")
    else:
        st.success("Authenticated: BITS Pilani Registrar")
        if st.button("Logout (Uni)"):
            st.session_state['logged_in_uni'] = False
            st.rerun()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("1. Issue New Degree")
            with st.form("issue_form"):
                s_id = st.text_input("Student ID", value="2023A7PS0286U")
                s_name = st.text_input("Student Name", value="Zayaan Ali")
                s_degree = st.selectbox("Degree", ["B.E. Computer Science", "B.E. Electrical", "M.Sc. Economics"])
                s_gpa = st.slider("GPA", 0.0, 10.0, 9.0)
                
                submitted = st.form_submit_button("Issue & Anchor")
                
                if submitted:
                    # Create Asset
                    credential = {
                        "id": s_id,
                        "name": s_name,
                        "degree": s_degree,
                        "gpa": str(s_gpa),
                        "issuer": "BITS Pilani",
                        "date": datetime.now().isoformat()
                    }
                    
                    # Hash and Anchor
                    c_hash = hash_data(credential)
                    st.session_state['blockchain_ledger'][c_hash] = {
                        "status": "VALID",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Save to Student DB
                    if s_id not in st.session_state['student_db']:
                        st.session_state['student_db'][s_id] = []
                    st.session_state['student_db'][s_id].append(credential)
                    
                    st.success(f"Degree Issued! Hash: {c_hash[:10]}...")
                    
                    # --- NEW: Display JSON for Copying ---
                    st.markdown("**Generated JSON (Copy this for verification):**")
                    st.code(json.dumps(credential, indent=2), language='json')
                    # -------------------------------------

        with col2:
            st.subheader("2. Employer Approvals")
            st.info("Approve companies to access the verification API.")
            
            new_req = st.text_input("Add New Company Request", placeholder="e.g. Google")
            if st.button("Approve Request"):
                st.session_state['employer_registry'][new_req] = "APPROVED"
                st.success(f"{new_req} approved!")
            
            st.write("---")
            st.write("**Authorized Employers:**")
            st.json(st.session_state['employer_registry'])

# ==========================================
# TAB 2: STUDENT (Pass: student)
# ==========================================
with tab2:
    if not st.session_state['logged_in_student']:
        login_block("Student Portal", "student", "logged_in_student")
    else:
        # Student ID Lookup
        if st.session_state['current_student_id'] is None:
            st.subheader("Identify Yourself")
            sid_input = st.text_input("Enter your Student ID to fetch records:")
            if st.button("Fetch My Records"):
                if sid_input in st.session_state['student_db']:
                    st.session_state['current_student_id'] = sid_input
                    st.rerun()
                else:
                    st.error("ID not found or no degrees issued yet.")
        else:
            # Student Wallet View
            my_id = st.session_state['current_student_id']
            st.success(f"Welcome, Student {my_id}")
            if st.button("Logout (Student)"):
                st.session_state['logged_in_student'] = False
                st.session_state['current_student_id'] = None
                st.rerun()
            
            st.divider()
            st.markdown("### 📂 My Digital Wallet")
            
            my_docs = st.session_state['student_db'][my_id]
            for i, doc in enumerate(my_docs):
                with st.expander(f"📄 {doc['degree']} (Issued: {doc['date'][:10]})"):
                    st.json(doc)
                    st.download_button(
                        f"⬇️ Download Degree #{i+1}",
                        data=json.dumps(doc),
                        file_name=f"degree_{my_id}_{i}.json",
                        mime="application/json"
                    )

# ==========================================
# TAB 3: EMPLOYER (Pass: company)
# ==========================================
with tab3:
    if not st.session_state['logged_in_emp']:
        login_block("Employer Portal", "company", "logged_in_emp")
    else:
        st.success("Authenticated: Recruitment Portal")
        if st.button("Logout (Employer)"):
            st.session_state['logged_in_emp'] = False
            st.rerun()
        
        # 1. Authorization Check
        st.subheader("1. System Authorization")
        company_name = st.selectbox("Select Your Organization", ["Apple Inc", "Google", "Microsoft", "Unknown Startup"])
        
        status = st.session_state['employer_registry'].get(company_name, "DENIED")
        
        if status == "DENIED":
            st.error("🚫 ACCESS DENIED. Your company is not authorized by the University Consortium.")
            st.warning("Please contact the University Admin (Tab 1) to request approval.")
        else:
            st.success(f"✅ ACCESS GRANTED. Welcome, {company_name}.")
            
            st.divider()
            st.subheader("2. Credential Verification")
            st.info("Verify a candidate's credentials against the Blockchain.")

            # --- UPDATED INPUT METHOD ---
            input_method = st.radio("Select Input Method:", ["Paste JSON Text", "Upload JSON File"], horizontal=True)
            
            data_to_verify = None
            
            if input_method == "Paste JSON Text":
                json_text = st.text_area("Paste the Credential JSON here:")
                if json_text:
                    try:
                        data_to_verify = json.loads(json_text)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format.")
            else:
                uploaded_file = st.file_uploader("Upload Degree JSON")
                if uploaded_file:
                    data_to_verify = json.loads(uploaded_file.getvalue())

            # Verification Button
            if st.button("Verify Integrity"):
                if data_to_verify:
                    check_hash = hash_data(data_to_verify)
                    record = st.session_state['blockchain_ledger'].get(check_hash)
                    
                    if record and record['status'] == "VALID":
                        st.balloons()
                        st.success("✅ DEGREE VERIFIED: Authentic & Untampered")
                        st.write(f"**Timestamp:** {record['timestamp']}")
                        st.json(data_to_verify) # Show the valid data
                    else:
                        st.error("❌ FRAUD DETECTED: No matching hash on ledger.")
                else:
                    st.warning("Please provide JSON data first.")