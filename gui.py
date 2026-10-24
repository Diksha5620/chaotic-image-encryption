import os
import json
import secrets
import cv2
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Chaotic Image Encryption Using AES-GCM ",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PROJECT PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(BASE_DIR, "images")
RESULTS_FOLDER = os.path.join(BASE_DIR, "results")
KEY_FOLDER = os.path.join(BASE_DIR, "key")
ORIGINAL_IMAGE = os.path.join(
    RESULTS_FOLDER, "original_image.png"
)
ENCRYPTED_IMAGE = os.path.join(
    RESULTS_FOLDER, "encrypted_image.png"
)
DECRYPTED_IMAGE = os.path.join(
    RESULTS_FOLDER, "decrypted_image.png"
)
PROTECTED_KEY_FILE = os.path.join(
    KEY_FOLDER, "protected_key.bin"
)
USER_SECRET_FILE = os.path.join(
    KEY_FOLDER, "user_secret_key.txt"
)
USERS_JSON_FILE = os.path.join(
    KEY_FOLDER, "users.json"
)

os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(KEY_FOLDER, exist_ok=True)

# ============================================================
# PERSISTENT USER DATABASE HELPERS & PASSWORD VALIDATION
# ============================================================
def load_users_db():
    if os.path.exists(USERS_JSON_FILE):
        try:
            with open(USERS_JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"admin": "Secret@123"}
    return {"admin": "Secret@123"}

def save_users_db(db):
    with open(USERS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

def check_password_strength(password):
    """Enforces strong password requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter (A-Z)."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter (a-z)."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number (0-9)."
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/~`" for c in password):
        return False, "Password must contain at least one special character (!@#$%^&*...)."
    return True, "Strong password."

# ============================================================
# CYBER PURPLE THEME & STUNNING LOGIN PORTAL CSS
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    
    .dashboard-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
        border: 1px solid #4c1d95;
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 25px;
    }
    
    .metric-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    
    .badge-secure {
        background-color: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.2);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .main-title {
        font-size: 22px;
        font-weight: 700;
        color: #ffffff;
    }
    
    .sub-category {
        font-size: 11px;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 10px;
        margin-bottom: 15px;
        color: #ffffff;
    }
    /* Gorgeous Glowing Auth Container */
    .auth-card {
        background: linear-gradient(145deg, #111827 0%, #1e1b4b 100%);
        border: 2px solid #7c3aed;
        box-shadow: 0 0 50px rgba(124, 58, 237, 0.3);
        border-radius: 24px;
        padding: 40px;
        margin-top: 30px;
    }
    .stButton>button[kind="primary"] {
        background-color: #7c3aed;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        width: 100%;
        padding: 10px;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #6d28d9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE & AUTHENTICATION
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "users_db" not in st.session_state:
    st.session_state.users_db = load_users_db()
if "encrypted_result" not in st.session_state:
    st.session_state.encrypted_result = None
if "decrypted_result" not in st.session_state:
    st.session_state.decrypted_result = None
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠 Dashboard"

# ============================================================
# STUNNING REDESIGNED LOGIN / SIGNUP PORTAL
# ============================================================
if not st.session_state.authenticated:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown(
            """
            <div class="auth-card">
                <div style="text-align: center; margin-bottom: 25px;">
                    <div style="font-size: 44px; margin-bottom: 10px; filter: drop-shadow(0 0 12px rgba(124,58,237,0.6));">🛡️</div>
                    <h1 style="color: #ffffff; font-size: 30px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 4px;">Chaotic Image Encryption</h1>
                    <h1 style="color: #ffffff; font-size: 30px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 4px;">Chaotic image encryption using AES-GCM</h1>
                    <p style="color: #c084fc; font-size: 11px; text-transform: uppercase; letter-spacing: 2.5px; font-weight: 600;">Secure Image Protection Gateway</p>
                </div>
            unsafe_allow_html=True
        )
        
        tab_login, tab_signup = st.tabs(["🔐 Secure Sign In", "✨ Register Account"])
        
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            login_user = st.text_input("Username", key="l_user", placeholder="Enter username")
            login_pass = st.text_input("Password", type="password", key="l_pass", placeholder="Enter password")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Authenticate Session", type="primary", key="btn_l"):
                db = st.session_state.users_db
                if login_user in db and db[login_user] == login_pass:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("⚠️ Invalid username or password.")
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            new_user = st.text_input("Choose Username", key="s_user", placeholder="Create username")
            new_pass = st.text_input("Choose Password", type="password", key="s_pass", placeholder="Create password")
            st.caption("Password requirements: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Create Permanent Account", key="btn_s"):
                if not new_user or not new_pass:
                    st.warning("⚠️ Please fill in all fields.")
                elif new_user in st.session_state.users_db:
                    st.error("⚠️ Username already exists. Choose another.")
                else:
                    is_strong, msg = check_password_strength(new_pass)
                    if not is_strong:
                        st.error(f"⚠️ Weak Password: {msg}")
                    else:
                        st.session_state.users_db[new_user] = new_pass
                        save_users_db(st.session_state.users_db)
                        st.success("🎉 Account successfully saved! Switch to 'Secure Sign In' to log in.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================================================
# HELPER FUNCTIONS (True Native Resolution Preserved)
# ============================================================
def load_uploaded_image(uploaded_file):
    data = np.frombuffer(
        uploaded_file.getvalue(),
        dtype=np.uint8
    )
    image_bgr = cv2.imdecode(
        data,
        cv2.IMREAD_COLOR
    )
    if image_bgr is None:
        raise ValueError(
            "The selected file is not a valid image."
        )
    return cv2.cvtColor(
        image_bgr,
        cv2.COLOR_BGR2RGB
    )

def save_rgb_image(image_rgb, path):
    image_bgr = cv2.cvtColor(
        image_rgb,
        cv2.COLOR_RGB2BGR
    )
    if not cv2.imwrite(path, image_bgr):
        raise IOError(
            "Could not save image."
        )

def generate_chaotic_sequence(image_key, total_values):
    key_number = int.from_bytes(
        image_key,
        byteorder="big"
    )
    x0 = (
        key_number % 1000000
    ) / 1000000
    if x0 == 0:
        x0 = 0.000001
    r = 3.9999
    
    sequence = np.empty(total_values, dtype=np.float64)
    sequence[0] = x0
    for i in range(1, total_values):
        prev = sequence[i - 1]
        sequence[i] = r * prev * (1.0 - prev)
    return sequence, x0, r

# ============================================================
# OPTIMIZED VECTORIZED ENCRYPTION
# ============================================================
def encrypt_image(image_rgb):
    image = np.asarray(image_rgb, dtype=np.uint8)
    original_shape = image.shape
    total_values = image.size
    image_key = secrets.token_bytes(32)
    
    chaotic_sequence, x0, r = generate_chaotic_sequence(
        image_key,
        total_values
    )
    
    flat_pixels = image.flatten()
    permutation = np.argsort(chaotic_sequence)
    permuted = flat_pixels[permutation]
    
    chaotic_bytes = np.mod(
        np.floor(chaotic_sequence * 1000000),
        256
    ).astype(np.uint8)
    forward = np.empty_like(permuted)
    forward[0] = (int(permuted[0]) + int(chaotic_bytes[0])) % 256
    
    f_val = int(forward[0])
    for i in range(1, total_values):
        f_val = (int(permuted[i]) + f_val + int(chaotic_bytes[i])) % 256
        forward[i] = f_val
    shifted_bytes = np.roll(chaotic_bytes, 1)
    mixed = (forward.astype(np.uint16) + shifted_bytes.astype(np.uint16)) % 256
    mixed = mixed.astype(np.uint8)
    backward = np.empty_like(mixed)
    backward[-1] = (int(mixed[-1]) + int(chaotic_bytes[-1])) % 256
    
    b_val = int(backward[-1])
    for i in range(total_values - 2, -1, -1):
        b_val = (int(mixed[i]) + b_val + int(chaotic_bytes[i])) % 256
        backward[i] = b_val
    encrypted = backward.reshape(original_shape)
    user_secret_key = secrets.token_bytes(32)
    user_secret_text = user_secret_key.hex().upper()
    aes_gcm = AESGCM(user_secret_key)
    nonce = secrets.token_bytes(12)
    protected_key = aes_gcm.encrypt(nonce, image_key, None)
    protected_key_text = (nonce + protected_key).hex().upper()
    with open(PROTECTED_KEY_FILE, "wb") as file:
        file.write(nonce)
        file.write(protected_key)
    with open(USER_SECRET_FILE, "w", encoding="utf-8") as file:
        file.write(user_secret_text)
    save_rgb_image(image, ORIGINAL_IMAGE)
    save_rgb_image(encrypted, ENCRYPTED_IMAGE)
    return (
        encrypted,
        user_secret_text,
        protected_key_text,
        x0,
        r,
        total_values
    )

# ============================================================
# OPTIMIZED VECTORIZED DECRYPTION
# ============================================================
def decrypt_image(
    encrypted_rgb,
    secret_key_text,
    protected_key_text
):
    try:
        secret_key = bytes.fromhex(secret_key_text.strip())
    except ValueError:
        raise ValueError("Secret key must contain hexadecimal characters only.")
    if len(secret_key) != 32:
        raise ValueError("Secret key must contain exactly 64 hexadecimal characters.")
    try:
        protected_data = bytes.fromhex(protected_key_text.strip())
    except ValueError:
        raise ValueError("Protected key must contain hexadecimal characters only.")
    if len(protected_data) <= 12:
        raise ValueError("Protected key is too short to be valid.")
    nonce = protected_data[:12]
    protected_key = protected_data[12:]
    aes_gcm = AESGCM(secret_key)
    try:
        image_key = aes_gcm.decrypt(nonce, protected_key, None)
    except Exception:
        raise ValueError("Incorrect secret key or protected key. AES-GCM authentication failed.")
    encrypted = np.asarray(encrypted_rgb, dtype=np.uint8)
    original_shape = encrypted.shape
    total_values = encrypted.size
    chaotic_sequence, x0, r = generate_chaotic_sequence(
        image_key,
        total_values
    )
    chaotic_bytes = np.mod(
        np.floor(chaotic_sequence * 1000000),
        256
    ).astype(np.uint8)
    backward = encrypted.flatten()
    mixed = np.empty_like(backward)
    mixed[-1] = (int(backward[-1]) - int(chaotic_bytes[-1])) % 256
    
    for i in range(total_values - 2, -1, -1):
        diff = int(backward[i]) - int(backward[i + 1]) - int(chaotic_bytes[i])
        mixed[i] = diff % 256
    shifted_bytes = np.roll(chaotic_bytes, 1)
    forward = (mixed.astype(np.int32) - shifted_bytes.astype(np.int32)) % 256
    forward = forward.astype(np.uint8)
    permuted = np.empty_like(forward)
    permuted[0] = (int(forward[0]) - int(chaotic_bytes[0])) % 256
    
    for i in range(1, total_values):
        diff = int(forward[i]) - int(forward[i - 1]) - int(chaotic_bytes[i])
        permuted[i] = diff % 256
    permutation = np.argsort(chaotic_sequence)
    inverse_permutation = np.argsort(permutation)
    original_flat = permuted[inverse_permutation]
    decrypted = original_flat.reshape(original_shape)
    save_rgb_image(decrypted, DECRYPTED_IMAGE)
    return (
        decrypted,
        x0,
        r,
        total_values
    )

# ============================================================
# ANALYSIS FUNCTIONS & FILE GENERATORS
# ============================================================
def to_grayscale(image):
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(
        image,
        cv2.COLOR_RGB2GRAY
    )

def calculate_entropy(image):
    histogram = cv2.calcHist(
        [image],
        [0],
        None,
        [256],
        [0, 256]
    ).flatten()
    total = histogram.sum()
    if total == 0:
        return 0.0
    probability = histogram / total
    probability = probability[probability > 0]
    return float(-np.sum(probability * np.log2(probability)))

def calculate_correlation(image):
    x = image[:, :-1].flatten()
    y = image[:, 1:].flatten()
    if len(x) == 0:
        return 0.0
    return float(np.corrcoef(x.astype(float), y.astype(float))[0, 1])

def image_properties(image):
    return {
        "Width": image.shape[1],
        "Height": image.shape[0],
        "Minimum intensity": int(np.min(image)),
        "Maximum intensity": int(np.max(image)),
        "Mean intensity": float(np.mean(image)),
        "Standard deviation": float(np.std(image))
    }

def run_and_save_analysis():
    original_bgr = cv2.imread(ORIGINAL_IMAGE, cv2.IMREAD_UNCHANGED)
    encrypted_bgr = cv2.imread(ENCRYPTED_IMAGE, cv2.IMREAD_UNCHANGED)
    decrypted_bgr = cv2.imread(DECRYPTED_IMAGE, cv2.IMREAD_UNCHANGED)
    if original_bgr is None or encrypted_bgr is None or decrypted_bgr is None:
        raise ValueError("One or more images could not be loaded.")
    original = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2RGB)
    encrypted = cv2.cvtColor(encrypted_bgr, cv2.COLOR_BGR2RGB)
    decrypted = cv2.cvtColor(decrypted_bgr, cv2.COLOR_BGR2RGB)
    orig_gray = to_grayscale(original)
    enc_gray = to_grayscale(encrypted)
    dec_gray = to_grayscale(decrypted)
    
    # 1. Save original_histogram.png
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(orig_gray.flatten(), bins=256, color='blue', alpha=0.7, range=(0, 256))
    ax.set_title("Original Image Histogram")
    ax.set_xlabel("Pixel Intensity")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FOLDER, "original_histogram.png"))
    plt.close(fig)
    
    # 2. Save encrypted_histogram.png
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(enc_gray.flatten(), bins=256, color='purple', alpha=0.7, range=(0, 256))
    ax.set_title("Encrypted Image Histogram")
    ax.set_xlabel("Pixel Intensity")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FOLDER, "encrypted_histogram.png"))
    plt.close(fig)
    
    # 3. Save decrypted_histogram.png
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(dec_gray.flatten(), bins=256, color='green', alpha=0.7, range=(0, 256))
    ax.set_title("Decrypted Image Histogram")
    ax.set_xlabel("Pixel Intensity")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FOLDER, "decrypted_histogram.png"))
    plt.close(fig)
    
    # 4. Save entropy_graph.png
    fig, ax = plt.subplots(figsize=(6, 4))
    ent_orig = calculate_entropy(orig_gray)
    ent_enc = calculate_entropy(enc_gray)
    ent_dec = calculate_entropy(dec_gray)
    ax.bar(["Original", "Encrypted", "Decrypted"], [ent_orig, ent_enc, ent_dec], color=['blue', 'purple', 'green'])
    ax.set_xlabel("Image Stage")
    ax.set_ylabel("Shannon Entropy")
    ax.set_title("Shannon Entropy Comparison")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FOLDER, "entropy_graph.png"))
    plt.close(fig)
    
    # 5. Save correlation_graph.png
    fig, ax = plt.subplots(figsize=(6, 4))
    sample_indices = np.random.choice(orig_gray[:, :-1].size, size=min(2000, orig_gray[:, :-1].size), replace=False)
    orig_x = orig_gray[:, :-1].flatten()[sample_indices]
    orig_y = orig_gray[:, 1:].flatten()[sample_indices]
    ax.scatter(orig_x, orig_y, s=1, color='blue', alpha=0.5)
    ax.set_title("Adjacent Pixel Correlation (Original)")
    ax.set_xlabel("Pixel Intensity I(x, y)")
    ax.set_ylabel("Adjacent Pixel Intensity I(x+1, y)")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_FOLDER, "correlation_graph.png"))
    plt.close(fig)
    
    # 6. Metrics calculation
    props_orig = image_properties(orig_gray)
    props_enc = image_properties(enc_gray)
    props_dec = image_properties(dec_gray)
    
    corr_orig = calculate_correlation(orig_gray)
    corr_enc = calculate_correlation(enc_gray)
    corr_dec = calculate_correlation(dec_gray)
    
    report_content = f"""=== CHAOTIC STATISTICAL ANALYSIS REPORT ===
[Grayscale Properties]
Original Image: {props_orig}
Encrypted Image: {props_enc}
Decrypted Image: {props_dec}
[Shannon Entropy]
Original Entropy: {ent_orig:.6f}
Encrypted Entropy: {ent_enc:.6f}
Decrypted Entropy: {ent_dec:.6f}
[Adjacent Pixel Correlation]
Original Correlation: {corr_orig:.6f}
Encrypted Correlation: {corr_enc:.6f}
Decrypted Correlation: {corr_dec:.6f}
"""
    with open(os.path.join(RESULTS_FOLDER, "analysis_results.txt"), "w", encoding="utf-8") as f:
        f.write(report_content)
    return (
        original, encrypted, decrypted,
        props_orig, props_enc, props_dec,
        ent_orig, ent_enc, ent_dec,
        corr_orig, corr_enc, corr_dec
    )

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 10px 0px 20px 0px;">
            <div class="sub-category"> IMAGE PROTECTION</div>
            <div class="main-title">Chaotic Image Encryption</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    pages = ["🏠 Dashboard", "🔐 Encryption", "🔓 Decryption", "📊 Security Analysis"]
    curr_index = pages.index(st.session_state.nav_page) if st.session_state.nav_page in pages else 0
    
    selected_page = st.radio(
        "Navigation",
        pages,
        index=curr_index,
        label_visibility="collapsed"
    )
    st.session_state.nav_page = selected_page
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
        
    st.markdown(
        """
        <hr style="border-color: #1f2937;">
        <div style="font-size: 11px; color: #9ca3af; display: flex; align-items: center; gap: 6px;">
            <span style="height: 8px; width: 8px; background-color: #34d399; border-radius: 50%; display: inline-block;"></span>
            System Interface Online
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# MAIN PAGE ROUTING
# ============================================================
if st.session_state.nav_page == "🏠 Dashboard":
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
                <div class="sub-category"> IMAGE PROTECTION</div>
                <h1 style="margin: 0; font-size: 28px; color: #ffffff;">Security Dashboard</h1>
            </div>
            <div>
                <span class="badge-secure">● SECURE INTERFACE</span>
            </div>
        </div>
        
        <div class="dashboard-banner">
            <div style="max-width: 65%;">
                <div style="color: #c084fc; font-weight: 600; font-size: 12px; margin-bottom: 8px;">WELCOME TO CHAOSCRYPT</div>
                <h2 style="color: #ffffff; font-size: 26px; margin-top: 0; margin-bottom: 10px;">Protect your images.<br>Secure your data.</h2>
                <p style="color: #9ca3af; font-size: 13px; margin-bottom: 18px;">Chaotic Image Encryption using AES-GCM and Logistic Maps for ultimate privacy protection.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("### Security Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            '<div class="metric-card"><div class="sub-category">ENCRYPTION ALGORITHM</div><h3 style="color:#ffffff; margin:8px 0 4px 0; font-size:18px;">AES-GCM</h3><p style="font-size:11px; color:#9ca3af; margin:0;">Authenticated encryption</p></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<div class="metric-card"><div class="sub-category">IMAGE PROCESSING</div><h3 style="color:#ffffff; margin:8px 0 4px 0; font-size:18px;">Image Based</h3><p style="font-size:11px; color:#9ca3af; margin:0;">One image at a time</p></div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '<div class="metric-card"><div class="sub-category">KEY MANAGEMENT</div><h3 style="color:#ffffff; margin:8px 0 4px 0; font-size:18px;">Secure Key</h3><p style="font-size:11px; color:#9ca3af; margin:0;">Required for decryption</p></div>',
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            '<div class="metric-card"><div class="sub-category">SYSTEM STATUS</div><h3 style="color:#34d399; margin:8px 0 4px 0; font-size:18px;">Ready</h3><p style="font-size:11px; color:#9ca3af; margin:0;">Frontend operational</p></div>',
            unsafe_allow_html=True
        )
    st.markdown("### Quick Actions")
    qcol1, qcol2 = st.columns(2)
    with qcol1:
        st.markdown(
            '<div class="metric-card"><b>Encrypt an Image</b><p style="font-size:12px; color:#9ca3af;">Upload an image and protect it using the encryption system.</p></div>',
            unsafe_allow_html=True
        )
        if st.button("Open Encryption →", key="go_enc", type="primary"):
            st.session_state.nav_page = "🔐 Encryption"
            st.rerun()
    with qcol2:
        st.markdown(
            '<div class="metric-card"><b>Decrypt an Image</b><p style="font-size:12px; color:#9ca3af;">Restore your encrypted image using the correct key.</p></div>',
            unsafe_allow_html=True
        )
        if st.button("Open Decryption →", key="go_dec", type="primary"):
            st.session_state.nav_page = "🔓 Decryption"
            st.rerun()

elif st.session_state.nav_page == "🔐 Encryption":
    st.markdown('<div class="section-title">🔐 Image Encryption</div>', unsafe_allow_html=True)
    st.write("Select an image and encrypt it using the Logistic Map based chaotic transformation.")
    uploaded_image = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png", "bmp", "webp", "tif", "tiff"],
        key="encrypt_upload"
    )
    if uploaded_image is None:
        st.info("Please upload an image to begin encryption.")
    else:
        try:
            image_rgb = load_uploaded_image(uploaded_image)
            st.subheader("Selected Image")
            st.image(image_rgb, caption=uploaded_image.name, width=450)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Width", image_rgb.shape[1])
            with col2:
                st.metric("Height", image_rgb.shape[0])
            with col3:
                st.metric("Channels", image_rgb.shape[2])
            if st.button("🔐 Encrypt Image", type="primary", key="encrypt_button"):
                with st.spinner("Encrypting image..."):
                    (
                        encrypted,
                        secret_key,
                        protected_key_text,
                        x0,
                        r,
                        total_values
                    ) = encrypt_image(image_rgb)
                st.session_state.encrypted_result = {
                    "image": encrypted,
                    "secret_key": secret_key,
                    "protected_key": protected_key_text,
                    "x0": x0,
                    "r": r,
                    "total_values": total_values
                }
                st.session_state.decrypted_result = None
                st.success("Encryption completed successfully.")
        except Exception as error:
            st.error(f"Encryption error: {error}")
    if st.session_state.encrypted_result is not None:
        result = st.session_state.encrypted_result
        st.divider()
        st.subheader("Encrypted Image")
        st.image(result["image"], caption="Encrypted Image", width=450)
        st.subheader("🔑 Secret Key")
        st.warning("Keep this 64-character key safe. You will need it, together with the Protected Key below, to decrypt this image.")
        st.code(result["secret_key"], language="text")
        st.download_button(
            "⬇️ Download Secret Key",
            data=result["secret_key"],
            file_name="user_secret_key.txt",
            mime="text/plain",
            key="download_secret_key"
        )
        st.subheader("🛡️ Protected Key")
        st.warning("You will also need this Protected Key, together with the Secret Key above, to decrypt this image.")
        st.code(result["protected_key"], language="text")
        st.download_button(
            "⬇️ Download Protected Key",
            data=result["protected_key"],
            file_name="protected_key.txt",
            mime="text/plain",
            key="download_protected_key"
        )
        st.write(f"Logistic Map parameter x₀: {result['x0']}")
        st.write(f"Logistic Map parameter r: {result['r']}")
        st.write(f"Chaotic sequence length: {result['total_values']}")

elif st.session_state.nav_page == "🔓 Decryption":
    st.markdown('<div class="section-title">🔓 Image Decryption</div>', unsafe_allow_html=True)
    st.write("Restore your encrypted image using your Secret Key and Protected Key (either by uploading their text files or entering them).")
    encrypted_rgb = None
    source_label = None
    if st.session_state.encrypted_result is not None:
        encrypted_rgb = st.session_state.encrypted_result["image"]
        source_label = "Encrypted image from the Encrypt tab"
    elif os.path.isfile(ENCRYPTED_IMAGE):
        encrypted_bgr = cv2.imread(ENCRYPTED_IMAGE, cv2.IMREAD_UNCHANGED)
        if encrypted_bgr is not None:
            encrypted_rgb = cv2.cvtColor(encrypted_bgr, cv2.COLOR_BGR2RGB)
            source_label = "results/encrypted_image.png"
    if encrypted_rgb is None:
        st.info("Encrypt an image first — this section will then let you decrypt it.")
    else:
        st.subheader("Selected Encrypted Image")
        st.image(encrypted_rgb, caption=source_label, width=450)
        st.markdown("### 📁 Upload Key Files (Optional)")
        col_k1, col_k2 = st.columns(2)
        uploaded_secret_file = col_k1.file_uploader("Upload Secret Key File (.txt)", type=["txt"], key="up_sec")
        uploaded_protected_file = col_k2.file_uploader("Upload Protected Key File (.txt)", type=["txt"], key="up_prot")
        default_secret_key = ""
        if uploaded_secret_file is not None:
            default_secret_key = uploaded_secret_file.getvalue().decode("utf-8").strip()
        default_protected_key = ""
        if uploaded_protected_file is not None:
            default_protected_key = uploaded_protected_file.getvalue().decode("utf-8").strip()
        secret_key = st.text_input(
            "Secret Key (64 hexadecimal characters)",
            value=default_secret_key,
            type="password",
            key="decrypt_secret"
        )
        protected_key_text = st.text_input(
            "Protected Key (hexadecimal)",
            value=default_protected_key,
            type="password",
            key="decrypt_protected_key"
        )
        if st.button("🔓 Decrypt Image", type="primary", key="decrypt_button"):
            if not secret_key.strip():
                st.error("Please enter the Secret Key.")
            elif not protected_key_text.strip():
                st.error("Please enter the Protected Key.")
            else:
                with st.spinner("Decrypting image..."):
                    try:
                        (
                            decrypted,
                            x0,
                            r,
                            total_values
                        ) = decrypt_image(
                            encrypted_rgb,
                            secret_key,
                            protected_key_text
                        )
                        st.session_state.decrypted_result = {
                            "image": decrypted,
                            "x0": x0,
                            "r": r,
                            "total_values": total_values
                        }
                        st.success("Decryption completed successfully.")
                    except Exception as error:
                        st.error(f"Decryption failed: {error}")
        if st.session_state.decrypted_result is not None:
            result = st.session_state.decrypted_result
            st.divider()
            st.subheader("Decrypted Image")
            st.image(result["image"], caption="Decrypted Image", width=450)
            if os.path.isfile(DECRYPTED_IMAGE):
                with open(DECRYPTED_IMAGE, "rb") as file:
                    st.download_button(
                        "⬇️ Download Decrypted Image",
                        data=file,
                        file_name="decrypted_image.png",
                        mime="image/png",
                        key="download_decrypted"
                    )

elif st.session_state.nav_page == "📊 Security Analysis":
    st.markdown('<div class="section-title">📊 Security & Statistical Analysis</div>', unsafe_allow_html=True)
    st.write("Compare the original, encrypted, and decrypted images using statistical analysis.")
    if not os.path.isfile(ORIGINAL_IMAGE) or not os.path.isfile(ENCRYPTED_IMAGE) or not os.path.isfile(DECRYPTED_IMAGE):
        st.warning("Please complete both encryption and decryption cycles first to populate analysis data.")
    else:
        if st.button("📊 Run Analysis & Save Files", type="primary", key="run_analysis"):
            with st.spinner("Calculating image analysis and generating artifact files..."):
                try:
                    (
                        original, encrypted, decrypted,
                        props_orig, props_enc, props_dec,
                        ent_orig, ent_enc, ent_dec,
                        corr_orig, corr_enc, corr_dec
                    ) = run_and_save_analysis()
                    st.success("Analysis complete! All files generated in results folder.")
                    
                    st.text(
                        "Files created in results folder:\n"
                        "1. original_histogram.png\n"
                        "2. encrypted_histogram.png\n"
                        "3. decrypted_histogram.png\n"
                        "4. entropy_graph.png\n"
                        "5. correlation_graph.png\n"
                        "6. analysis_results.txt\n\n"
                        "No original/encrypted/decrypted image was modified."
                    )
                    st.markdown("### Image Comparison")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.image(original, caption="Original", width=250)
                    with col2:
                        st.image(encrypted, caption="Encrypted", width=250)
                    with col3:
                        st.image(decrypted, caption="Decrypted", width=250)
                    st.markdown("### Grayscale Properties")
                    prop_table = {
                        "Property": list(props_orig.keys()),
                        "Original": list(props_orig.values()),
                        "Encrypted": list(props_enc.values()),
                        "Decrypted": list(props_dec.values())
                    }
                    st.table(prop_table)
                    st.markdown("### Shannon Entropy")
                    ecol1, ecol2, ecol3 = st.columns(3)
                    ecol1.metric("Original Entropy", f"{ent_orig:.6f}")
                    ecol2.metric("Encrypted Entropy", f"{ent_enc:.6f}")
                    ecol3.metric("Decrypted Entropy", f"{ent_dec:.6f}")
                    st.markdown("### Adjacent Pixel Correlation")
                    ccol1, ccol2, ccol3 = st.columns(3)
                    ccol1.metric("Original Correlation", f"{corr_orig:.6f}")
                    ccol2.metric("Encrypted Correlation", f"{corr_enc:.6f}")
                    ccol3.metric("Decrypted Correlation", f"{corr_dec:.6f}")
                    st.markdown("### Visual Analysis & Graphs")
                    gcol1, gcol2, gcol3 = st.columns(3)
                    with gcol1:
                        st.image(os.path.join(RESULTS_FOLDER, "original_histogram.png"), caption="Original Histogram")
                    with gcol2:
                        st.image(os.path.join(RESULTS_FOLDER, "encrypted_histogram.png"), caption="Encrypted Histogram")
                    with gcol3:
                        st.image(os.path.join(RESULTS_FOLDER, "decrypted_histogram.png"), caption="Decrypted Histogram")
                    gcol4, gcol5 = st.columns(2)
                    with gcol4:
                        st.image(os.path.join(RESULTS_FOLDER, "entropy_graph.png"), caption="Shannon Entropy Comparison")
                    with gcol5:
                        st.image(os.path.join(RESULTS_FOLDER, "correlation_graph.png"), caption="Correlation Graph")
                except Exception as error:
                    st.error(f"Analysis error: {error}")
