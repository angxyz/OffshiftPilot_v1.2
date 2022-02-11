# Offshift Testnet Pilot - Version 1.2
![[Offshift Testnet Pilot: Client-Side Guide](https://offshift.io/public/blog/2021-12-31-offshift-pilot-client-side-guide/)](https://offshift.io/public/blog/2021-12-31-offshift-pilot-client-side-guide/cover.png)
[Offshift Testnet Pilot: Client-Side Guide](https://offshift.io/public/blog/2021-12-31-offshift-pilot-client-side-guide/)

## Downloading and running the Docker container for the first time
This requires Docker Desktop (and its dependencies) to be installed on your machine. [Docker Installation Documentation](https://docs.docker.com/desktop/)

### To pull the Offshift Docker v1.2 Container
`docker pull offshiftxft/offshift:v1.2`

[Video walkthrough here](https://youtu.be/8Rd0VProHF4)

### To run the container
`docker run -p 10000:10000/offshiftxft/offshift:v1.2`

### Downloading example JSON files to working directory
`docker cp (containerID):/app/inputExample/ ./`

Where (containerID) is that of the Offshift v1.2 Pilot currently running in Docker. 
For example, if the container ID is `ab51486470c8`, we get

`docker cp ab51486470c8:/app/inputExample/ ./`

[Video walkthrough here](https://youtu.be/hXVluwb1ED0)

## Getting Test XFT
`curl -i -X POST -H "Content-Type: application/json" -d "@getTokens.json" localhost:10000/getTokens`

Input format:
```json
{
  "recipient": "0x8Bcca25d1CDedBC6A09802B11aaD4c6AC4a52dE2"
}

```
Each transaction will send 10 TestXFT

## Depositing Test XFT and Generating a Pedersen Commitment
### 1. Generation of public and private keys
`curl -i -X GET -H "Content-Type: application/json" -d "@keys.json" localhost:10000/keys`

Output format:
```json
{
 "PublicKey":
  {
    "X":55393486233968973884023741539226407878877539358088804034904205276743150878592,
    "Y":67470022574068113682912966951026732901032112437171999642164715379119585347587
  },
 "PrivateKey":"50164087880838209208916483351314702263229810715424671509385049262595918466125"
 }
```

### 2. Schnorr signature (for 1 user)
`curl -i -X POST -H "Content-Type: application/json" -d "@singleSig.json" localhost:10000/singleSig`

Input format:
```json
{
   "Message": "1234",
   "PrivateKey": 50164087880838209208916483351314702263229810715424671509385049262595918466125,
   "PubKey": {
      "X": 55393486233968973884023741539226407878877539358088804034904205276743150878592,
      "Y": 67470022574068113682912966951026732901032112437171999642164715379119585347587
   }
}

```
Where:
`"Message"` is the secret message to be encoded;

`"PrivateKey"` and  `"PubKey"` user 1's keys generated in step 1.


Output format:
```json
{
"R":
  {
    "X":66320251617260054097359498953279972194460317246623014650071823237991832001873,
    "Y":43924063416169606105749452716949701288867104906269404650930371145957367751385
  },
"S":"107566485657041323120838151611738930088458765751712843787299781921212703624109"
}
```

Where: `R = r*G` and `S = r - e*x` with: 

* `r` being a randomly generated value
* `G` being the generating point on the elliptic curve 
* `e` is the hash of (r, message)
* `x` being the signing private key

### 3. Generating a Pedersen Commitment

Input format:

```json
{
   "amount": 10000000000,
   "recipientPubKey": {
      "X": 55393486233968973884023741539226407878877539358088804034904205276743150878592,
      "Y": 67470022574068113682912966951026732901032112437171999642164715379119585347587
   }
}
```

Where: `"amount"` is the uint256-formatted number of test XFT to be deposited (Deposit amount times 10^18), and where `recipientPubKey` is the user's public key generated in step 1.

Output format: 
```json
{
  "X":90386016570344411106070881933860155672109506867273679191277367088208927588563,
  "Y":67075365857930316302791410587605110040157189826604989888642285612787624437276
}
```

Denote the above EC point as `C`, defined as follows:

`C = r*H + a*G`, where:
* `r` is a randomly generated integer
* `H = q*G` is an EC point whose discrete logarithm (`q`) is a hidden value
* `a` is the value to be committed (`amount` from part 2.)
* `G` is the generating point on the EC.

### 4. Approval

Input format:
```json
{
   "amount": 10000000000,
   "senderPrivateKey": "[Private key goes here]",
   "spender": "[Wallet address goes here]"
}
```
Where `"amount"` is the amount to approve (times 10^18), `"senderPrivateKey"` is the wallet private key of the sender, and `"spender"` is the wallet address of the sender

Output format:
```json
{"tx":"0x655467da71096c1b9e025931cca6c3ff45cda20911296af664983fddeb3bc237"}
```
Where `tx` is the transaction hash of the approval transaction (on the Goerli testnet).

### 5. Deposit

Input format:
```json
{
   "R": {
      "X": 66320251617260054097359498953279972194460317246623014650071823237991832001873,
      "Y": 43924063416169606105749452716949701288867104906269404650930371145957367751385
   },
   "S": "107566485657041323120838151611738930088458765751712843787299781921212703624109",
   "amount": 10000000000,
   "commitment": {
      "X": 90386016570344411106070881933860155672109506867273679191277367088208927588563,
      "Y": 67075365857930316302791410587605110040157189826604989888642285612787624437276
   },
   "message": "1234",
   "publicKey": {
      "X": 55393486233968973884023741539226407878877539358088804034904205276743150878592,
      "Y": 67470022574068113682912966951026732901032112437171999642164715379119585347587
   },
   "senderPrivateKey": "[Insert private key here]"
}
```
Where: 
* `R` and `S` are the values generated by `singleSig`
* `amount` is the amount of test XFT to deposit
* `commitment` is the value `C` generated by `generateCommitment`
* `message` is the secret message
* `publicKey` is the user's public key generated by `keys`
* `senderPrivateKey` is the depositor's wallet private key

## Transferring a commitment from one wallet address to another
### 1. Key Generation for the Recipient

`curl localhost:10000/keys`

Output format:
```json
{
  "PublicKey": 
    { 
      "X":105385934772674921333338303584659716769598014421292424295398416788977472437709,
      "Y":57841707114828419480734530433428159235823078030340093421815956515046734186225
    },
  "PrivateKey": "60342033444369117030273856201831256525169522153752337788702083998354826500681"
}
```

### 2. Aggregation of Public Keys
`curl -i -X POST -H "Content-Type: application/json" -d "@aggregatedPubKey.json" localhost:10000/aggregatedPubKey`

Input format:
```json
{
   "markBool": [
      true,
      false
   ],
   "publicKeySet": [
      {
         "X": 55393486233968973884023741539226407878877539358088804034904205276743150878592,
         "Y": 67470022574068113682912966951026732901032112437171999642164715379119585347587
      },
      {
         "X": 105385934772674921333338303584659716769598014421292424295398416788977472437709,
         "Y": 57841707114828419480734530433428159235823078030340093421815956515046734186225
      }
   ]
}
```
Where:
* `"markBool"` is a list of boolean values
* `"publicKeySet"` is a list of the two users' public keys, in order of generation.

Output format:
```json
{
  "L":"39184799402545805145171235335300888234955695445695599265555164800677136519179",
  "aggregatedPublicKey": 
    {
      "X":20657495020295923301006045976226194621624255514829111031096075364417450856540,
      "Y":42624676770439296054454169726109514637551597792162004898913060256557676401132
    }
}
```

Where `L = H(X_i)` and `aggregatedPublicKey = Sum(X_i * H(L, X_i))`. Given that:
* `H()` is the hashing function over all the inputs `i`
* `X_i` is the public key for user `i`


### 3. Generation of Private Keys r_i for Schnorr Multi Signature
Note: Key pairs must be generated for each user (in this case, two key pairs are generated).
`curl localhost:10000/singleRPair`

Output Format:
```json
{
  "R":
    {
      "X":14382088549438545712247104673870587093844658838907497224857044651179886453118,
      "Y":63160472532445594617448964916177331970232729906900287696447319236916875440833
    },
"Valr":112053316493580319602358640340979462689867117818695139990021056566464610376527
}
```
```json
{
  "R":
    {
      "X":18003731094453827348132757752065293992803470197886195935388880717733572029168,
      "Y":56751863986877942639763927669331087484320466616727243341593419138270763407982
    },
"Valr":46425634002882492625694697956066250797149435081381153689184430199074440692193
}
```
Where:
* `Valr` is the private key `r_i` for user `i`
* `R = Valr * G` is the corresponding public key `R_i` with `G` being the generator point on the EC.

### 4. Calculating the Common R Value for Signing

`curl -i -X POST -H "Content-Type: application/json" -d "@calculateR.json" localhost:10000/calculateR`

Input Format:
```json
{
   "markBool": [
      true,
      false
   ],
   "riSet": [
      {
         "X": 14382088549438545712247104673870587093844658838907497224857044651179886453118,
         "Y": 63160472532445594617448964916177331970232729906900287696447319236916875440833
      },
      {
         "X": 18003731094453827348132757752065293992803470197886195935388880717733572029168,
         "Y": 56751863986877942639763927669331087484320466616727243341593419138270763407982
      }
   ]
}
```

Where:
* `markBool` is a list of boolean values
* `riSet` is a list of the public key values `R_i` generated for each user in step 3.

Output Format:
```json
{
  "X":30259578276785630768900691512621140540650559853620269272307576454027705636618,
  "Y":23812363279936222966579924595367442077745313694469434498508882167383321228591
}
```
Where `R = R_1 + R_2` is the sum of the `R_i` values for users `i` 

### 5. Partial Signatures
Each user must generate a partial signature that takes the following form

`s_i = r_i + H(X, R, m) * H(L, X_i) * x_i`

Where:
* `s_i` is the partial signauture generated by user `i`
* `r_i` is `Valr` for user `i`, generated in step 3
* `H()` is the hash function
* `X` is the aggregated public key calculated in step 2
* `R` is the common R value calculated in step 4
* `m` is the message to be signed
* `L = H(X_1, X_2)` is the hash of the public keys `X_i = x_i * G`
* `X_i` and `x_i` are the public and private key, respectively, of user `i`

Input Format:
```json
```
```json
{
   "L": 39184799402545805145171235335300888234955695445695599265555164800677136519179,
   "R": {
      "X": 30259578276785630768900691512621140540650559853620269272307576454027705636618,
      "Y": 23812363279936222966579924595367442077745313694469434498508882167383321228591
   },
   "Ri": {
      "X": 18003731094453827348132757752065293992803470197886195935388880717733572029168,
      "Y": 56751863986877942639763927669331087484320466616727243341593419138270763407982
   },
   "aggregatedPubKey": {
      "X": 40097700241745887153431677709747181557501865566708788589569871829235774550452,
      "Y": 115162653860619789327614593622826455370377235451706335817206541683018399755252
   },
   "aggregatedPublicKey": {
      "X": 20657495020295923301006045976226194621624255514829111031096075364417450856540,
      "Y": 42624676770439296054454169726109514637551597792162004898913060256557676401132
   },
   "message": "1234",
   "privateKey": 60342033444369117030273856201831256525169522153752337788702083998354826500681,
   "pubKey": {
      "X": 105385934772674921333338303584659716769598014421292424295398416788977472437709,
      "Y": 57841707114828419480734530433428159235823078030340093421815956515046734186225
   },
   "ri": 46425634002882492625694697956066250797149435081381153689184430199074440692193
}
```

Output format:
```javascript
84417483900300259050463624941323963069615240052275663931460275535044809240685
```
```javascript
5758867890189939535830337634726952830145825529040107550819170580038403442544
```

### 6. Signature Aggregation
`curl -i -X POST -H "Content-Type: application/json" -d "@aggregatedSignature.json" localhost:10000/aggregatedSignature`

Input Format: 

```json
{
   "L": 39184799402545805145171235335300888234955695445695599265555164800677136519179,
   "R": {
      "X": 30259578276785630768900691512621140540650559853620269272307576454027705636618,
      "Y": 23812363279936222966579924595367442077745313694469434498508882167383321228591
   },
   "aggregatedPublicKey": {
      "X": 20657495020295923301006045976226194621624255514829111031096075364417450856540,
      "Y": 42624676770439296054454169726109514637551597792162004898913060256557676401132
   },
   "markBool": [
      true,
      false
   ],
   "sigList": [
      5758867890189939535830337634726952830145825529040107550819170580038403442544,
      84417483900300259050463624941323963069615240052275663931460275535044809240685
   ]
}
```
Where:
* `L` is the value `H(X_1, X_2)` calculated in step 2
* `R` is the common R value calculated in step 4
* `aggregatedPublicKey` is the value `Sum(H(L, Xi)*Xi)` calculated in step 2
* `markBool` is a list of boolean values
* `sigList` is the list of partial signatures `s_i` generated in step 5.

Output Format:
```json
{
  "R":
    {
      "X":30259578276785630768900691512621140540650559853620269272307576454027705636618,
      "Y":23812363279936222966579924595367442077745313694469434498508882167383321228591
    },
  "S":"37133473227205875908937697702090897613368149755839348001964058186511755696196"
}
```
Where:
* `R` is the common R value from step 4
* `S = Sum(s_i)` is the sum of the partial signatures `s_i` generated in step 5

### 7. Transfer
`curl -i -X POST -H "Content-Type: application/json" -d "@transfer.json" localhost:10000/transfer`

Input Format: 
```json
{
   "R": {
      "X": 30259578276785630768900691512621140540650559853620269272307576454027705636618,
      "Y": 23812363279936222966579924595367442077745313694469434498508882167383321228591
   },
   "S": "37133473227205875908937697702090897613368149755839348001964058186511755696196",
   "aggregatedPublicKey": {
      "X": 20657495020295923301006045976226194621624255514829111031096075364417450856540,
      "Y": 42624676770439296054454169726109514637551597792162004898913060256557676401132
   },
   "amount": 10000000000,
   "commitmentId": 5,
   "message": "1234",
   "recipient": "[Recipient address goes here]",
   "recipientPubKey": {
      "X": 105385934772674921333338303584659716769598014421292424295398416788977472437709,
      "Y": 57841707114828419480734530433428159235823078030340093421815956515046734186225
   },
   "senderPrivateKey": "[Wallet private key goes here]",
   "senderPubKey": {
      "X": 55393486233968973884023741539226407878877539358088804034904205276743150878592,
      "Y": 67470022574068113682912966951026732901032112437171999642164715379119585347587
   }
}
```
Where:
* `R` is the common R generated in step 4
* `S` is the aggregated signature calculated in step 6
* `aggregatedPublicKey` was generated in step 2
* `amount` is the deposit amount (times 10^18)
* `commitmentId` is the number corresponding to the commitment generated by user 1
* `message` is the signed message
* `recipient` is the Ethereum address of the intended recipient
* `recipientPublicKey` is the recipient's generated public key
* `senderPrivateKey` is the Ethereum private key of the sender
* `senderPubKey` is the generated public key of the sender

## Recipient Withdrawal of Committed Tokens
### 1. Schnorr Single Signature
`curl -i -X POST -H "Content-Type: application/json" -d "@singleSig.json" localhost:10000/singleSig`

Input format:
```json
{
   "Message": "1234",
   "PrivateKey": 50164087880838209208916483351314702263229810715424671509385049262595918466125,
   "PubKey": {
      "X": 55393486233968973884023741539226407878877539358088804034904205276743150878592,
      "Y": 67470022574068113682912966951026732901032112437171999642164715379119585347587
   }
}

```
Where:
`"Message"` is the secret message to be encoded;

`"PrivateKey"` and  `"PubKey"` user 1's keys generated in step 1.


Output format:
```json
{
"R":
  {
    "X":66320251617260054097359498953279972194460317246623014650071823237991832001873,
    "Y":43924063416169606105749452716949701288867104906269404650930371145957367751385
  },
"S":"107566485657041323120838151611738930088458765751712843787299781921212703624109"
}
```

### 2. Withdrawal
`curl -i -X POST -H "Content-Type: application/json" -d "@withdraw.json" localhost:10000/withdraw`

```json
{
   "R": {
      "X": 88591355403813842779860435825624823225226634623962894382168517548323241389858,
      "Y": 10138031624112932855475458620758180874457135499351406753398420273937926159050
   },
   "S": "101535677211241494780729862937391412333921537347832530642806859772468805573385",
   "amount": 10000000000,
   "commitmentOldId": 4,
   "message": "1234",
   "publicKey": {
      "X": 41255657716858643098295895619894439272077023025469053007949754941291125785666,
      "Y": 26930685929672893587610449705930960608851827760970437980334922890775866836884
   },
   "senderPrivateKey": "[Wallet private key goes here]"
}
```
* `R` is the common R generated in step 4 of part 2.
* `S` is the aggregated signature generated in step 6 of part 2.
* `amount` is the amount to withdraw (Note: In this version of the pilot, the entire committed amount must be withdrawn).
* `commitmentOldId` is the index of the commitment made by user 1 (depositor)
* `message` is the secret message signed by both users
* `publicKey` is user 2's (the withdrawer's) generated public key
* `senderPrivateKey` is the Ethereum (web3) private key corresponding to the address sending the transaction to the blockchain
