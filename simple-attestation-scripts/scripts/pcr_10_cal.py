import hashlib
import subprocess

# Read the binary_runtime_measurements file into a byte string
with open('/sys/kernel/security/ima/binary_runtime_measurements', 'rb') as f:
    data = f.read()

# Iterate through the byte string in 24-byte chunks
for i in range(0, len(data), 24):
    # Extract the PCR index and measurement value
    pcr_idx = int.from_bytes(data[i+16:i+18], byteorder='little')
    if pcr_idx == 10:
        measurement = data[i:i+16]

        # Hash the measurement value
        hash_value = hashlib.sha256(measurement).digest()

        # Extend the PCR value with the hash value
        subprocess.run(['tpm2_pcrextend', f'{pcr_idx}:sha256={hash_value.hex()}'])

# Print the final PCR values
output = subprocess.check_output(['tpm2_pcrread'])
print(output.decode())
