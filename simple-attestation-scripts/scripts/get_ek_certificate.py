import subprocess

RSA_EK_CERT_NV_INDEX = "0x01C00002"

# Get NV size
nv_info = subprocess.check_output(["tpm2_nvreadpublic", RSA_EK_CERT_NV_INDEX])
nv_size = int(nv_info.decode().split("size:")[1].strip())

# Read NV contents
cmd = ["tpm2_nvread",
       "--hierarchy", "owner",
       "--size", str(nv_size),
       "--output", "rsa_ek_cert.bin",
       RSA_EK_CERT_NV_INDEX]

subprocess.run(cmd, check=True)
