import subprocess

# tpm2_createek command
create_ek_command = ["tpm2_createek",
                     "--ek-context", "rsa_ek.ctx",
                     "--key-algorithm", "rsa",
                     "--public", "rsa_ek.pub"]

create_ek_process = subprocess.Popen(create_ek_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
create_ek_output, create_ek_error = create_ek_process.communicate()

# tpm2_createak command
create_ak_command = ["tpm2_createak",
                     "--ek-context", "rsa_ek.ctx",
                     "--ak-context", "rsa_ak.ctx",
                     "--key-algorithm", "rsa",
                     "--hash-algorithm", "sha256",
                     "--signing-algorithm", "rsassa",
                     "--public", "rsa_ak.pub",
                     "--private", "rsa_ak.priv",
                     "--ak-name", "rsa_ak.name"]

create_ak_process = subprocess.Popen(create_ak_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
create_ak_output, create_ak_error = create_ak_process.communicate()
