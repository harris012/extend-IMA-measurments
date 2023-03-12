import os

# Privacy-CA creating the wrapped credential and encryption key
file_size = os.stat("rsa_ak.name").st_size
with open("rsa_ak.name", "rb") as f:
    loaded_key_name = f.read().hex()

with open("file_input.data", "w") as f:
    f.write("this is my secret")

tpm2_makecredential_command = f"tpm2_makecredential --tcti none --encryption-key rsa_ek.pub --secret file_input.data --name {loaded_key_name} --credential-blob cred.out"
os.system(tpm2_makecredential_command)

# Device-Node activating the credential
tpm2_startauthsession_command = "tpm2_startauthsession --policy-session --session session.ctx"
os.system(tpm2_startauthsession_command)

tpm2_policysecret_command = "tpm2_policysecret -S session.ctx -c 0x4000000B"
os.system(tpm2_policysecret_command)

tpm2_activatecredential_command = "tpm2_activatecredential --credentialedkey-context rsa_ak.ctx --credentialkey-context rsa_ek.ctx --credential-blob cred.out --certinfo-data actcred.out --c>
os.system(tpm2_activatecredential_command)

tpm2_flushcontext_command = "tpm2_flushcontext session.ctx"
os.system(tpm2_flushcontext_command)
