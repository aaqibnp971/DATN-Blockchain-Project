import streamlit as st
import json
import hashlib
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="DATN: Academic Trust Network", layout="wide")

# --- MOCK BLOCKCHAIN LEDGER (Shared State) ---
# In a real app, this would query Hyperledger Fabric.
# For the demo, we initialize it with a few valid degrees.
if 'blockchain_ledger' not in st.session_state:
    st.session_state['blockchain_ledger'] = {
        # Valid Hash (Example)
        "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4": {
            "status": "VALID",
            "issuerDID": "did:fabric:BITS_Pilani",
            "timestamp": "2024-01-01T12:00:00Z"
        },
        # Revoked Hash (Example)
        "e5f6g7h8...": {
            "status": "REVOKED",
            "issuerDID": "did:fabric:BITS_Pilani",
            "timestamp": "2025-11-01T10:00:00Z"
        }
    }

# --- HELPER FUNCTIONS ---
def generate_vc(student_id, name, degree, gpa):
    """Simulates Layer 2: SIS-Bridge Logic"""
    vc = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id": f"http://university.edu/credentials/{student_id}",
        "type": ["VerifiableCredential", "UniversityDegreeCredential"],
        "issuer": "did:fabric:BITS_Pilani",
        "issuanceDate": datetime.now().isoformat(),
        "credentialSubject": {
            "id": f"did:sov:{student_id}",
            "name": name,
            "degree": degree,
            "gpa": gpa,
            "alumni_of": "BITS Pilani"
        }
    }
    return vc

def calculate_hash(vc_data):
    """Cryptographic Hashing (SHA-256)"""
    # Use standard separators to ensure consistency
    vc_string = json.dumps(vc_data, separators=(',', ':'))
    return hashlib.sha256(vc_string.encode('utf-8')).hexdigest()

# --- UI LAYOUT ---
st.title("🎓 Decentralized Academic Trust Network (DATN)")
st.markdown("**Phase III Prototype:** Secure On-Chain Verification System")

# Create Tabs for different Stakeholders
tab1, tab2, tab3 = st.tabs(["🏛️ University (Issuer)", "👨‍🎓 Student (Holder)", "🏢 Employer (Verifier)"])

# --- TAB 1: ISSUER (University) ---
with tab1:
    st.header("University Registrar Portal")
    st.info("Role: Issue a new degree credential from the Legacy SIS.")
    
    col1, col2 = st.columns(2)
    with col1:
        s_id = st.text_input("Student ID", value="2023A7PS0286U")
        s_name = st.text_input("Student Name", value="Zayaan Ali")
    with col2:
        s_degree = st.selectbox("Degree Conferred", ["B.E. Computer Science", "B.E. Electrical", "M.Sc. Economics"])
        s_gpa = st.slider("Cumulative GPA", 0.0, 10.0, 8.5)

    if st.button("Issue & Anchor Credential", type="primary"):
        with st.spinner('Connecting to SIS Bridge... Extracting Data...'):
            time.sleep(1) # Simulate network delay
            
            # 1. Generate Credential
            vc_data = generate_vc(s_id, s_name, s_degree, str(s_gpa))
            
            # 2. Hash it
            vc_hash = calculate_hash(vc_data)
            
            # 3. "Write" to Blockchain (Session State)
            st.session_state['blockchain_ledger'][vc_hash] = {
                "status": "VALID",
                "issuerDID": "did:fabric:BITS_Pilani",
                "timestamp": datetime.now().isoformat()
            }
            
            # 4. Success UI
            st.success("Credential Issued Successfully!")
            st.metric(label="Blockchain Transaction ID (Hash)", value=f"{vc_hash[:10]}...{vc_hash[-5:]}")
            
            # 5. Display the JSON for the user to copy
            st.subheader("Generated Verifiable Credential (JSON)")
            st.json(vc_data)
            st.toast("Degree anchored on Hyperledger Fabric!", icon="⛓️")

# --- TAB 2: HOLDER (Student) ---
with tab2:
    st.header("Student Wallet")
    st.info("Role: View and Manage your Credentials.")
    st.markdown("Your wallet contains the signed JSON file. You can download it to share with employers.")
    
    # Just a placeholder to show the concept
    st.image("https://cdn-icons-png.flaticon.com/512/60/60484.png", width=100)
    st.caption("Secure Enclave Storage")

# --- TAB 3: VERIFIER (Employer) ---
with tab3:
    st.header("Employer Verification Portal")
    st.info("Role: Verify a candidate's degree instantly using the Blockchain.")
    
    # Input method
    input_method = st.radio("Input Method", ["Paste JSON", "Upload File"])
    
    vc_input = None
    if input_method == "Paste JSON":
        vc_text = st.text_area("Paste the Credential JSON here:")
        if vc_text:
            try:
                vc_input = json.loads(vc_text)
            except:
                st.error("Invalid JSON format.")
    else:
        uploaded_file = st.file_uploader("Upload Degree.json")
        if uploaded_file is not None:
            vc_input = json.loads(uploaded_file.getvalue())

    if st.button("Verify Credential"):
        if not vc_input:
            st.warning("Please provide a credential first.")
        else:
            with st.spinner('Querying Hyperledger Fabric Ledger...'):
                time.sleep(1.5) # Simulate Blockchain query
                
                # 1. Calculate Hash of provided data
                check_hash = calculate_hash(vc_input)
                st.write(f"**Calculated Hash:** `{check_hash}`")
                
                # 2. Check against Ledger
                record = st.session_state['blockchain_ledger'].get(check_hash)
                
                if record:
                    if record['status'] == 'VALID':
                        st.balloons()
                        st.success("✅ VERIFIED: This degree is AUTHENTIC.")
                        st.write(f"**Issuer:** {record['issuerDID']}")
                        st.write(f"**Anchored Date:** {record['timestamp']}")
                        
                        # Show Data
                        subj = vc_input.get('credentialSubject', {})
                        st.dataframe({
                            "Field": ["Name", "Degree", "GPA", "Alumni Of"],
                            "Value": [subj.get('name'), subj.get('degree'), subj.get('gpa'), subj.get('alumni_of')]
                        })
                    else:
                        st.error(f"❌ REVOKED: This degree was revoked on {record.get('timestamp')}.")
                else:
                    st.error("⚠️ FAKE: No matching record found on the blockchain.")

# --- SIDEBAR: ADMIN CONTROLS ---
with st.sidebar:
    st.header("Network Admin")
    st.markdown("Current Ledger State (Debug View)")
    st.write(f"Total Records: {len(st.session_state['blockchain_ledger'])}")
    if st.checkbox("Show Raw Ledger"):
        st.json(st.session_state['blockchain_ledger'])