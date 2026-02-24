#!/bin/bash

# === Check Input ===
if [ ! -f "firmware.bin" ]; then
    echo "Error: firmware.bin not found."
    exit 1
fi

# === Generate ECC Key Pair ===
openssl ecparam -name prime256v1 -genkey -noout -out private_key.pem
openssl ec -in private_key.pem -pubout -out public_key.pem

# === Extract Raw Public Key ===
openssl ec -in private_key.pem -pubout -outform DER | tail -c 65 > public_key_raw.bin
echo "Raw public key written to public_key_raw.bin"

# === Hash Firmware ===
openssl dgst -sha256 -binary firmware.bin > firmware.hash
echo "Firmware hash written to firmware.hash"

# === Sign the Hash ===
openssl dgst -sha256 -sign private_key.pem -out signature.der firmware.bin
echo "Signature written to signature.der"

# === Output Files ===
echo "Files generated:"
echo "- private_key.pem"
echo "- public_key.pem"
echo "- public_key_raw.bin"
echo "- firmware.hash"
echo "- signature.der"
