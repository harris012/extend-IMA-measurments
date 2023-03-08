# Simple attestation scripts with tpm2-tools

## Intro

This repo uses [tpm2-tools](https://github.com/tpm2-software/tpm2-tools) project to set up a bare bone remote attestation of the system software state as reflected by the TPM2 platform-configuration-registers (PCR).

## Software Requirements


* [tpm2-tss v2.3.0](https://github.com/tpm2-software/tpm2-tss)
* [tpm2-abrmd v2.2.0](https://github.com/tpm2-software/tpm2-abrmd)
* [tpm2-tools v4.0](https://github.com/tpm2-software/tpm2-tools)
* [ibmswtpm](https://sourceforge.net/projects/ibmswtpm2/)
* [openssl](https://linux.die.net/man/1/openssl)

## Tools and utilities used from the tpm2-tools project
* [tpm2_createprimary](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_createprimary.1.md)
* [tpm2_create](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_create.1.md)
* [tpm2_createek](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_createek.1.md)
* [tpm2_createak](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_createak.1.md)
* [tpm2_getekcertificate](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_getekcertificate.1.md)
* [tpm2_makecredential](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_makecredential.1.md)
* [tpm2_activatecredential](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_activatecredential.1.md)
* [tpm2_pcrextend](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_pcrextend.1.md)
* [tpm2_pcrread](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_pcrread.1.md)
* [tpm2_quote](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_quote.1.md)
* [tpm2_checkquote](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_checkquote.1.md)
* [tpm2_getrandom](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_getrandom.1.md)
* [tpm2_readpublic](https://github.com/tpm2-software/tpm2-tools/blob/master/man/tpm2_readpublic.1.md)


### Steps
1. “Device-Node“ creating the endorsement-key and the attestation-identity-key. Use the script `create_keys.py`. It will generate six files as shown in the command below.

```bash

tpm2_createek \
--ek-context rsa_ek.ctx \
--key-algorithm rsa \
--public rsa_ek.pub

tpm2_createak \
--ek-context rsa_ek.ctx \
--ak-context rsa_ak.ctx \
--key-algorithm rsa \
--hash-algorithm sha256 \
--signing-algorithm rsassa \
--public rsa_ak.pub \
--private rsa_ak.priv \
--ak-name rsa_ak.name
```

2. “Device-Node“ retrieving the endorsement-key-certificate to send to the
“Privacy-CA“. The endorsement key certificates are provided by the TPM manufacturer. While most TPM manufacturers
store them in the [TCG specified NV indices]((https://trustedcomputinggroup.org/wp-content/uploads/TCG_IWG_Credential_Profile_EK_V2.1_R13.pdf)). It can be done by executing the script `get_ek_certificate.py`.

```bash
# TPM2 NV Index 0x1c00002 is the TCG specified location for RSA-EK-certificate.
RSA_EK_CERT_NV_INDEX=0x01C00002

NV_SIZE=`tpm2_nvreadpublic $RSA_EK_CERT_NV_INDEX | grep size |  awk '{print $2}'`

tpm2_nvread \
--hierarchy owner \
--size $NV_SIZE \
--output rsa_ek_cert.bin \
$RSA_EK_CERT_NV_INDEX

```
3. “Privacy-CA“ and the “Device-Node“ performing a credential activation
challenge in order to verify the AIK is bound to the EK from the EK-certificate
originally shared by the “Device-Node“. This is done in two different instances
in the proposed simple-attestation-framework — Once when the “Service-Provider“
requests the “Device-Node“ to send over the identities as part of the service
registration process. And the second time when the “Device-Node“ sends its AIK
to the “Service-Provider“ and the “Service-Provider“ in turn sends it over to
the “Privacy-CA“ in order to verify the anonymous identity. It will be done using the script `credential_activation.py`.

```bash
# Privacy-CA creating the wrapped credential and encryption key
file_size=`stat --printf="%s" rsa_ak.name`
loaded_key_name=`cat rsa_ak.name | xxd -p -c $file_size`

echo "this is my secret" > file_input.data
tpm2_makecredential \
--tcti none \
--encryption-key rsa_ek.pub \
--secret file_input.data \
--name $loaded_key_name \
--credential-blob cred.out

# Device-Node activating the credential
tpm2_startauthsession \
--policy-session \
--session session.ctx

TPM2_RH_ENDORSEMENT=0x4000000B
tpm2_policysecret -S session.ctx -c $TPM2_RH_ENDORSEMENT

tpm2_activatecredential \
--credentialedkey-context rsa_ak.ctx \
--credentialkey-context rsa_ek.ctx \
--credential-blob cred.out \
--certinfo-data actcred.out \
--credentialkey-auth "session:session.ctx"

tpm2_flushcontext session.ctx
```

The output from the terminal will look like below:

```log
root@ubuntu:/home/ubuntu/scripts# python3 credential_activation.py 
WARN: Tool optionally uses SAPI. Continuing with tcti=none
837197674484b3f81a90cc8d46a5d724fd52d76e06520b64f2a1da1b331469aa
certinfodata:74686973206973206d7920736563726574

```

4. “Device-Node“ generating the PCR attestation quote on request from the
“Service-Provider“. The “Service-Provider“ specifies the PCR-banks, PCR-indices,
and the ephemeral NONCE data. The NONCE is to ensure there is no possibility of
a replay attack on the quote verification and validation process. Validity of
the signing key for attestation quote is ascertained to be a valid one by the
“Privacy-CA“. This step will be performed by the script `generate_pcr_attestation_quote.py`.

```bash
echo "12345678" > SERVICE_PROVIDER_NONCE

tpm2_quote \
--key-context rsa_ak.ctx \
--pcr-list sha256:0,1,2,3,4,5,6,7,8,9,10 \
--message pcr_quote.plain \
--signature pcr_quote.signature \
--qualification SERVICE_PROVIDER_NONCE \
--hash-algorithm sha256 \
--pcr pcr.bin
```

The example output will be:

```log

root@ubuntu:/home/ubuntu/scripts# python3 generate_pcr_attestation_quote.py 
quoted: ff54434780180022000ba3913137675f18fb5cbf6937f2733ace178d6e323ae39c6c92ec2a37d9df7be70008313233343536373800000000221679c8000000460000000001201910230016363600000001000b03ff07000020026a602828a6f99c0e98c95d7a94fd35ddaf2e7ea3c831bb69f865d88ef8954f
signature:
  alg: rsassa
  sig: 694c21125290fe83162308b12e1f0b134e2511f57e22defe0d2840bce1fb1a12a10e09f4a310f2984b522869edf9c8e143f2d28f0e7003f501aae6e8bc7892f4b36c973351701054f7a520577dec6035d38676b9a7a0146c694081b6eb04690c955dff9d71d80282d40ad25594b4861a62a652d794d64ee417c1b8d63573c2488c95632247602d6976514e73e0aa51e499a86a4e6007fc37ec850b00897a3a77f7042b84975e3340e3d7205dc6b98008a4bb60746ffd01a543d39feee6a597fc5f368b47cfd56a744f9b799f92bba86c91f3372430a5196675b9d64b5040a56e0ac8b209ea997582b0184f03d222107af216758140e9ebce1c4138869b4883a8
pcrs:
  sha256:
    0 : 0xE21B703EE69C77476BCCB43EC0336A9A1B2914B378944F7B00A10214CA8FEA93
    1 : 0x5D67D5F3E97E858D285DFBC110319DEFA99AF8D8991E7CFD163E27D7DEC64074
    2 : 0x5CEB8FB1DC47C1D630CEF318477D36583D5ABFF85E55F399DFCA23763AEDF3F5
    3 : 0xE21B703EE69C77476BCCB43EC0336A9A1B2914B378944F7B00A10214CA8FEA93
    4 : 0x45803F687DCFFB1C4274E44D520B0DC279AE1FCAC423902AB3ACE81E3B1647E3
    5 : 0xED9C09F4521129FCBDE64B23EA29E57FF5CE71BC0ECBD6B54BED7A8A88E7A767
    6 : 0xE21B703EE69C77476BCCB43EC0336A9A1B2914B378944F7B00A10214CA8FEA93
    7 : 0xE21B703EE69C77476BCCB43EC0336A9A1B2914B378944F7B00A10214CA8FEA93
    8 : 0x0000000000000000000000000000000000000000000000000000000000000000
    9 : 0x0000000000000000000000000000000000000000000000000000000000000000
    10: 0x8E00398309DAC14633A021F47304810799C6CA5BE28640859DCA25690A525558
calcDigest: 026a602828a6f99c0e98c95d7a94fd35ddaf2e7ea3c831bb69f865d88ef8954f
```

5. “Service-Provider“ verifying the attestation quote generated and signed by
the “Device-Node“. To make the determination of the software-state of the
“Device-Node“, after the signature and nonce verification process, the
“Service-Provider“ validates the digest of the PCR values in the quote against
a known-good-valid —the [golden/ reference value](https://tpm2-software.github.io/2020/06/12/Remote-Attestation-With-tpm2-tools.html#golden-or-reference-pcr)
ascertained previously. This step will be performed by the script `get_ek_certificate.py`.

```bash
tpm2_checkquote \
--public rsa_ak.pub \
--message pcr_quote.plain \
--signature pcr_quote.signature \
--qualification SERVICE_PROVIDER_NONCE \
--pcr pcr.bin
```

The example output will be:

```log

root@ubuntu:/home/ubuntu/scripts# python3 check_quote.py 
b'pcrs:\n  sha256:\n    0 : 0xE21B703EE69C77476BCCB43EC0336A9A1B2914B378944F7B00A10214CA8FEA93\n    1 : 0x5D67D5F3E97E858D285DFBC110319DEFA99AF8D8991E7CFD163E27D7DEC64074\n    2 : 0x5CEB8FB1DC47C1D630CEF318477D36583D5ABFF85E55F399DFCA23763AEDF3F5\n    3 : 0xE21B703EE69C77476BCCB43EC0336A9A1B2914B378944F7B00A10214CA8FEA93\n    4 : 0x45803F687DCFFB1C4274E44D520B0DC279AE1FCAC423902AB3ACE81E3B1647E3\n    5 : 0xED9C09F4521129FCBDE64B23EA29E57FF5CE71BC0ECBD6B54BED7A8A88E7A767\n    6 : 0xE21B703EE69C77476BCCB43EC0336A9A1B2914B378944F7B00A10214CA8FEA93\n    7 : 0xE21B703EE69C77476BCCB43EC0336A9A1B2914B378944F7B00A10214CA8FEA93\n    8 : 0x0000000000000000000000000000000000000000000000000000000000000000\n    9 : 0x0000000000000000000000000000000000000000000000000000000000000000\n    10: 0x8E00398309DAC14633A021F47304810799C6CA5BE28640859DCA25690A525558\nsig: 694c21125290fe83162308b12e1f0b134e2511f57e22defe0d2840bce1fb1a12a10e09f4a310f2984b522869edf9c8e143f2d28f0e7003f501aae6e8bc7892f4b36c973351701054f7a520577dec6035d38676b9a7a0146c694081b6eb04690c955dff9d71d80282d40ad25594b4861a62a652d794d64ee417c1b8d63573c2488c95632247602d6976514e73e0aa51e499a86a4e6007fc37ec850b00897a3a77f7042b84975e3340e3d7205dc6b98008a4bb60746ffd01a543d39feee6a597fc5f368b47cfd56a744f9b799f92bba86c91f3372430a5196675b9d64b5040a56e0ac8b209ea997582b0184f03d222107af216758140e9ebce1c4138869b4883a8\n'
Quote is valid

```
