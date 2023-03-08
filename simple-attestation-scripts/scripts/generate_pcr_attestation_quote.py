import subprocess

# Set SERVICE_PROVIDER_NONCE value
nonce_value = "12345678"
with open("SERVICE_PROVIDER_NONCE", "w") as f:
    f.write(nonce_value)

# Quote
pcr_list = "sha256:0,1,2,3,4,5,6,7,8,9,10"
subprocess.run(["tpm2_quote",
                "--key-context", "rsa_ak.ctx",
                "--pcr-list", pcr_list,
                "--message", "pcr_quote.plain",
                "--signature", "pcr_quote.signature",
                "--qualification", "SERVICE_PROVIDER_NONCE",
                "--hash-algorithm", "sha256",
                "--pcr", "pcr.bin"])
