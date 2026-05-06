package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

type SmartContract struct {
	contractapi.Contract
}

type CredentialState struct {
	CredentialHash string `json:"credentialHash"`
	IssuerDID      string `json:"issuerDID"`
	Status         string `json:"status"`
	LastUpdated    string `json:"lastUpdated"`
}

func (s *SmartContract) IssueCredentialHash(ctx contractapi.TransactionContextInterface, credentialHash string, issuerDID string) error {
	
	exists, err := s.CredentialExists(ctx, credentialHash)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the credential hash %s already exists", credentialHash)
	}

	asset := CredentialState{
		CredentialHash: credentialHash,
		IssuerDID:      issuerDID,
		Status:         "VALID",
		LastUpdated:    time.Now().Format(time.RFC3339),
	}
	
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(credentialHash, assetJSON)
}

func (s *SmartContract) RevokeCredential(ctx contractapi.TransactionContextInterface, credentialHash string) error {
	
	assetJSON, err := ctx.GetStub().GetState(credentialHash)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if assetJSON == nil {
		return fmt.Errorf("the credential %s does not exist", credentialHash)
	}

	var asset CredentialState
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return err
	}

	asset.Status = "REVOKED"
	asset.LastUpdated = time.Now().Format(time.RFC3339)

	updatedAssetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(credentialHash, updatedAssetJSON)
}

func (s *SmartContract) CredentialExists(ctx contractapi.TransactionContextInterface, credentialHash string) (bool, error) {
	assetJSON, err := ctx.GetStub().GetState(credentialHash)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}
	return assetJSON != nil, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(new(SmartContract))
	if err != nil {
		fmt.Printf("Error creating DATN chaincode: %s", err.Error())
		return
	}

	if err := chaincode.Start(); err != nil {
		fmt.Printf("Error starting DATN chaincode: %s", err.Error())
	}
}