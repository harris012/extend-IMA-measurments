import subprocess

result = subprocess.run([
    "tpm2_checkquote",
    "--public", "rsa_ak.pub",
    "--message", "pcr_quote.plain",
    "--signature", "pcr_quote.signature",
    "--qualification", "SERVICE_PROVIDER_NONCE",
    "--pcr", "pcr.bin"
], capture_output=True)

# print the output
print(result.stdout)

if result.returncode == 0:
    print("Quote is valid")
else:
    print("Quote is invalid")
    print(result.stderr.decode())
