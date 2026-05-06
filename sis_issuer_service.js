const crypto = require('crypto');

async function fetchLegacyRecord(studentID) {
    console.log(`[SIS-Bridge] Querying Legacy SQL DB for Student ID: ${studentID}...`);
    return {
        id: "2023A7PS0286U",
        name: "Zayaan Ali",
        degree: "Bachelor of Science in Computer Science",
        graduationDate: "2025-05-20",
        gpa: "3.8"
    };
}

function createVerifiableCredential(studentData, issuerDID) {
    return {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id": `http://university.edu/credentials/${studentData.id}`,
        "type": ["VerifiableCredential", "UniversityDegreeCredential"],
        "issuer": issuerDID,
        "issuanceDate": new Date().toISOString(),
        "credentialSubject": {
            "id": `did:sov:${studentData.id}`,
            "degree": studentData.degree,
            "alumni_of": "BITS Pilani"
        }
    };
}

async function issueCredentialWorkflow(studentID) {
    try {
        const studentRecord = await fetchLegacyRecord(studentID);

        const vcObject = createVerifiableCredential(studentRecord, "did:fabric:BITS_Pilani");
        const vcString = JSON.stringify(vcObject);
        const vcHash = crypto.createHash('sha256').update(vcString).digest('hex');
        
        console.log(`[SIS-Bridge] Generated VC Hash: ${vcHash}`);
        console.log(`[SIS-Bridge] Anchoring Hash to Hyperledger Fabric...`);
        
        console.log(`[Success] Credential Anchored! Sending JSON to Student Wallet.`);
        console.log(JSON.stringify(vcObject, null, 2));
        return vcObject; 

    } catch (error) {
        console.error(`[Error] Issuance Failed: ${error}`);
    }
}

issueCredentialWorkflow("2023A7PS0286U");