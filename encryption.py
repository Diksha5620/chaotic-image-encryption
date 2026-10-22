# Chaotic Image Encryption Using AES-GCM
# Combined Encryption Program - Phase 1
# ============================================================
import os
import cv2
import numpy as np
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

if os.path.exists("results/encrypted_image.png"):
    print("Encrypted image already exists.")
    print("Delete it first if you want to encrypt a new image.")
    exit()
# ============================================================
# STEP 1: LOAD IMAGE
# ============================================================
image_folder = "images"
image_files = os.listdir(image_folder)

if len(image_files) == 0:
    raise FileNotFoundError("No image found in the images folder.")

image_name = image_files[0]
image_path = os.path.join(image_folder, image_name)

image = cv2.imread(image_path)

if image is None:
    raise ValueError("Image could not be loaded.")
print("Image loaded successfully!")
print("Image name:",image_name)    
# ============================================================
# STEP 2: CONVERT BGR TO RGB
# ============================================================
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pixel_array = np.array(image)
print("Image size:", image.shape)
print("Pixel array shape:", pixel_array.shape)
# ============================================================
# STEP 3: GENERATE RANDOM 256-BIT IMAGE ENCRYPTION KEY
# ============================================================
image_key = secrets.token_bytes(32)
print("\n256-bit image key generated successfully!")
print("Key size:", len(image_key), "bytes")
# ============================================================
# STEP 4: GENERATE LOGISTIC MAP PARAMETERS
# ============================================================
key_number = int.from_bytes(image_key, byteorder="big")
x0 = (key_number % 1000000) / 1000000
if x0 == 0:
  x0 = 0.000001
r = 3.9999
print("\nLogistic Map parameters generated!")
print("x0:", x0)
print("r:", r)
# ============================================================
# STEP 5: GENERATE LOGISTIC CHAOTIC SEQUENCE
# ============================================================
total_values = pixel_array.size
chaotic_sequence = np.zeros(total_values, dtype=np.float64)
chaotic_sequence[0] = x0
for i in range(1, total_values):
 chaotic_sequence[i] = (
  r
  * chaotic_sequence[i - 1]
  * (1 - chaotic_sequence[i - 1])
)
print("\nChaotic sequence generated successfully!")
print("Sequence length:", len(chaotic_sequence))
# ============================================================
# STEP 6: CHAOTIC PIXEL PERMUTATION
# ============================================================
flat_pixels = pixel_array.flatten()
permutation = np.argsort(chaotic_sequence)
permuted_pixels = flat_pixels[permutation]
print("\nPixel permutation completed!")
# ============================================================
# STEP 7: CONVERT CHAOTIC SEQUENCE TO BYTE VALUES
# ============================================================
chaotic_bytes = np.mod(
 np.floor(chaotic_sequence * 1000000),
 256
).astype(np.uint8)
# ============================================================
# STEP 8: FORWARD DIFFUSION
# ============================================================
forward_diffused = np.zeros(
 total_values,
 dtype=np.uint8
)
forward_diffused[0] = (
 int(permuted_pixels[0])
 + int(chaotic_bytes[0])
) % 256
for i in range(1, total_values):
 forward_diffused[i] = (
  int(permuted_pixels[i])
  + int(forward_diffused[i - 1])
  + int(chaotic_bytes[i])
) % 256
print("Forward diffusion completed!")
# ============================================================
# STEP 9: MODULAR MIXING
# ============================================================
mixed_pixels = np.zeros(
 total_values,
 dtype=np.uint8
)
for i in range(total_values):
 mixed_pixels[i] = (
  int(forward_diffused[i])
  + int(chaotic_bytes[(i + 1) % total_values])
) % 256
print("Modular mixing completed!")
# ============================================================
# STEP 10: BACKWARD DIFFUSION
# ============================================================
backward_diffused = np.zeros(
 total_values,
 dtype=np.uint8
)
backward_diffused[-1] = (
 int(mixed_pixels[-1])
 + int(chaotic_bytes[-1])
) % 256
for i in range(total_values - 2, -1, -1):
 backward_diffused[i] = (
  int(mixed_pixels[i])
  + int(backward_diffused[i + 1])
  + int(chaotic_bytes[i])
) % 256
print("Backward diffusion completed!")
# ============================================================
# STEP 11: CREATE AND SAVE ENCRYPTED IMAGE
# ============================================================
encrypted_image = backward_diffused.reshape(
 pixel_array.shape
)
os.makedirs("results", exist_ok=True)
encrypted_bgr = cv2.cvtColor(
 encrypted_image,
 cv2.COLOR_RGB2BGR
)
encrypted_path = "results/encrypted_image.png"
cv2.imwrite(
 encrypted_path,
 encrypted_bgr
)
print("\nEncrypted image saved successfully!")
print("Saved at:", encrypted_path)
# ============================================================
# STEP 12: GENERATE USER SECRET KEY
# ============================================================

print("\n========================================")
print(" SECRET KEY GENERATION")
print("========================================")

# Generate a random 256-bit secret key for the user
user_secret_key = secrets.token_bytes(32)

# Convert to readable hexadecimal form
user_secret_text = user_secret_key.hex().upper()

print("\nSecret key generated successfully!")
print("SAVE THIS SECRET KEY:")
print(user_secret_text)


# ============================================================
# STEP 13: AES-GCM KEY PROTECTION
# ============================================================

# The generated 256-bit user secret is used as the AES-256 key.
aes_key = user_secret_key

aes_gcm = AESGCM(aes_key)

# AES-GCM requires a unique nonce.
nonce = secrets.token_bytes(12)

# Protect the randomly generated image encryption key.
protected_key = aes_gcm.encrypt(
    nonce,
    image_key,
    None
)

print("\nAES-GCM key protection completed!")


# ============================================================
# STEP 14: SAVE PROTECTED KEY INFORMATION
# ============================================================

os.makedirs("key", exist_ok=True)

# Save nonce + protected image key.
with open("key/protected_key.bin", "wb") as file:
    file.write(nonce)
    file.write(protected_key)

# Save the user's secret key in a text file ONLY for local testing.
# In the final website, we should NOT store this file automatically.
with open("key/user_secret_key.txt", "w") as file:
    file.write(user_secret_text)

print("Protected key saved successfully!")
print("User secret key saved for testing.")
# ============================================================
# FINAL OUTPUT
# ============================================================
print("\n========================================")
print(" ENCRYPTION COMPLETED")
print("========================================")
print("Original image :", image_path)
print("Encrypted image:", encrypted_path)
print("Secret key file : key/user_secret_key.txt")
print("Protected key   : key/protected_key.bin")
print("Original Image")
print(" ¯")
print("RGB Pixel Array")
print(" ¯")
print("Random 256-bit Image Key")
print(" ¯")
print("Logistic Chaotic Sequence")
print(" ¯")
print("Chaotic Pixel Permutation")
print(" ¯")
print("Forward Diffusion")
print(" ¯")
print("Modular Mixing")
print(" ¯")
print("Backward Diffusion")
print(" ¯")
print("Encrypted PNG")
print(" ¯")
print("AES-GCM Key Protection")
print(" ¯")
print("Protected Key")
