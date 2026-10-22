# Chaotic Image Decryption Using AES-GCM
# Combined Decryption Program - Phase 
# ============================================================

import os
import cv2
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ============================================================zz
# STEP 1: LOAD ENCRYPTED IMAGE
# ============================================================

encrypted_path = "results/encrypted_image.png"

if not os.path.exists(encrypted_path):
    raise FileNotFoundError(
        "Encrypted image not found at results/encrypted_image.png"
    )

encrypted_bgr = cv2.imread(encrypted_path)

if encrypted_bgr is None:
    raise ValueError("Encrypted image could not be loaded.")

print("Encrypted image loaded successfully!")
print("Encrypted image size:", encrypted_bgr.shape)

encrypted_image = cv2.cvtColor(
    encrypted_bgr,
    cv2.COLOR_BGR2RGB
)

encrypted_array = np.array(encrypted_image)

print("Encrypted pixel array shape:", encrypted_array.shape)


# ============================================================
# ==========================================
# STEP 2: READ SECRET KEY FROM GUI OR TERMINAL
# ==========================================
import sys

# Check if arguments were passed from gui.py
if len(sys.argv) > 1:
    secret_key_text = sys.argv[1].strip()
else:
    # Fallback to terminal input if executed manually
    secret_key_text = input("\nEnter your secret key: ").strip()

# ============================================================
# STEP 3: CONVERT SECRET KEY TO AES-256 KEY
# ============================================================

try:
    aes_key = bytes.fromhex(secret_key_text)
except ValueError:
    print("\nERROR: Invalid secret key format.")
    print("The secret key must contain hexadecimal characters.")
    raise SystemExit


# Check AES-256 key size

if len(aes_key) != 32:
    print("\nERROR: Invalid secret key length.")
    print("The secret key must represent exactly 256 bits.")
    raise SystemExit

print("\nSecret key format verified!")
print("AES-256 key size:", len(aes_key), "bytes")


# ============================================================
# STEP 4: LOAD PROTECTED IMAGE KEY
# ============================================================

protected_key_path = "key/protected_key.bin"

if not os.path.exists(protected_key_path):
    raise FileNotFoundError(
        "Protected key not found at key/protected_key.bin"
    )

with open(protected_key_path, "rb") as file:
    protected_data = file.read()


# Encryption stored:
#
# nonce + protected_key
#
# AES-GCM nonce = 12 bytes

nonce = protected_data[:12]
protected_key = protected_data[12:]

print("\nProtected key loaded successfully!")
print("Nonce size:", len(nonce), "bytes")


# ============================================================
# STEP 5: AES-GCM KEY VERIFICATION AND RECOVERY
# ============================================================

print("\nVerifying secret key using AES-GCM...")

aes_gcm = AESGCM(aes_key)

try:

    image_key = aes_gcm.decrypt(
        nonce,
        protected_key,
        None
    )

except Exception:

    print("\n========================================")
    print("       DECRYPTION FAILED")
    print("========================================")

    print("\nInvalid secret key!")
    print("AES-GCM authentication failed.")
    print("The image cannot be decrypted.")

    raise SystemExit


print("\nAES-GCM authentication successful!")
print("256-bit image encryption key recovered!")
print("Image key size:", len(image_key), "bytes")


# ============================================================
# STEP 6: REGENERATE LOGISTIC MAP PARAMETERS
# ============================================================

key_number = int.from_bytes(
    image_key,
    byteorder="big"
)

x0 = (key_number % 1000000) / 1000000

if x0 == 0:
    x0 = 0.000001

r = 3.9999

print("\nLogistic Map parameters regenerated!")
print("x0:", x0)
print("r:", r)


# ============================================================
# STEP 7: REGENERATE CHAOTIC SEQUENCE
# ============================================================

total_values = encrypted_array.size

chaotic_sequence = np.zeros(
    total_values,
    dtype=np.float64
)

chaotic_sequence[0] = x0

for i in range(1, total_values):

    chaotic_sequence[i] = (
        r
        * chaotic_sequence[i - 1]
        * (1 - chaotic_sequence[i - 1])
    )

print("\nChaotic sequence regenerated successfully!")
print("Sequence length:", len(chaotic_sequence))


# ============================================================
# STEP 8: REGENERATE CHAOTIC BYTE VALUES
# ============================================================

chaotic_bytes = np.mod(
    np.floor(chaotic_sequence * 1000000),
    256
).astype(np.uint8)

print("Chaotic byte sequence regenerated successfully!")


# ============================================================
# STEP 9: INVERSE BACKWARD DIFFUSION
# ============================================================

backward_diffused = encrypted_array.flatten()

mixed_pixels = np.zeros(
    total_values,
    dtype=np.uint8
)


# Reverse encryption:
#
# backward_diffused[-1] =
#     mixed_pixels[-1] + chaotic_bytes[-1]
#
# Therefore:
#
# mixed_pixels[-1] =
#     backward_diffused[-1] - chaotic_bytes[-1]

mixed_pixels[-1] = (
    int(backward_diffused[-1])
    - int(chaotic_bytes[-1])
) % 256


for i in range(total_values - 2, -1, -1):

    mixed_pixels[i] = (
        int(backward_diffused[i])
        - int(backward_diffused[i + 1])
        - int(chaotic_bytes[i])
    ) % 256


print("\nInverse backward diffusion completed!")


# ============================================================
# STEP 10: INVERSE MODULAR MIXING
# ============================================================

forward_diffused = np.zeros(
    total_values,
    dtype=np.uint8
)


# Encryption:
#
# mixed_pixels[i] =
#     forward_diffused[i]
#     + chaotic_bytes[(i + 1) % total_values]
#
# Therefore:
#
# forward_diffused[i] =
#     mixed_pixels[i]
#     - chaotic_bytes[(i + 1) % total_values]

for i in range(total_values):

    forward_diffused[i] = (
        int(mixed_pixels[i])
        - int(chaotic_bytes[(i + 1) % total_values])
    ) % 256


print("Inverse modular mixing completed!")


# ============================================================
# STEP 11: INVERSE FORWARD DIFFUSION
# ============================================================

permuted_pixels = np.zeros(
    total_values,
    dtype=np.uint8
)


# Encryption:
#
# forward_diffused[0] =
#     permuted_pixels[0] + chaotic_bytes[0]
#
# Therefore:
#
# permuted_pixels[0] =
#     forward_diffused[0] - chaotic_bytes[0]

permuted_pixels[0] = (
    int(forward_diffused[0])
    - int(chaotic_bytes[0])
) % 256


for i in range(1, total_values):

    permuted_pixels[i] = (
        int(forward_diffused[i])
        - int(forward_diffused[i - 1])
        - int(chaotic_bytes[i])
    ) % 256


print("Inverse forward diffusion completed!")


# ============================================================
# STEP 12: RECREATE PIXEL PERMUTATION
# ============================================================

permutation = np.argsort(
    chaotic_sequence
)

# Encryption:
#
# permuted_pixels = flat_pixels[permutation]
#
# Therefore we use the inverse permutation.

inverse_permutation = np.argsort(
    permutation
)

original_flat = permuted_pixels[
    inverse_permutation
]

print("Inverse pixel permutation completed!")


# ============================================================
# STEP 13: RECONSTRUCT ORIGINAL IMAGE
# ============================================================

original_rgb = original_flat.reshape(
    encrypted_array.shape
)

original_bgr = cv2.cvtColor(
    original_rgb,
    cv2.COLOR_RGB2BGR
)


# ============================================================
# STEP 14: SAVE DECRYPTED IMAGE
# ============================================================

os.makedirs(
    "results",
    exist_ok=True
)

decrypted_path = "results/decrypted_image.png"

success = cv2.imwrite(
    decrypted_path,
    original_bgr
)

if not success:
    raise IOError(
        "Could not save decrypted image."
    )


print("\n========================================")
print("       DECRYPTION COMPLETED")
print("========================================")

print("Encrypted image :", encrypted_path)
print("Decrypted image :", decrypted_path)
print("Protected key   :", protected_key_path)

print("\nDecrypted image saved successfully!")
print("Saved at:", decrypted_path)


# ============================================================
# DECRYPTION PIPELINE
# ============================================================

print("\nDecryption pipeline:")

print("Encrypted PNG")
print("      ↓")
print("User Secret Key")
print("      ↓")
print("AES-GCM Verification")
print("      ↓")
print("Recover 256-bit Image Key")
print("      ↓")
print("Regenerate Logistic Chaotic Sequence")
print("      ↓")
print("Inverse Backward Diffusion")
print("      ↓")
print("Inverse Modular Mixing")
print("      ↓")
print("Inverse Forward Diffusion")
print("      ↓")
print("Inverse Pixel Permutation")
print("      ↓")
print("Original Image")