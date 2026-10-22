import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# PROJECT FOLDERS
# ============================================================

PROJECT_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

IMAGES_FOLDER = os.path.join(
    PROJECT_FOLDER, "images"
)

RESULTS_FOLDER = os.path.join(
    PROJECT_FOLDER, "results"
)

os.makedirs(RESULTS_FOLDER, exist_ok=True)


# ============================================================
# FIND ORIGINAL IMAGE AUTOMATICALLY
# ============================================================

if not os.path.isdir(IMAGES_FOLDER):
    raise FileNotFoundError(
        "The 'images' folder was not found."
    )

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff"
)

image_files = [
    file for file in os.listdir(IMAGES_FOLDER)
    if file.lower().endswith(IMAGE_EXTENSIONS)
]

if len(image_files) == 0:
    raise FileNotFoundError(
        "No supported image was found in the images folder."
    )

original_file = image_files[0]

if len(image_files) > 1:
    print(
        "More than one image found."
    )
    print(
        "Using:",
        original_file
    )

original_path = os.path.join(
    IMAGES_FOLDER,
    original_file
)


# ============================================================
# ENCRYPTED AND DECRYPTED IMAGE PATHS
# ============================================================

encrypted_path = os.path.join(
    RESULTS_FOLDER,
    "encrypted_image.png"
)

decrypted_path = os.path.join(
    RESULTS_FOLDER,
    "decrypted_image.png"
)


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

if not os.path.isfile(encrypted_path):
    raise FileNotFoundError(
        "encrypted_image.png was not found in the results folder."
    )

if not os.path.isfile(decrypted_path):
    raise FileNotFoundError(
        "decrypted_image.png was not found in the results folder."
    )


# ============================================================
# LOAD IMAGES
# ============================================================

original = cv2.imread(
    original_path,
    cv2.IMREAD_UNCHANGED
)

encrypted = cv2.imread(
    encrypted_path,
    cv2.IMREAD_UNCHANGED
)

decrypted = cv2.imread(
    decrypted_path,
    cv2.IMREAD_UNCHANGED
)


if original is None:
    raise ValueError(
        "Original image could not be loaded."
    )

if encrypted is None:
    raise ValueError(
        "Encrypted image could not be loaded."
    )

if decrypted is None:
    raise ValueError(
        "Decrypted image could not be loaded."
    )


# ============================================================
# CONVERT TO GRAYSCALE FOR ANALYSIS
# ============================================================

def to_grayscale(image):

    # Already grayscale
    if len(image.shape) == 2:
        return image

    # One channel
    if image.shape[2] == 1:
        return image[:, :, 0]

    # Three-channel colour image
    if image.shape[2] == 3:
        return cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    # Four-channel image with transparency
    if image.shape[2] == 4:
        return cv2.cvtColor(
            image,
            cv2.COLOR_BGRA2GRAY
        )

    raise ValueError(
        "Unsupported image format."
    )


original_gray = to_grayscale(original)
encrypted_gray = to_grayscale(encrypted)
decrypted_gray = to_grayscale(decrypted)


# ============================================================
# GRAYSCALE PROPERTIES
# ============================================================

def grayscale_properties(image):

    return {
        "Width": image.shape[1],
        "Height": image.shape[0],
        "Minimum intensity": int(np.min(image)),
        "Maximum intensity": int(np.max(image)),
        "Mean intensity": float(np.mean(image)),
        "Standard deviation": float(np.std(image))
    }


original_gray_properties = grayscale_properties(
    original_gray
)

encrypted_gray_properties = grayscale_properties(
    encrypted_gray
)

decrypted_gray_properties = grayscale_properties(
    decrypted_gray
)


# ============================================================
# ENTROPY
# ============================================================

def calculate_entropy(image):

    histogram = cv2.calcHist(
        [image],
        [0],
        None,
        [256],
        [0, 256]
    ).flatten()

    total_pixels = histogram.sum()

    if total_pixels == 0:
        return 0.0

    probability = histogram / total_pixels

    probability = probability[
        probability > 0
    ]

    entropy = -np.sum(
        probability * np.log2(probability)
    )

    return float(entropy)


original_entropy = calculate_entropy(
    original_gray
)

encrypted_entropy = calculate_entropy(
    encrypted_gray
)

decrypted_entropy = calculate_entropy(
    decrypted_gray
)


# ============================================================
# CORRELATION
# ============================================================

def calculate_correlation(image):

    if image.shape[1] < 2:
        return 0.0

    x = image[:, :-1].flatten().astype(
        np.float64
    )

    y = image[:, 1:].flatten().astype(
        np.float64
    )

    if np.std(x) == 0 or np.std(y) == 0:
        return 0.0

    correlation = np.corrcoef(
        x,
        y
    )[0, 1]

    if not np.isfinite(correlation):
        return 0.0

    return float(correlation)


original_correlation = calculate_correlation(
    original_gray
)

encrypted_correlation = calculate_correlation(
    encrypted_gray
)

decrypted_correlation = calculate_correlation(
    decrypted_gray
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n==========================================")
print("          IMAGE ANALYSIS RESULTS")
print("==========================================")

print("\nOriginal image:")
print(original_file)


print("\n---------- GRAYSCALE PROPERTIES ----------")

print("\nOriginal:")
print(
    "Size:",
    original_gray_properties["Width"],
    "x",
    original_gray_properties["Height"]
)
print(
    "Minimum intensity:",
    original_gray_properties["Minimum intensity"]
)
print(
    "Maximum intensity:",
    original_gray_properties["Maximum intensity"]
)
print(
    "Mean intensity:",
    original_gray_properties["Mean intensity"]
)
print(
    "Standard deviation:",
    original_gray_properties["Standard deviation"]
)


print("\nEncrypted:")
print(
    "Size:",
    encrypted_gray_properties["Width"],
    "x",
    encrypted_gray_properties["Height"]
)
print(
    "Minimum intensity:",
    encrypted_gray_properties["Minimum intensity"]
)
print(
    "Maximum intensity:",
    encrypted_gray_properties["Maximum intensity"]
)
print(
    "Mean intensity:",
    encrypted_gray_properties["Mean intensity"]
)
print(
    "Standard deviation:",
    encrypted_gray_properties["Standard deviation"]
)


print("\nDecrypted:")
print(
    "Size:",
    decrypted_gray_properties["Width"],
    "x",
    decrypted_gray_properties["Height"]
)
print(
    "Minimum intensity:",
    decrypted_gray_properties["Minimum intensity"]
)
print(
    "Maximum intensity:",
    decrypted_gray_properties["Maximum intensity"]
)
print(
    "Mean intensity:",
    decrypted_gray_properties["Mean intensity"]
)
print(
    "Standard deviation:",
    decrypted_gray_properties["Standard deviation"]
)


print("\n---------- ENTROPY ----------")

print(
    "Original  :",
    original_entropy
)

print(
    "Encrypted :",
    encrypted_entropy
)

print(
    "Decrypted :",
    decrypted_entropy
)


print("\n---------- CORRELATION ----------")

print(
    "Original  :",
    original_correlation
)

print(
    "Encrypted :",
    encrypted_correlation
)

print(
    "Decrypted :",
    decrypted_correlation
)


# ============================================================
# HISTOGRAM FUNCTION
# ============================================================

def create_histogram(
    image,
    title,
    filename
):

    plt.figure(
        figsize=(8, 5)
    )

    plt.hist(
        image.flatten(),
        bins=256,
        range=(0, 256)
    )

    plt.title(title)

    plt.xlabel(
        "Pixel Intensity"
    )

    plt.ylabel(
        "Frequency"
    )

    plt.xlim(
        0,
        256
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            RESULTS_FOLDER,
            filename
        ),
        dpi=300
    )

    plt.close()


# ============================================================
# CREATE HISTOGRAMS
# ============================================================

create_histogram(
    original_gray,
    "Original Grayscale Histogram",
    "original_histogram.png"
)

create_histogram(
    encrypted_gray,
    "Encrypted Grayscale Histogram",
    "encrypted_histogram.png"
)

create_histogram(
    decrypted_gray,
    "Decrypted Grayscale Histogram",
    "decrypted_histogram.png"
)


# ============================================================
# ENTROPY GRAPH
# ============================================================

plt.figure(
    figsize=(7, 5)
)

plt.bar(
    [
        "Original",
        "Encrypted",
        "Decrypted"
    ],
    [
        original_entropy,
        encrypted_entropy,
        decrypted_entropy
    ]
)

plt.title(
    "Entropy Comparison"
)

plt.ylabel(
    "Entropy"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULTS_FOLDER,
        "entropy_graph.png"
    ),
    dpi=300
)

plt.close()


# ============================================================
# CORRELATION GRAPH
# ============================================================

plt.figure(
    figsize=(7, 5)
)

plt.bar(
    [
        "Original",
        "Encrypted",
        "Decrypted"
    ],
    [
        original_correlation,
        encrypted_correlation,
        decrypted_correlation
    ]
)

plt.title(
    "Correlation Comparison"
)

plt.ylabel(
    "Correlation"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULTS_FOLDER,
        "correlation_graph.png"
    ),
    dpi=300
)

plt.close()


# ============================================================
# SAVE ALL RESULTS TO TXT
# ============================================================

txt_path = os.path.join(
    RESULTS_FOLDER,
    "analysis_results.txt"
)

with open(
    txt_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "IMAGE ANALYSIS RESULTS\n"
    )

    file.write(
        "======================\n\n"
    )

    file.write(
        "Original Image: "
        + original_file
        + "\n\n"
    )

    # --------------------------------------------------------
    # GRAYSCALE PROPERTIES
    # --------------------------------------------------------

    file.write(
        "GRAYSCALE PROPERTIES\n"
    )

    file.write(
        "----------------------\n"
    )

    file.write(
        "\nOriginal:\n"
    )

    for key, value in original_gray_properties.items():
        file.write(
            key + ": " + str(value) + "\n"
        )

    file.write(
        "\nEncrypted:\n"
    )

    for key, value in encrypted_gray_properties.items():
        file.write(
            key + ": " + str(value) + "\n"
        )

    file.write(
        "\nDecrypted:\n"
    )

    for key, value in decrypted_gray_properties.items():
        file.write(
            key + ": " + str(value) + "\n"
        )

    # --------------------------------------------------------
    # ENTROPY
    # --------------------------------------------------------

    file.write(
        "\n\nENTROPY\n"
    )

    file.write(
        "----------------------\n"
    )

    file.write(
        "Original  : "
        + str(original_entropy)
        + "\n"
    )

    file.write(
        "Encrypted : "
        + str(encrypted_entropy)
        + "\n"
    )

    file.write(
        "Decrypted : "
        + str(decrypted_entropy)
        + "\n"
    )

    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    file.write(
        "\nCORRELATION\n"
    )

    file.write(
        "----------------------\n"
    )

    file.write(
        "Original  : "
        + str(original_correlation)
        + "\n"
    )

    file.write(
        "Encrypted : "
        + str(encrypted_correlation)
        + "\n"
    )

    file.write(
        "Decrypted : "
        + str(decrypted_correlation)
        + "\n"
    )


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n==========================================")
print("          ANALYSIS COMPLETED")
print("==========================================")

print("\nFiles created in results folder:")

print("1. original_histogram.png")
print("2. encrypted_histogram.png")
print("3. decrypted_histogram.png")
print("4. entropy_graph.png")
print("5. correlation_graph.png")
print("6. analysis_results.txt")

print("\nNo original/encrypted/decrypted image was modified.")