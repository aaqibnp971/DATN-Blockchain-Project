# 🎓 DATN: Decentralized Academic Trust Network

Welcome to the **Decentralized Academic Trust Network (DATN)**. This project is a prototype for a secure, blockchain-based ecosystem designed to issue, store, and verify university degrees. By leveraging **Hyperledger Fabric** and **W3C Verifiable Credentials**, this system eliminates academic fraud and provides a seamless verification process for employers.

## 🏗️ Project Architecture

This project consists of three main layers:

1. **Frontend Portals (Python/Streamlit)**
   - `security.py`: The main Role-Based Access web application with separate secure portals for University Admins, Students, and Employers.
   - `dashboard.py`: An alternative prototype demonstrating the UI and cryptographic hashing flow.

2. **Layer 2 SIS-Bridge (Node.js)**
   - `sis_issuer_service.js`: Middleware that queries legacy Student Information Systems (SIS), converts student data into standardized **W3C Verifiable Credentials** (JSON format), and prepares the cryptographic hash for the blockchain.

3. **Layer 1 Blockchain Smart Contract (Go)**
   - `credential_contract.go`: The core Hyperledger Fabric Chaincode. It handles writing degree hashes to the immutable ledger (`IssueCredentialHash`), checking for duplicates (`CredentialExists`), and marking degrees as invalid (`RevokeCredential`).

## 🚀 Getting Started

### Prerequisites
To run all components of this project, you will need to install:
- **Python 3.8+** (for the web portals)
- **Node.js** (for the SIS bridge)
- **Go / Golang** (for the smart contract)

### 1. Web Portal Setup (Python)
First, install the required UI library:
```bash
pip install streamlit
```
To launch the secure interactive portal, run:
```bash
streamlit run security.py
```
*(Passwords - Admin: `admin` | Student: `student` | Employer: `company`)*

### 2. SIS Issuer Service (Node.js)
To test the legacy database extraction and JSON credential generation:
```bash
node sis_issuer_service.js
```

### 3. Blockchain Smart Contract (Go)
To verify the integrity of the Hyperledger Fabric smart contract code:
```bash
go mod tidy
go build
```

## 🔒 Verification Flow (How it works)
1. **Issuance:** The University generates a digital degree (JSON) for a student. A SHA-256 hash of this JSON is permanently anchored to the blockchain.
2. **Storage:** The student receives the JSON file in their Digital Wallet.
3. **Verification:** The student shares the JSON file with an Employer. The Employer uploads it to the portal, which recalculates the hash and checks the blockchain to prove the degree has not been tampered with.

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
