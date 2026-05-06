import hashlib
import json

def verify_credential(vc_json_file, blockchain_state_mock):
    print("--- Starting Employer Verification Process ---")
    
    try:
        with open(vc_json_file, 'r') as f:
            vc_data = json.load(f)
    except FileNotFoundError:
        print("Error: Credential file not found.")
        return

    vc_string = json.dumps(vc_data, separators=(',', ':'))
    calculated_hash = hashlib.sha256(vc_string.encode('utf-8')).hexdigest()
    
    print(f" Calculated Hash: {calculated_hash}")

    print(" Querying Hyperledger Fabric Ledger for Status...")
    
    chain_record = blockchain_state_mock.get(calculated_hash)

    if not chain_record:
        print(" [FAIL] Verification Failed: Hash not found on ledger (Possible Fake).")
        return

    if chain_record['status'] == 'REVOKED':
        print(f" [FAIL] Verification Failed: Degree was REVOKED on {chain_record['lastUpdated']}.")
    elif chain_record['status'] == 'VALID':
        print(f" [SUCCESS] Degree Verified! Issued by {chain_record['issuerDID']}.")
        print(f" Student Name: {vc_data['credentialSubject']['alumni_of']}") 
    else:
        print(" [WARN] Unknown Status.")

blockchain_ledger = {
    "7c06f65fd47ede797c0e6d14edc21c5651d1b611661edc2928371b6378c89d1b": {
        "status": "VALID", 
        "issuerDID": "did:fabric:BITS_Pilani"
    },
    "e5f6g7h8...": {
        "status": "REVOKED", 
        "lastUpdated": "2025-11-01T10:00:00Z"
    }
}

verify_credential('student_degree.json', blockchain_ledger)