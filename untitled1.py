# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 18:17:30 2022

@author: xyz_a
"""
import json

print("Welcome to the pilot, if you haven't already, \
run the Offshift Docker container, and then \
open a new command line and navigate to the folder containing the input JSONs\n")


print("\nRun the following command to generate the first user's public and private keys\n\ncurl localhost:10000/keys")
user1 = input("Paste the output of the function here and press enter: ")
user1 = json.loads(user1)

singleSig = open("./singleSig.json")
singleSig = json.load(singleSig)

singleSig["PubKey"] = user1["PublicKey"]
singleSig["PrivateKey"] = int(user1["PrivateKey"])

with open("./singleSig.json", "w") as fileSingleSig:
    json.dump(singleSig, fileSingleSig , sort_keys=True, indent=3)
    
print("\nRun the following command to generate the first user's Schnorr signature\n\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@singleSig.json\" localhost:10000/singleSig\n")
user1Schnorr = input("Paste the output of the function here and press enter: ")
user1Schnorr = json.loads(user1Schnorr)

generateCommitment = open('./generateCommitment.json')
generateCommitment = json.load(generateCommitment)

generateCommitment["recipientPubKey"] = user1["PublicKey"]

amountInput = input("Enter the amount of test XFT you wish to deposit (must be a non-negative integer): ")
amountInput = int(amountInput)
generateCommitment["amount"] = amountInput * 10**18

with open("./generateCommitment.json", "w") as fileGenerateCommitment:
    json.dump(generateCommitment, fileGenerateCommitment , sort_keys=True, indent=3)
    
print("\nRun the following command to generate the Pedersen Commitment corresponding to User 1's upcoming deposit\n\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@generateCommitment.json\" localhost:10000/generateCommitment")

pedersenCommitment = input("Paste the output of the generateCommitment function here: ")
pedersenCommitment = json.loads(pedersenCommitment)

approve = open("./approve.json")
approve = json.load(approve)

approvalAmount = float(input("Input the number of XFT test tokens you wish to approve for deposit (must be greater than or equal to the number of tokens in the commitment): "))
approvalAmount = int(max(amountInput,approvalAmount) * 10**18)
    
senderPrivateKey = input("If approving spend from your own wallet address, enter its private key here, otherwise, press enter to use the default address: ")

if len(senderPrivateKey) == 64:
    approve["senderPrivateKey"] = senderPrivateKey
    print("Proceeding with user-provided private key")

approve["amount"] = approvalAmount

with open("./approve.json", "w") as fileApprove:
    json.dump(approve, fileApprove, sort_keys=True, indent=3)

print("\nRun the following command to approve tokens for deposit \n\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@approve.json\" localhost:10000/approve")

approvalTransaction = input("Enter the output of the approval transaction here: ")
approvalTransaction = json.loads(approvalTransaction)

print("\nTransaction receipt for token approval:\n https://goerli.etherscan.io/tx/" + approvalTransaction["tx"])

deposit = open("./deposit.json")
deposit = json.load(deposit)

deposit["senderPrivateKey"] = approve["senderPrivateKey"]
deposit["commitment"] = pedersenCommitment
deposit["amount"] = generateCommitment["amount"]
deposit["message"] = singleSig["Message"]
deposit["publicKey"] = user1["PublicKey"]
deposit["R"] = user1Schnorr["R"]
deposit["S"] = user1Schnorr["S"]

with open("./deposit.json", "w") as fileDeposit:
    json.dump(deposit, fileDeposit, sort_keys=True, indent=3)
    
print("\nRun the following command to deposit tokens\n\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@deposit.json\" localhost:10000/deposit")

depositTransaction = input("Paste the output of the deposit function here: ")
depositTransaction = json.loads(depositTransaction)

print("\nTransaction receipt for your deposit is here:\nhttps://goerli.etherscan.io/tx/" + depositTransaction["tx"])
input("Congratulations, you have turned your test XFT into a shielded commitment. Press enter to continue.")

print("\nTo continue onto the commitment transfer, we must make a key for our recipient.")
print("Run the following command to generate user 2's keys:\ncurl localhost:10000/keys")

user2 = input("Enter the output of the key generation here: ")
user2 = json.loads(user2)

aggregatedPubKeyInput = open("./aggregatedPubKey.json")
aggregatedPubKeyInput = json.load(aggregatedPubKeyInput)
aggregatedPubKeyInput["publicKeySet"] = [user1["PublicKey"], user2["PublicKey"]]

with open("./aggregatedPubKey.json", "w") as fileAggregatedPubKey:
    json.dump(aggregatedPubKeyInput, fileAggregatedPubKey, sort_keys=True, indent=3)
    
print("\nTo generate the aggregated public key for our two users, run the following command:\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@aggregatedPubKey.json\" localhost:10000/aggregatedPubKey")
aggregatedPubKey = input("Paste the output of the aggregatedPubKey function here: ")
aggregatedPubKey = json.loads(aggregatedPubKey)

print("\nNow, we generate the R_i values to be used in the aggregated signature. Run the following command to generate the R_i for user 1.\ncurl localhost:10000/singleRPair")

user1Ri = input("Paste the output of user 1's singleRPair function here: ")
user1Ri = json.loads(user1Ri)

print("\nNow, run the command again to generate the R_i value for user 2.\ncurl localhost:10000/singleRPair")

user2Ri = input("Paste the output of user 2's singleRPair function here: ")
user2Ri = json.loads(user2Ri)

calculateR = open("./calculateR.json")
calculateR = json.load(calculateR)

calculateR["riSet"] = [user1Ri["R"], user2Ri["R"]]
with open("./calculateR.json", "w") as fileCalculateR:
    json.dump(calculateR, fileCalculateR, sort_keys=True, indent=3)
    
print("Run the following command to calculate the aggregated R value for the multiSig:\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@calculateR.json\" localhost:10000/calculateR")

aggregatedR = input("Paste the output of the calculateR value here: ")
aggregatedR = json.loads(aggregatedR)

signaturePartUser1 = open("./signaturePart.json")
signaturePartUser1 = json.load(signaturePartUser1)

signaturePartUser1["aggregatedPublicKey"] = aggregatedPubKey["aggregatedPublicKey"]
signaturePartUser1["L"] = int(aggregatedPubKey["L"])
signaturePartUser1["message"] = singleSig["Message"]
signaturePartUser1["privateKey"] = int(user1["PrivateKey"])
signaturePartUser1["pubKey"] = user1["PublicKey"]
signaturePartUser1["R"] = aggregatedR
signaturePartUser1["Ri"] = user1Ri["R"]
signaturePartUser1["ri"] = user1Ri["Valr"]

with open("./signaturePart.json", "w") as fileSignaturePart:
    json.dump(signaturePartUser1, fileSignaturePart, sort_keys=True, indent=3)

print("Run the following command to calculate user 1's portion of the Schnorr multi-signature\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@signaturePart.json\" localhost:10000/signaturePart")

user1MultiSig = input("Enter the output of user 1's partial signature': ")
user1MultiSig = int(user1MultiSig)

signaturePartUser2 = open("./signaturePart.json")
signaturePartUser2 = json.load(signaturePartUser2)

signaturePartUser2["aggregatedPublicKey"] = aggregatedPubKey["aggregatedPublicKey"]
signaturePartUser2["L"] = int(aggregatedPubKey["L"])
signaturePartUser2["message"] = singleSig["Message"]
signaturePartUser2["privateKey"] = int(user2["PrivateKey"])
signaturePartUser2["pubKey"] = user2["PublicKey"]
signaturePartUser2["R"] = aggregatedR
signaturePartUser2["Ri"] = user2Ri["R"]
signaturePartUser2["ri"] = user2Ri["Valr"]

with open("./signaturePart.json", "w") as fileSignaturePart:
    json.dump(signaturePartUser2, fileSignaturePart, sort_keys=True, indent=3)
    
print("Run the following command to calculate user 2's portion of the Schnorr multi-signature\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@signaturePart.json\" localhost:10000/signaturePart")

user2MultiSig = input("Enter the output of user 2's partial signature': ")
user2MultiSig = int(user2MultiSig)

sigList = [user1MultiSig, user2MultiSig]

aggregatedSignature = open("./aggregatedSignature.json")
aggregatedSignature = json.load(aggregatedSignature)

aggregatedSignature["L"] = int(aggregatedPubKey["L"])
aggregatedSignature["aggregatedPublicKey"] = aggregatedPubKey["aggregatedPublicKey"]
aggregatedSignature["R"] = aggregatedR
aggregatedSignature["sigList"] = sigList

with open("./aggregatedSignature.json", "w") as fileAggregatedSignature:
    json.dump(aggregatedSignature, fileAggregatedSignature, sort_keys=True, indent=3)

print("Run the following command to aggregate the two partial signatures into a complete Schnorr MultiSig\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@aggregatedSignature.json\" localhost:10000/aggregatedSignature")

schnorrMultiSig = input("Enter the output of the aggregatedSignature function here: ")
schnorrMultiSig = json.loads(schnorrMultiSig)
recipientAddress = input("Enter the Ethereum address of the intended recipient here (leave blank to send to the default recipient wallet): ")

transferInput = open("./transfer.json")
transferInput = json.load(transferInput)

if len(senderPrivateKey) == 64:
    transferInput["senderPrivateKey"] = senderPrivateKey
else:
    transferInput["senderPrivateKey"] = deposit["senderPrivateKey"]
    
if len(recipientAddress) == 42:
    transferInput["recipient"] = recipientAddress
elif len(recipientAddress) == 0:
    transferInput["recipient"] = "0xAB1cA31A8c3316d662c71e26e02786dEbb902256"

transferInput["amount"] = deposit["amount"]
transferInput["senderPubKey"] = user1["PublicKey"]
transferInput["recipientPubKey"] = user2["PublicKey"]
transferInput["message"] = singleSig["Message"]
transferInput["aggregatedPublicKey"] = aggregatedPubKey["aggregatedPublicKey"]
transferInput["R"] = schnorrMultiSig["R"]
transferInput["S"] = schnorrMultiSig["S"]
commitmentId = transferInput["commitmentId"]

print("\nUser 1's commitment is represented by the following point on the EC:\n" + "X: " + str(pedersenCommitment["X"]) + "\n" + "Y: " + str(pedersenCommitment["Y"]))
print("\nNavigate to:\nhttps//goerli.etherscan.io/address/0xC83476667bDcE8c859A444f4430cCBA14A786d1A#readContract")
print("\nUsing function (2.) _commitmentById, the address used to deposit (default address: 0x1b17552bE3192810B80AE14B6CF8769D5dF9FF9e), and starting with ID 1, query the contract until the output matches that of your Pedersen Commitment")
commitmentInput = input("Enter the ID corresponding to the commitment generated above (if using default address, leave blank): ")

if len(commitmentInput) == 0:
    commitmentId += 1
    transferInput["commitmentId"] = commitmentId
else:
    commitmentId = int(commitmentInput)
    transferInput["commitmentId"] = commitmentId
    
with open("./transfer.json", "w") as fileTransfer:
    json.dump(transferInput, fileTransfer, sort_keys=True, indent=3)

print("To transfer your commitment, enter the following command:\n curl -i -X POST -H \"Content-Type: application/json\" -d \"@transfer.json\" localhost:10000/transfer")
transferReceipt = input("Enter the output of the transfer function here: ")
transferReceipt = json.loads(transferReceipt)
print("View the receipt of your transfer here:\nhttps://goerli.etherscan.io/tx/"+transferReceipt["tx"])

print("Congratulations, you just performed a shielded transfer using Bulletproofs and Pedersen Commitments")
input("Press enter to continue onto the final step: withdrawing tokens to the recipient account:\n")

singleSig2 = open("./singleSig.json")
singleSig2 = json.load(singleSig2)

singleSig2["Message"] = singleSig["Message"]
singleSig2["PrivateKey"] = int(user2["PrivateKey"])
singleSig2["PubKey"] = user2["PublicKey"]

with open("./singleSig2.json", "w") as fileSingleSig2:
    json.dump(singleSig2, fileSingleSig2, sort_keys=True, indent=3)

print("Before executing the withdrawal, user 2 must generate a Schnorr single signature.")
print("To do so, run the following command:\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@singleSig2.json\" localhost:10000/singleSig")
user2Schnorr = input("Paste user 2's Schnorr signature here: ")
user2Schnorr = json.loads(user2Schnorr)

withdrawInput = open("./withdraw.json")
withdrawInput = json.load(withdrawInput)

withdrawPrivateKey = input("Enter the private key of the recipient wallet: ")

withdrawInput["senderPrivateKey"] = withdrawPrivateKey
withdrawInput["commitmentOldId"] = commitmentId
withdrawInput["amount"] = deposit["amount"]
withdrawInput["message"] = singleSig["Message"]
withdrawInput["publicKey"] = user2["PublicKey"]
withdrawInput["R"] = user2Schnorr["R"]
withdrawInput["S"] = user2Schnorr["S"]

with open("./withdraw.json", "w") as fileWithdraw:
    json.dump(withdrawInput, fileWithdraw, sort_keys=True, indent=3)

print("To perform the withdrawal, run the following command:\ncurl -i -X POST -H \"Content-Type: application/json\" -d \"@withdraw.json\" localhost:10000/withdraw")
withdrawTransaction = input("Enter the output of the withdrawal function here: ")
withdrawTransaction = json.loads(withdrawTransaction)
print("The receipt for your withdrawal can be found here:")
print("https://goerli.etherscan.io/tx/" + withdrawTransaction["tx"])
print("Congratulations, you have successfully redeemed your shielded commitments for test XFT.")
