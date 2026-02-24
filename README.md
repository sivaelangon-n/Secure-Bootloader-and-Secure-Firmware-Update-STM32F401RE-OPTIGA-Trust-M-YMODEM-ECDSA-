# STM32 Secure Bootloader with OPTIGA™ Trust M

A secure, lightweight bootloader designed for STM32F401RE microcontrollers that integrates hardware-based cryptographic verification using Infineon’s OPTIGA™ Trust M secure element. This project implements a robust and fail-safe firmware update mechanism that leverages YMODEM protocol for transmission and ECDSA signature verification for ensuring firmware authenticity before execution. Built for resource-constrained embedded systems, this bootloader is suitable for industrial, consumer, and IoT deployments where firmware security and reliability are critical.

## 🚀 Why This Bootloader?
Unlike conventional bootloaders that rely on internal flash-based key storage, this design uses a dedicated secure element (Trust M) to ensure the private key is never exposed — even to the MCU itself. The STM32 simply hashes the firmware and delegates validation to Trust M, creating a tamper-proof firmware update pipeline that is ideal for mission-critical devices.

---

## 📦 Project Structure 

```
Repository
├── docs/                # Documentation and design references
├── externals/           # External libraries and middleware
│   ├── mbedtls/         # TLS cryptographic library used for SHA-256 hash
│   └── optiga-trust-m/  # OPTIGA™ Trust M stack and dependency libraries
├── project/             # Project source (STM32CubeIDE structure)
│   ├── Core/            # Application logic and STM32 startup files
│   ├── Drivers/         # HAL/CMSIS drivers
│   ├── optiga/          # Integrated OPTIGA™ libraries for secure boot
│   └── pal/             # Platform Abstraction Layer for STM32 (GPIO/I2C)
├── tools/               # Utility scripts (e.g., firmware signing, ymodem)
└── README.md            # Project overview and usage documentation
```

---

## ✨ Features

- UART-based firmware update using YMODEM protocol
- SHA-256 hash computation using mbedTLS
- ECDSA signature verification with OPTIGA™ Trust M
- Secure public key storage inside Trust M (OID-based)
- Jump-to-application logic after signature validation

---

## 🔐 Secure Boot Flow

1. **Firmware Reception**  
   Bootloader receives a `firmware.bin` file with an appended ECDSA signature via UART using YMODEM.

2. **Metadata Parsing**  
   Parses version, length, and signature from the received payload.

3. **SHA-256 Hashing**  
   Uses `mbedTLS` to compute the hash of the firmware (excluding the signature).

4. **Public Key Validation (Trust M)**  
   Verifies the hash against the signature using a secure public key stored in OPTIGA™ Trust M.

5. **Firmware Flashing & Jump**  
   If verification passes, firmware is flashed into application memory and execution is transferred.

---

## 🧪 How to Use

- Use the provided `.sh` script in `/tools` to:
  - Generate an ECC keypair
  - Sign `firmware.bin`
  - Produce `signature.der` and `public_key_raw.bin`

- Flash the bootloader binary to STM32.

- Use a UART terminal or Python YMODEM script to transmit the signed firmware.

---

## 🛠️ Configuration

Key settings can be adjusted inside:
- `project/Core/Inc/config.h`
- `project/optiga/include/optiga/`

Memory layout and boot regions can be changed via linker files:
- `STM32F401RETX_FLASH.ld`

---

## 📚 References

- [OPTIGA™ Trust M Documentation](https://www.infineon.com/trustm)
- [mbedTLS GitHub](https://github.com/Mbed-TLS/mbedtls)
- [STM32 Programming Manual (PM0214)](https://www.st.com/resource/en/programming_manual/dm00046982.pdf)

---

## 🧩 License

This project is licensed under the MIT License — see `LICENSE` file for details.

---

## 📣 Contributions

Feel free to open issues or submit pull requests to improve this bootloader or expand it to support other STM32 families.
