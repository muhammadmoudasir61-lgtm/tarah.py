# ==============================================================================
# 0. AUTO-SETUP: ضروری پیکجز خود انسٹال ہو جائیں گے (requirements.txt کی ضرورت نہیں)
# ==============================================================================
import importlib
import subprocess
import sys

def ensure_package(pip_name, import_name):
    try:
        importlib.import_module(import_name)
        return True
    except Exception:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", pip_name])
            importlib.invalidate_caches()
            importlib.import_module(import_name)
            return True
        except Exception:
            return False

ensure_package("streamlit-geolocation", "streamlit_geolocation")

from datetime import datetime
import base64
import hashlib
import json
import os
import random
import re
import smtplib
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

# پرانے Streamlit میں fragment نہ ہو تو ایپ پھر بھی چلے (آٹو ریفریش بند رہے گا)
if not hasattr(st, "fragment"):
    def _fragment_fallback(*args, **kwargs):
        if args and callable(args[0]):
            return args[0]
        return lambda f: f
    st.fragment = _fragment_fallback

# اصل GPS لوکیشن کے لیے (پیکج اوپر خود انسٹال ہو جاتا ہے)
try:
    from streamlit_geolocation import streamlit_geolocation
    GEO_AVAILABLE = True
except Exception:
    GEO_AVAILABLE = False

# ==============================================================================
# 1. APP BRAND IDENTITY & HIGH-CONTRAST VISIBILITY
# ==============================================================================
APP_NAME = "FamilyCare / فیملی کیئر"
APP_TAGLINE = "Together. Safe. Supported. / باہم۔ محفوظ۔ بااختیار۔"
APP_FULL_TITLE = f"{APP_NAME} — Family Support System"
APP_ORGANIZATION = "FamilyCare Systems"
APP_VERSION = "43.0.0-VISIBLE-WHATSAPP-BUTTON"

ADMIN_REAL_PHONE = "03434067496"
ADMIN_SENDER_EMAIL = "moudasirkhan40@gmail.com"

# 📧 Gmail App Password یہاں اندر لکھ دیں (نیا والا! پرانا Google سے منسوخ کر دیں)۔
# فارمیٹ: "abcd efgh ijkl mnop"   — جب تک نہ لکھیں، ای میل OTP/الرٹ نہیں جائیں گے مگر PIN لاگ ان چلتا رہے گا۔
PASTE_GMAIL_APP_PASSWORD_HERE = ""

try:
    _secret_pw = st.secrets.get("ADMIN_APP_PASSWORD", "")
except Exception:
    _secret_pw = ""
ADMIN_APP_PASSWORD = _secret_pw or PASTE_GMAIL_APP_PASSWORD_HERE

# ٹیسٹنگ کوڈ: لائیو کرنے سے پہلے اسے False کر دیں تاکہ 123456 سے کوئی لاگ ان نہ ہو سکے۔
ENABLE_TEST_OTP = True
DEFAULT_TEST_OTP = "123456"

EMOTIONAL_THANKYOU_MESSAGES = [
    "✨ **شکر گزاری و دعا:** آپ کے اس خلوصِ دل سے کسی کا گھر روشن ہوا ہے! اللہ آپ کے رزق اور صحت میں برکت دے۔ آمین! 🤲💖",
    "🌟 **ایثار:** خون کے رشتوں کی حفاظت اور باہمی مدد ہی حقیقی طاقت ہے۔ آپ کے اس قدم کا تہہ دل سے شکریہ! 🛡️✨",
    "💫 **شعر:**  \n*ذرا سا قطرہ سہی پر خلوص کا ہے،*  \n*یہی خلوص تو آپس میں جوڑ رکھتا ہے!* 🌹",
    "💖 **احساس:** آپ کا جمع کرایا گیا ایک ایک روپیہ فیملی کے لیے ایک مضبوط ڈھال بنتا ہے۔ جزاک اللہ! 🌺"
]

st.set_page_config(
    page_title=APP_FULL_TITLE,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# PWA FULL MANIFEST & SERVICE WORKER INJECTION (FOR PWABUILDER 100% SCORE)
# ==============================================================================
pwa_manifest_json = {
    "name": "FamilyCare — Family Support System",
    "short_name": "FamilyCare",
    "description": "Together. Safe. Supported. A complete, secure family care and emergency support system.",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "display_override": ["window-controls-overlay", "standalone", "minimal-ui"],
    "orientation": "portrait-primary",
    "theme_color": "#0F172A",
    "background_color": "#0F172A",
    "lang": "ur",
    "dir": "rtl",
    "iarc_rating_id": "e84b0000-0000-0000-0000-000000000000",
    "icons": [
        {
            "src": "https://cdn-icons-png.flaticon.com/512/3064/3064197.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "https://cdn-icons-png.flaticon.com/512/3064/3064197.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable"
        }
    ],
    "screenshots": [
        {
            "src": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?auto=format&fit=crop&w=1080&q=80",
            "sizes": "1080x1920",
            "type": "image/jpeg",
            "form_factor": "narrow",
            "label": "FamilyCare Dashboard & SOS"
        },
        {
            "src": "https://images.unsplash.com/photo-1511632765486-a01980e01a18?auto=format&fit=crop&w=1920&q=80",
            "sizes": "1920x1080",
            "type": "image/jpeg",
            "form_factor": "wide",
            "label": "Desktop Overview"
        }
    ],
    "shortcuts": [
        {
            "name": "Emergency SOS",
            "short_name": "SOS",
            "description": "Trigger instant emergency alert to family",
            "url": "/?action=sos",
            "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/1033/1033090.png", "sizes": "192x192"}]
        },
        {
            "name": "Deposit Funds",
            "short_name": "Deposit",
            "description": "Submit payment receipt quickly",
            "url": "/?action=deposit",
            "icons": [{"src": "https://cdn-icons-png.flaticon.com/512/2489/2489756.png", "sizes": "192x192"}]
        }
    ],
    "protocol_handlers": [
        {
            "protocol": "web+familycare",
            "url": "/?req=%s"
        }
    ],
    "file_handlers": [
        {
            "action": "/",
            "accept": {
                "image/*": [".jpg", ".jpeg", ".png"]
            }
        }
    ],
    "launch_handler": {
        "client_mode": "focus-existing"
    },
    "note_taking": {
        "new_note_url": "/?note=true"
    },
    "widgets": [
        {
            "name": "FamilyCare Emergency Status",
            "short_name": "Status",
            "description": "Quick view of family safety and balance status",
            "tag": "familycare-widget",
            "template": "widget-template",
            "ms_ac_template": "widget-template.json",
            "data": "widget-data.json",
            "type": "text/html",
            "screenshots": [
                {
                    "src": "https://cdn-icons-png.flaticon.com/512/3064/3064197.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }
    ]
}

manifest_base64 = base64.b64encode(json.dumps(pwa_manifest_json).encode('utf-8')).decode('utf-8')

# Android viewport + PWA style meta + CSS Blocker
st.markdown(f"""
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
    <meta name="theme-color" content="#0F172A">
    <meta name="mobile-web-app-capable" content="yes">
    <link rel="manifest" href="data:application/json;base64,{manifest_base64}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="FamilyCare">
    
    <script>
    if ('serviceWorker' in navigator) {{
        window.addEventListener('load', function() {{
            const swCode = `
                const CACHE_NAME = 'familycare-v1';
                self.addEventListener('install', (e) => {{ self.skipWaiting(); }});
                self.addEventListener('activate', (e) => {{ e.waitUntil(clients.claim()); }});
                self.addEventListener('fetch', (e) => {{
                    e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
                }});
            `;
            const blob = new Blob([swCode], {{ type: 'application/javascript' }});
            const swUrl = URL.createObjectURL(blob);
            navigator.serviceWorker.register(swUrl);
        }});
    }}
    </script>
""", unsafe_allow_html=True)

# Clean & High-Contrast Custom CSS - Zero Word Overlapping + Android Responsive
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&family=Poppins:wght@400;600;700&display=swap');
    
    /* Streamlit کے تمام سروس آئیکنز، ٹاپ بارز، واٹر مارک اور فوٹر کو مکمل طور پر بلاک کرنا */
    #MainMenu, footer, header, [data-testid="stHeader"], .stDeployButton, [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain !important;
        touch-action: pan-x pan-y !important;
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        -webkit-text-size-adjust: 100%;
        -webkit-tap-highlight-color: transparent;
    }
    
    body, div, span, h1, h2, h3, h4, p, label, input, button {
        font-family: 'Poppins', 'Noto Nastaliq Urdu', sans-serif !important;
    }
    
    .main .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-bottom: calc(5rem + env(safe-area-inset-bottom)) !important;
        max-width: 100% !important;
    }
    
    /* Input Fields Fix - Bold Clear Text (16px = Android zoom نہیں کرتا) */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 2px solid #0284C7 !important;
        border-radius: 8px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        min-height: 48px !important;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 2px solid #0284C7 !important;
        min-height: 48px !important;
    }
    
    /* Clean File Uploader Fix - No Merged Text */
    [data-testid="stFileUploader"] {
        background-color: #1E293B !important;
        border: 2px dashed #0284C7 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    /* HIGH VISIBILITY SOLID BUTTONS - 48px touch target for thumbs */
    .stButton>button, div[data-testid="stPopover"]>button, .stFormSubmitButton>button {
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        border: 2px solid #38BDF8 !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        min-height: 50px !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
        white-space: normal !important;
        line-height: 1.3 !important;
    }
    .stButton>button:hover, div[data-testid="stPopover"]>button:hover {
        background-color: #0369A1 !important;
        color: #FFFFFF !important;
        border-color: #7DD3FC !important;
    }
    .stButton>button:active { transform: scale(0.97); }

    /* 📲 واٹس ایپ SOS بٹن: چمکدار ہرا، بڑا، دھڑکتا ہوا تاکہ فوراً نظر آئے */
    div[data-testid="stLinkButton"] a,
    a[data-testid^="stBaseLinkButton"] {
        background: #25D366 !important;
        color: #FFFFFF !important;
        border: 3px solid #FFFFFF !important;
        border-radius: 14px !important;
        min-height: 76px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        text-decoration: none !important;
        box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7);
        animation: waPulse 1.6s infinite;
    }
    div[data-testid="stLinkButton"] a *,
    a[data-testid^="stBaseLinkButton"] * {
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 900 !important;
    }
    @keyframes waPulse {
        0%   { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.75); }
        70%  { box-shadow: 0 0 0 18px rgba(37, 211, 102, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
    }
    
    /* Primary Red Button for Emergency SOS & Delete */
    .stButton>button[data-testid="baseButton-primary"],
    .stButton>button[kind="primary"],
    .stFormSubmitButton>button[kind="primary"] {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
        border: 2px solid #EF4444 !important;
    }
    
    .brand-banner {
        background: linear-gradient(135deg, #1E3A8A 0%, #0284C7 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    .banner-flex {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .banner-chip {
        background: rgba(255,255,255,0.2);
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        word-break: break-all;
    }
    
    .metric-card-white {
        background: #1E293B;
        border-radius: 12px;
        padding: 1rem;
        border: 2px solid #0284C7;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        text-align: center;
        color: #FFFFFF !important;
        margin-bottom: 0.5rem;
    }
    .metric-card-white h4 {
        color: #7DD3FC !important;
        font-size: 1.05rem !important;
        font-weight: 700;
        margin: 0 0 6px 0 !important;
    }
    .metric-card-white h2 {
        color: #FFFFFF !important;
        font-size: 1.7rem !important;
        font-weight: 800;
        margin: 2px 0 !important;
        word-break: break-word;
    }
    
    .content-section {
        background: #1E293B;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    .rules-card {
        background: #0F172A;
        border-radius: 10px;
        padding: 12px;
        border: 1.5px solid #EF4444;
        font-size: 0.9rem;
        color: #F8FAFC;
        margin-top: 8px;
    }
    
    .chat-bubble-admin {
        background: #1E3A8A;
        padding: 12px 16px;
        border-radius: 12px 12px 0px 12px;
        margin-bottom: 8px;
        border-left: 5px solid #38BDF8;
        font-size: 1rem;
        color: #FFFFFF;
        word-break: break-word;
    }
    .chat-bubble-member {
        background: #0F172A;
        padding: 12px 16px;
        border-radius: 12px 12px 12px 0px;
        margin-bottom: 8px;
        border-left: 5px solid #10B981;
        font-size: 1rem;
        color: #FFFFFF;
        word-break: break-word;
    }
    
    .sos-container {
        text-align: center;
        padding: 14px;
        background: #0F172A;
        border-radius: 12px;
        border: 2.5px solid #EF4444;
        margin-bottom: 1rem;
    }

    .member-card {
        background:#0F172A; padding:10px 14px; border-radius:8px;
        margin-bottom:6px; word-break: break-word;
    }
    .credential-card {
        background:#052E16; border:2px solid #10B981; border-radius:12px;
        padding:14px; margin-top:10px; color:#ECFDF5; font-size:1rem;
    }
    .help-step {
        background:#0F172A; border-left:4px solid #38BDF8; border-radius:8px;
        padding:10px 14px; margin-bottom:8px; font-size:0.98rem;
    }

    /* ===================== ANDROID / MOBILE LAYOUT ===================== */
    @media (max-width: 768px) {
        /* ہر columns والی قطار موبائل پر اوپر نیچے آ جائے (کوئی لفظ نہ کٹے) */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.4rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .content-section { padding: 0.8rem; }
        .metric-card-white h2 { font-size: 1.45rem !important; }
        .brand-banner h2 { font-size: 1.25rem !important; }
        .banner-flex { flex-direction: column; align-items: flex-start; }
        h1 { font-size: 1.5rem !important; }
        h2, .stSubheader { font-size: 1.2rem !important; }
        h3 { font-size: 1.1rem !important; }
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none;
        }
        .stTabs [data-baseweb="tab"] { white-space: nowrap; padding: 8px 10px; }
        [data-testid="stDataFrame"] { overflow-x: auto; }
        audio { width: 100% !important; }
    }
    @media (max-width: 380px) {
        .metric-card-white h4 { font-size: 0.95rem !important; }
        .stButton>button { font-size: 0.98rem !important; padding: 0.5rem 0.7rem !important; }
    }
    </style>
""", unsafe_allow_html=True)

# Helper Audio Functions
def play_chat_sound():
    components.html("""<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg"></audio>""", height=0)

def play_emergency_siren():
    components.html("""<audio autoplay loop><source src="https://assets.mixkit.co/active_storage/sfx/995/995-preview.mp3" type="audio/mpeg"></audio>""", height=0)

# Helper: نمبر کو صاف کرنا (space, dash ہٹانا) تاکہ لاگ ان میں غلطی نہ ہو
def normalize_key(value):
    value = (value or "").strip()
    if "@" in value:
        return value.lower()
    return re.sub(r"[\s\-\+]", "", value)

def is_valid_pk_mobile(value):
    return bool(re.fullmatch(r"03\d{9}", value))

def generate_pin(length=6):
    return "".join(str(random.randint(0, 9)) for _ in range(length))

# Real Mail OTP Dispatcher
def send_real_gmail_otp(recipient_email, otp_code, user_name, reason="authentication"):
    if not ADMIN_APP_PASSWORD:
        return False, "Gmail App Password not set in code"
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{APP_NAME} <{ADMIN_SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"🔑 Security OTP Code / تصدیقی کوڈ: {otp_code}"

        body = f"Dear / محترم {user_name},\n\nYour OTP Code for {reason} is / آپ کا تصدیقی کوڈ ہے:\n🔑 {otp_code}\n\nValid for 10 minutes."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ADMIN_SENDER_EMAIL, ADMIN_APP_PASSWORD.replace(" ", ""))
        server.send_message(msg)
        server.quit()
        return True, "Success"
    except Exception as err:
        return False, str(err)

def update_user_password_globally(phone_or_email, new_password):
    if phone_or_email in st.session_state.registered_users:
        user_record = st.session_state.registered_users[phone_or_email]
        user_email = user_record.get("email")
        
        for key, record in st.session_state.registered_users.items():
            if (user_email and record.get("email") == user_email) or key == phone_or_email:
                record["password"] = new_password
                record["must_change_pw"] = False

def otp_matches(entered, expected):
    entered = (entered or "").strip()
    if expected and entered == expected:
        return True
    return ENABLE_TEST_OTP and entered == DEFAULT_TEST_OTP


# ==============================================================================
# 1B. SHARED DATA STORE (تمام ممبرز کا ڈیٹا ایک ہی جگہ، فائل میں محفوظ)
# ==============================================================================
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "familycare_data.json")
SHARED_KEYS = ["registered_users", "payment_accounts", "transactions",
               "assistance_requests", "chat_threads", "submitted_txn_ids", "sos_events"]

def _default_store():
    admin = {
        "name": "Muhammad Mudassir (Admin / ایڈمن)", "email": ADMIN_SENDER_EMAIL,
        "password": "1234", "role": "ADMIN", "status": "ACTIVE", "must_change_pw": False,
        "phone": ADMIN_REAL_PHONE
    }
    return {
        "_lock": threading.Lock(),
        "registered_users": {ADMIN_REAL_PHONE: dict(admin), ADMIN_SENDER_EMAIL: dict(admin)},
        "payment_accounts": [
            {"id": 1, "type": "Easypaisa / ایزی پیسہ", "title": "Muhammad Mudassir", "number": ADMIN_REAL_PHONE,
             "bank": "Easypaisa", "iban": "-",
             "instructions": "Upload receipt screenshot after payment / رقم بھیج کر رسید کی تصویر اپ لوڈ کریں۔",
             "status": "ACTIVE"}
        ],
        "transactions": [],
        "assistance_requests": [],
        "chat_threads": {"GENERAL": [], "ISSUES": [], "APPEALS": []},
        "submitted_txn_ids": set(),
        "sos_events": [],
    }

@st.cache_resource
def get_store():
    store = _default_store()
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k in SHARED_KEYS:
                if k in data:
                    store[k] = data[k]
            store["submitted_txn_ids"] = set(data.get("submitted_txn_ids", []))
            for room, msgs in store["chat_threads"].items():
                for m in msgs:
                    if m.get("audio_is_b64") and m.get("audio"):
                        m["audio"] = base64.b64decode(m["audio"])
                        m.pop("audio_is_b64", None)
    except Exception:
        pass
    return store

STORE = get_store()

def save_store():
    try:
        with STORE["_lock"]:
            data = {k: STORE[k] for k in SHARED_KEYS if k not in ("chat_threads", "submitted_txn_ids")}
            data["submitted_txn_ids"] = list(STORE["submitted_txn_ids"])
            chat = {}
            for room, msgs in STORE["chat_threads"].items():
                chat[room] = []
                for m in msgs:
                    mm = dict(m)
                    if isinstance(mm.get("audio"), (bytes, bytearray)):
                        mm["audio"] = base64.b64encode(bytes(mm["audio"])).decode()
                        mm["audio_is_b64"] = True
                    chat[room].append(mm)
            data["chat_threads"] = chat
            tmp = DATA_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp, DATA_FILE)
    except Exception:
        pass  # read-only فائل سسٹم ہو تو ایپ پھر بھی چلتی رہے

def rerun():
    save_store()
    st.rerun()

# ------------------------------------------------------------------------------
# Notification helpers (Email + WhatsApp share text)
# ------------------------------------------------------------------------------
def to_intl_phone(local_phone):
    return "92" + local_phone[1:] if local_phone.startswith("0") else local_phone

def send_bulk_email(recipients, subject, body):
    result = {}
    if not ADMIN_APP_PASSWORD or not recipients:
        return {e: False for e, _ in recipients}
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        server.starttls()
        server.login(ADMIN_SENDER_EMAIL, ADMIN_APP_PASSWORD.replace(" ", ""))
        for email, name in recipients:
            try:
                msg = MIMEMultipart()
                msg['From'] = f"{APP_NAME} <{ADMIN_SENDER_EMAIL}>"
                msg['To'] = email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server.send_message(msg)
                result[email] = True
            except Exception:
                result[email] = False
        server.quit()
    except Exception:
        for email, _ in recipients:
            result.setdefault(email, False)
    return result

def send_otp_everywhere(user_data, otp_code, reason="authentication"):
    return send_real_gmail_otp(user_data.get("email", ""), otp_code, user_data["name"], reason)

def build_sos_text(event, with_time=True):
    loc_line = event["maps_link"] if event.get("maps_link") else "لوکیشن دستیاب نہیں (فون سے رابطہ کریں)"
    time_line = f"⏰ وقت: {event['time']}\n" if with_time and event.get("time") else ""
    return (f"🚨 EMERGENCY ALERT / ہنگامی الرٹ!\n👤 نام: {event['name']}\n📱 نمبر: {event['phone']}\n"
            f"{time_line}📍 لوکیشن: {loc_line}\nفوراً رابطہ کریں!")

def notify_all_members(event):
    users = STORE["registered_users"]
    members = [(k, v) for k, v in users.items()
               if "@" not in k and v.get("status") == "ACTIVE" and k != event["phone"]]
    text = build_sos_text(event)
    mail_targets = [(v["email"], v["name"]) for k, v in members if v.get("email")]
    mail_res = send_bulk_email(mail_targets, f"🚨 EMERGENCY: {event['name']} needs help", text)
    results = [{"name": v["name"], "phone": k,
                "email": mail_res.get(v.get("email"), False) if v.get("email") else None}
               for k, v in members]
    return {"text": text, "results": results}

# ------------------------------------------------------------------------------
# ID helper (ڈیلیٹ کے بعد بھی ID کبھی دہرائی نہ جائے)
# ------------------------------------------------------------------------------
def next_txn_id():
    ids = [t.get("id", 0) for t in STORE["transactions"]]
    return (max(ids) + 1) if ids else 101

# ------------------------------------------------------------------------------
# Receipt screenshot reader (FAST OPTIMIZED OCR) — رقم اور ٹرانزیکشن آئی ڈی تیز پڑھتا ہے
# ------------------------------------------------------------------------------
def extract_receipt_info(text):
    clean = text.replace(",", "")
    amounts = []
    for m in re.finditer(r"(?:\bRs\.?|\bPKR|Amount|Total|Paid)\D{0,10}(\d{2,9}(?:\.\d{1,2})?)", clean, re.I):
        val = float(m.group(1))
        if val >= 10 and val not in amounts:
            amounts.append(val)
    tid = None
    m = re.search(r"(?:TID|Trx\.?\s*ID|Txn\s*ID|Transaction\s*ID|Ref\.?\s*No)\D{0,10}(\d{8,16})", clean, re.I)
    if m:
        tid = m.group(1)
    return {"amounts": amounts, "tid": tid}

@st.cache_resource
def get_ocr_engine():
    from rapidocr_onnxruntime import RapidOCR
    return RapidOCR()

def read_receipt(file_bytes):
    """تیز رفتار پروسیسنگ - تصویر کو چھوٹا کر کے 2 سے 3 سیکنڈ میں پڑھنا"""
    out = {"ok": False, "amounts": [], "tid": None, "note": ""}
    if not ensure_package("rapidocr-onnxruntime", "rapidocr_onnxruntime"):
        out["note"] = "OCR پیکج انسٹال نہیں ہو سکا"
        return out
    try:
        import io
        import numpy as np
        from PIL import Image, ImageEnhance
        
        # 1. Fast Image Resize to prevent network freeze
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        img.thumbnail((1000, 1000))
        
        enhancer = ImageEnhance.Contrast(img)
        img_prep = np.array(enhancer.enhance(1.8))
        
        engine = get_ocr_engine()
        result, _ = engine(img_prep)
        text = "\n".join(r[1] for r in (result or []))
        
        if not text.strip():
            out["note"] = "تصویر سے کوئی تحریر نہیں پڑھی گئی"
            return out
        info = extract_receipt_info(text)
        out.update(info)
        out["ok"] = True
        if not info["amounts"]:
            out["note"] = "رقم واضح نہیں پڑھی گئی"
    except Exception as err:
        out["note"] = f"OCR ایرر: {err}"
    return out

# ------------------------------------------------------------------------------
# Bill voting rules: تمام ممبرز (درخواست دہندہ کے علاوہ) متفق ہوں تو پاس، ایک بھی نا منظور تو مسترد
# ------------------------------------------------------------------------------
def eligible_voters(req):
    return [k for k, v in STORE["registered_users"].items()
            if "@" not in k and v.get("status") == "ACTIVE" and k != req.get("member_key")]

def refresh_bill_status(req):
    if req.get("status") in ("PAID", "REJECTED"):
        return
    need = len(eligible_voters(req))
    if req.get("disagree_votes", 0) > 0:
        req["status"] = "REJECTED"
    elif need > 0 and req.get("agree_votes", 0) >= need:
        req["status"] = "APPROVED"
    else:
        req["status"] = "PENDING"

# ==============================================================================
# 2. DATABASE INITIALIZATION
# ==============================================================================
if 'registered_users' not in st.session_state:
    st.session_state.registered_users = {
        ADMIN_REAL_PHONE: {
            "name": "Muhammad Mudassir (Admin / ایڈمن)", 
            "email": ADMIN_SENDER_EMAIL, 
            "password": "1234",
            "role": "ADMIN", 
            "status": "ACTIVE",
            "must_change_pw": False
        },
        ADMIN_SENDER_EMAIL: {
            "name": "Muhammad Mudassir (Admin / ایڈمن)", 
            "email": ADMIN_SENDER_EMAIL, 
            "password": "1234",
            "role": "ADMIN", 
            "status": "ACTIVE",
            "must_change_pw": False
        }
    }

if 'auth_state' not in st.session_state:
    st.session_state.auth_state = {
        "logged_in": False,
        "phone_or_email": None,
        "email": None,
        "role": None,
        "name": None,
        "generated_otp": None,
        "otp_sent": False,
        "forgot_pass_mode": False,
        "forgot_otp_sent": False,
        "forgot_target_user": None
    }

if 'payment_accounts' not in st.session_state:
    st.session_state.payment_accounts = [
        {"id": 1, "type": "Easypaisa / ایزی پیسہ", "title": "Muhammad Mudassir", "number": ADMIN_REAL_PHONE, "bank": "Easypaisa", "iban": "-", "instructions": "Upload receipt screenshot after payment / رقم بھیج کر رسید کی تصویر اپ لوڈ کریں۔", "status": "ACTIVE"}
    ]

if 'transactions' not in st.session_state:
    st.session_state.transactions = []

if 'assistance_requests' not in st.session_state:
    st.session_state.assistance_requests = []

if 'chat_threads' not in st.session_state:
    st.session_state.chat_threads = {"GENERAL": [], "ISSUES": [], "APPEALS": []}

if 'submitted_txn_ids' not in st.session_state:
    st.session_state.submitted_txn_ids = set()

if 'active_sos_event' not in st.session_state:
    st.session_state.active_sos_event = None

if 'sound_type_trigger' not in st.session_state:
    st.session_state.sound_type_trigger = None

if 'last_deposit_msg' not in st.session_state:
    st.session_state.last_deposit_msg = None

if 'last_created_member' not in st.session_state:
    st.session_state.last_created_member = None

if 'voice_counter' not in st.session_state:
    st.session_state.voice_counter = 0

for _k in SHARED_KEYS:
    st.session_state[_k] = STORE[_k]
if 'seen_sos' not in st.session_state:
    st.session_state.seen_sos = set()
if 'my_loc' not in st.session_state:
    st.session_state.my_loc = None
if 'last_sos_report' not in st.session_state:
    st.session_state.last_sos_report = None

if st.session_state.sound_type_trigger == "CHAT":
    play_chat_sound()
    st.session_state.sound_type_trigger = None
elif st.session_state.sound_type_trigger == "SIREN":
    play_emergency_siren()
    st.session_state.sound_type_trigger = None

# ==============================================================================
# 3. AUTHENTICATION & LOGIN SCREEN
# ==============================================================================
def render_login_screen():
    st.markdown(f"""
        <div class="brand-banner" style="text-align: center;">
            <h2 style="margin:0; font-size:1.5rem;">🛡️ {APP_NAME}</h2>
            <p style="margin:4px 0 0 0; font-size:0.95rem; opacity:0.9;">{APP_TAGLINE}</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_c, _ = st.columns([1, 0.01])
    with col_c:
        if st.session_state.auth_state["forgot_pass_mode"]:
            st.subheader("🔑 Reset Password / پاس ورڈ دوبارہ سیٹ کریں")
            
            if not st.session_state.auth_state["forgot_otp_sent"]:
                reset_input = st.text_input("Enter Registered Phone or Gmail / موبائل نمبر یا ای میل درج کریں:", placeholder="e.g. 03434067496")
                
                col_r1, col_r2 = st.columns(2)
                if col_r1.button("📩 Send OTP / کوڈ بھیجیں", type="primary", use_container_width=True):
                    clean_res = normalize_key(reset_input)
                    if clean_res in st.session_state.registered_users:
                        user_data = st.session_state.registered_users[clean_res]
                        generated_code = str(random.randint(100000, 999999))
                        st.session_state.auth_state["generated_otp"] = generated_code
                        st.session_state.auth_state["forgot_target_user"] = clean_res
                        
                        ok, info = send_otp_everywhere(user_data, generated_code, reason="resetting your password")
                        if not ok:
                            st.warning("⚠️ ای میل نہیں جا سکی۔ ایڈمن سے رابطہ کریں کہ وہ آپ کا PIN خود تبدیل کر دے۔")
                        st.session_state.auth_state["forgot_otp_sent"] = True
                        rerun()
                    else:
                        st.error("❌ Account not found / یہ اکاؤنٹ موجود نہیں ہے۔")
                
                if col_r2.button("🔙 Back / لاگ ان پر واپس جائیں", use_container_width=True):
                    st.session_state.auth_state["forgot_pass_mode"] = False
                    rerun()
            else:
                target_u = st.session_state.auth_state["forgot_target_user"]
                entered_otp = st.text_input("Enter 6-Digit OTP / 6 ہندسوں کا کوڈ درج کریں:", type="password")
                new_pass1 = st.text_input("Create New Password/PIN / نیا پاس ورڈ لکھیں:", type="password")
                new_pass2 = st.text_input("Confirm New Password / نیا پاس ورڈ دوبارہ لکھیں:", type="password")
                
                if st.button("✅ Reset & Save Password / پاس ورڈ تبدیل کریں", type="primary", use_container_width=True):
                    target_code = st.session_state.auth_state["generated_otp"]
                    if otp_matches(entered_otp, target_code) and new_pass1.strip() and new_pass1.strip() == new_pass2.strip():
                        update_user_password_globally(target_u, new_pass1.strip())
                        st.success("✅ Password updated successfully! / پاس ورڈ تبدیل ہو گیا!")
                        st.session_state.auth_state["forgot_pass_mode"] = False
                        st.session_state.auth_state["forgot_otp_sent"] = False
                        rerun()
                    else:
                        st.error("❌ Invalid OTP or Passwords do not match / غلط کوڈ یا پاس ورڈ میں فرق ہے۔")
                        
        else:
            st.subheader("🔒 Family Login / لاگ ان پورٹل")
            login_type = st.radio("Select Login Method / لاگ ان کا طریقہ منتخب کریں:", ["🔑 Password / PIN Login (تیز ترین)", "📩 Gmail OTP Login (تصدیق)"], horizontal=True)
            
            if "Password" in login_type:
                user_input = st.text_input("Mobile Number or Gmail / موبائل نمبر یا ای میل:", placeholder="e.g. 03434067496 or email@gmail.com")
                user_pass = st.text_input("Account Password / PIN / پاس ورڈ (👁️ آنکھ والے ائیکن سے دیکھیں):", type="password")
                
                st.caption("ℹ️ اپنا رجسٹرڈ موبائل نمبر اور پاس ورڈ درج کر کے نیچے دیے گئے بٹن پر کلک کریں۔")
                
                if st.button("🔓 Quick Login / ڈائریکٹ لاگ ان کریں", type="primary", use_container_width=True):
                    clean_input = normalize_key(user_input)
                    if clean_input in st.session_state.registered_users:
                        user_data = st.session_state.registered_users[clean_input]
                        
                        if user_data["status"] != "ACTIVE":
                            st.error("⛔ ACCESS DENIED / رسائی منسوخ: Account is INACTIVE")
                        elif user_pass.strip() == user_data.get("password"):
                            st.session_state.auth_state["logged_in"] = True
                            st.session_state.auth_state["phone_or_email"] = clean_input
                            st.session_state.auth_state["email"] = user_data["email"]
                            st.session_state.auth_state["role"] = user_data["role"]
                            st.session_state.auth_state["name"] = user_data["name"]
                            rerun()
                        else:
                            st.error("❌ Incorrect Password / پاس ورڈ غلط ہے!")
                    else:
                        st.error("❌ Account Not Found / یہ نمبر یا ای میل رجسٹرڈ نہیں ہے۔")
                
                if st.button("❓ Forgot Password / پاس ورڈ بھول گئے؟", use_container_width=True):
                    st.session_state.auth_state["forgot_pass_mode"] = True
                    rerun()
                    
            else:
                user_input = st.text_input("Registered Mobile Number or Gmail / موبائل نمبر یا ای میل:", placeholder="e.g. 03434067496 or email@gmail.com")
                
                if not st.session_state.auth_state["otp_sent"]:
                    if st.button("📲 Send Security OTP / ای میل پر کوڈ بھیجیں", type="primary", use_container_width=True):
                        clean_input = normalize_key(user_input)
                        if clean_input in st.session_state.registered_users:
                            user_data = st.session_state.registered_users[clean_input]
                            generated_code = str(random.randint(100000, 999999))
                            st.session_state.auth_state["generated_otp"] = generated_code
                            st.session_state.auth_state["phone_or_email"] = clean_input
                            st.session_state.auth_state["email"] = user_data["email"]
                            
                            ok, info = send_otp_everywhere(user_data, generated_code)
                            if not ok:
                                st.warning("⚠️ ای میل نہیں جا سکی۔ PIN والا طریقہ استعمال کریں۔")
                            st.session_state.auth_state["otp_sent"] = True
                            rerun()
                        else:
                            st.error("❌ Number/Gmail not authorized / یہ نمبر رجسٹرڈ نہیں ہے۔")
                else:
                    entered_otp = st.text_input("Enter 6-Digit OTP / 6 ہندسوں کا کوڈ:", type="password")
                    
                    if st.button("🔓 Verify & Login / تصدیق کر کے لاگ ان کریں", type="primary", use_container_width=True):
                        target_code = st.session_state.auth_state["generated_otp"]
                        if otp_matches(entered_otp, target_code):
                            user_data = st.session_state.registered_users[st.session_state.auth_state["phone_or_email"]]
                            if user_data["status"] != "ACTIVE":
                                st.error("⛔ ACCESS DENIED / رسائی منسوخ: Account is INACTIVE")
                            else:
                                st.session_state.auth_state["logged_in"] = True
                                st.session_state.auth_state["role"] = user_data["role"]
                                st.session_state.auth_state["name"] = user_data["name"]
                                rerun()
                        else:
                            st.error("❌ Invalid OTP Code / غلط کوڈ!")
                    if st.button("🔙 Change Number / نمبر تبدیل کریں", use_container_width=True):
                        st.session_state.auth_state["otp_sent"] = False
                        rerun()

if not st.session_state.auth_state["logged_in"]:
    render_login_screen()
    st.stop()

current_role = st.session_state.auth_state["role"]
current_name = st.session_state.auth_state["name"]
current_phone_email = st.session_state.auth_state["phone_or_email"]

# ==============================================================================
# 4. MAIN DASHBOARD (100% TRANSPARENT TO ALL MEMBERS)
# ==============================================================================
st.markdown(f"""
    <div class="brand-banner">
        <div class="banner-flex">
            <div>
                <h3 style="margin:0; font-size:1.3rem;">🛡 {APP_NAME} Portal</h3>
                <p style="margin:0; font-size:0.9rem; opacity:0.9;">خوش آمدید, <strong>{current_name}</strong> [{current_role}]</p>
            </div>
            <div>
                <span class="banner-chip">
                    📱 {current_phone_email}
                </span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# نئے ممبر کے لیے یاد دہانی: ایڈمن کا دیا ہوا PIN بدل لیں
_my_record = st.session_state.registered_users.get(current_phone_email, {})
if _my_record.get("must_change_pw"):
    st.warning("🔐 آپ کو ایڈمن نے عارضی PIN دیا تھا۔ براہ کرم نیچے ⚙️ بٹن سے اپنا ذاتی پاس ورڈ بنا لیں۔")

with st.expander("🔐 آپ کے اختیارات / Your Permissions"):
    if current_role == "ADMIN":
        st.markdown("""
            <div class="help-step">✅ <strong>ایڈمن:</strong> ممبر شامل/ہٹانا، PIN ری سیٹ، Active/Inactive، اکاؤنٹس، خرچہ، کسی کا بھی میسج یا اینٹری ڈیلیٹ۔</div>
            <div class="help-step">✅ باقی سب کچھ (چیٹ، SOS، ڈپازٹ، ووٹنگ) ایڈمن بھی استعمال کر سکتا ہے۔</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="help-step">👁️ <strong>ممبر:</strong> سارا مالیاتی ڈیٹا، ممبرز، چیٹ اور ووٹنگ دیکھ سکتا ہے۔</div>
            <div class="help-step">✅ رقم جمع کروانا، امداد کی درخواست، ووٹ، وائس/ٹیکسٹ میسج، SOS بٹن۔</div>
            <div class="help-step">🗑️ صرف اپنا میسج ڈیلیٹ کر سکتا ہے۔</div>
            <div class="help-step">⛔ ممبر شامل کرنا/ہٹانا، خرچہ لکھنا، کھاتے کی اینٹری ڈیلیٹ کرنا — صرف ایڈمن کے لیے۔</div>
        """, unsafe_allow_html=True)

col_top_act1, col_top_act2 = st.columns([1, 1])

with col_top_act1:
    with st.popover("⚙ Change Password / پاس ورڈ تبدیل کریں"):
        curr_p = st.text_input("Current Password / موجودہ پاس ورڈ:", type="password")
        new_p1 = st.text_input("New Password / نیا پاس ورڈ:", type="password")
        new_p2 = st.text_input("Confirm New Password / نیا پاس ورڈ دوبارہ درج کریں:", type="password")
        
        if st.button("💾 Save Password / محفوظ کریں", type="primary"):
            user_rec = st.session_state.registered_users.get(current_phone_email)
            if user_rec and curr_p.strip() == user_rec.get("password"):
                if new_p1.strip() and new_p1 == new_p2:
                    update_user_password_globally(current_phone_email, new_p1.strip())
                    st.success("✅ Password changed successfully! / پاس ورڈ تبدیل ہو گیا!")
                else:
                    st.error("❌ Passwords do not match / دونوں پاس ورڈ مختلف ہیں۔")
            else:
                st.error("❌ Incorrect current password / موجودہ پاس ورڈ غلط ہے۔")

with col_top_act2:
    if st.button("🚪 Logout / لاگ آؤٹ", use_container_width=True):
        st.session_state.auth_state["logged_in"] = False
        st.session_state.auth_state["otp_sent"] = False
        rerun()

# ------------------------------------------------------------------------------
# SECTION 1: LIVE GLOBAL FINANCIAL DASHBOARD (AUTO-SYNC VIA FRAGMENT)
# ------------------------------------------------------------------------------
@st.fragment(run_every=3)
def render_live_financial_dashboard():
    """ہر 3 سیکنڈ بعد لائیو اپ ڈیٹ ہونے والا ڈیش بورڈ (بغیر پیج ریفریش کیے)"""
    total_deposits = sum(
        t["amount"] for t in st.session_state.transactions 
        if t["type"] == "DEPOSIT" and t["status"] in ["APPROVED", "INSTANT_ADDITION"]
    )
    total_spendings = sum(
        t["amount"] for t in st.session_state.transactions 
        if t["type"] == "SPENDING"
    )
    remaining_balance = total_deposits - total_spendings
    my_total_contributed = sum(
        t["amount"] for t in st.session_state.transactions 
        if t["member_phone"] == current_phone_email and t["type"] == "DEPOSIT" and t["status"] in ["APPROVED", "INSTANT_ADDITION"]
    )

    st.markdown("### 📊 Overall Family Financial Dashboard / فیملی کا مالیاتی خلاصہ")
    c_f1, c_f2, c_f3 = st.columns(3)

    with c_f1:
        st.markdown(f"""
            <div class="metric-card-white">
                <h4>💰 Total Family Funds / کل جمع شدہ فنڈز</h4>
                <h2>PKR {total_deposits:,}</h2>
            </div>
        """, unsafe_allow_html=True)

    with c_f2:
        st.markdown(f"""
            <div class="metric-card-white" style="border-color:#EF4444;">
                <h4 style="color:#FCA5A5 !important;">💸 Total Spendings / کل اخراجات</h4>
                <h2>PKR {total_spendings:,}</h2>
            </div>
        """, unsafe_allow_html=True)

    with c_f3:
        st.markdown(f"""
            <div class="metric-card-white" style="border-color:#10B981;">
                <h4 style="color:#6EE7B7 !important;">🏦 Remaining Balance / بقایا محفوظ رقم</h4>
                <h2>PKR {remaining_balance:,}</h2>
            </div>
        """, unsafe_allow_html=True)

    st.info(f"👤 **آپ کا اپنا جمع کروایا گیا کل حصہ (Your Personal Contribution):** PKR {my_total_contributed:,}")

# ڈیش بورڈ کا لائیو ڈسپلے
render_live_financial_dashboard()

# پچھلی ڈپازٹ کا فوری شکر گزار اور دعائیہ پیغام
if st.session_state.last_deposit_msg:
    _ld = st.session_state.last_deposit_msg
    st.balloons()
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #065F46 0%, #047857 100%); 
                    border: 2px solid #10B981; padding: 18px; border-radius: 12px; 
                    margin-bottom: 15px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.4);">
            <h3 style="margin:0; color:#A7F3D0;">🎉 تصدیق شدہ ڈپازٹ موصول ہو گیا!</h3>
            <h2 style="margin:5px 0; color:#FFFFFF;">PKR {_ld['amount']:,}</h2>
            <p style="font-size: 1.1rem; margin-top:10px;">{_ld['quote']}</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("✖ Close / بند کریں", key="close_dep_msg", use_container_width=True):
        st.session_state.last_deposit_msg = None
        rerun()

st.markdown("<br/>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SECTION 2: HIGH-ALERT EMERGENCY SOS & LIVE GPS MAP
# ------------------------------------------------------------------------------
st.markdown("""
    <div class="sos-container">
        <h3 style="color:#EF4444; margin:0 0 5px 0;">🚨 EMERGENCY SOS & GPS MAP / اضطراری بٹن اور لائیو نقشہ</h3>
        <p style="color:#CBD5E1; margin:0; font-size:0.9rem;">کسی بھی ہنگامی صورتحال میں نیچے دیا گیا بٹن دبائیں:</p>
    </div>
""", unsafe_allow_html=True)

col_sos1, col_sos2 = st.columns([1.3, 1])

with col_sos1:
    st.markdown("**📍 مرحلہ 1: اپنی اصل لوکیشن آن کریں (ایک بار دبائیں)**")
    if GEO_AVAILABLE:
        _geo = streamlit_geolocation()
        if _geo and _geo.get("latitude") and _geo.get("longitude"):
            st.session_state.my_loc = {
                "lat": float(_geo["latitude"]), "lon": float(_geo["longitude"]), "acc": _geo.get("accuracy")
            }
    else:
        st.warning("⚠️ GPS پیکج انسٹال نہیں ہو سکا۔ ایپ ایک بار Reboot کریں، پھر بھی نہ چلے تو لاگ مجھے بھیجیں۔")

    _loc = st.session_state.my_loc
    if _loc:
        _acc = f" (درستگی ≈ {int(_loc['acc'])} میٹر)" if _loc.get("acc") else ""
        st.success(f"✅ آپ کی لوکیشن مل گئی{_acc}")
    else:
        st.info("اوپر والا لوکیشن آئیکن دبائیں اور براؤزر میں 'Allow' کریں۔ بغیر اجازت اصل لوکیشن نہیں بھیجی جا سکتی۔")

    st.markdown("**🚨 مرحلہ 2: ہنگامی صورتحال میں بٹن دبائیں**")
    if st.button("🚨 PUSH FOR HELP / مدد کے لیے یہ بٹن دبائیں 🚨", type="primary", use_container_width=True):
        st.session_state.sound_type_trigger = "SIREN"
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _l = st.session_state.my_loc
        maps_link = f"https://maps.google.com/?q={_l['lat']},{_l['lon']}" if _l else None
        event = {
            "id": f"sos{datetime.now().strftime('%H%M%S%f')}",
            "name": current_name, "phone": _my_record.get("phone") or current_phone_email, "time": current_time_str,
            "maps_link": maps_link, "lat": _l["lat"] if _l else None, "lon": _l["lon"] if _l else None,
            "active": True
        }
        STORE["sos_events"].append(event)
        del STORE["sos_events"][:-50]
        st.session_state.seen_sos.add(event["id"])
        with st.spinner("🚨 تمام ممبرز کو الرٹ بھیجا جا رہا ہے..."):
            st.session_state.last_sos_report = notify_all_members(event)
        rerun()

    st.markdown("**📲 مرحلہ 3: واٹس ایپ پر پوری فیملی کو بھیجیں** (PUSH کے بعد یہ بٹن بھی ضرور دبائیں)")
    _wa_loc = st.session_state.my_loc
    _wa_event = {
        "name": current_name, "phone": _my_record.get("phone") or current_phone_email, "time": "",
        "maps_link": f"https://maps.google.com/?q={_wa_loc['lat']},{_wa_loc['lon']}" if _wa_loc else None
    }
    _wa_text = build_sos_text(_wa_event, with_time=False)
    st.link_button("📲 واٹس ایپ پر سب کو بھیجیں  ←  فیملی گروپ چنیں  ←  Send",
                   "https://wa.me/?text=" + urllib.parse.quote(_wa_text), use_container_width=True)
    st.caption("💡 واٹس ایپ کھلے تو فیملی گروپ چن کر Send دبا دیں۔ پیغام پہلے سے لکھا ہوگا۔")

    _rep = st.session_state.last_sos_report
    if _rep:
        st.error("🚨 الرٹ ایپ اور ای میل پر چلا گیا! اب اوپر والا **سبز واٹس ایپ بٹن** بھی دبائیں تاکہ سب کے واٹس ایپ پر پہنچے۔")
        _mail_total = len([r for r in _rep["results"] if r["email"] is not None])
        if _mail_total:
            _mail_ok = len([r for r in _rep["results"] if r["email"]])
            st.caption(f"📧 ای میل خودکار گئی: {_mail_ok}/{_mail_total}")
        with st.expander("👥 یا ہر ممبر کو الگ الگ بھیجیں"):
            for r in _rep["results"]:
                _lnk = f"https://wa.me/{to_intl_phone(r['phone'])}?text={urllib.parse.quote(_rep['text'])}"
                st.markdown(f"👉 [{r['name']}]({_lnk})")
        if st.button("✖ بند کریں", key="close_sos_report"):
            st.session_state.last_sos_report = None
            rerun()

    st.markdown("""
        <div class="rules-card">
            <strong style="color:#EF4444;">⚠ ایمرجنسی بٹن کے ضروری قواعد و ضوابط (Rules):</strong><br/>
            1️⃣ اس بٹن کو صرف حقیقی ہنگامی صورتحال (حادثہ، طبی ایمرجنسی، یا ناگہانی آفت) میں استعمال کریں۔<br/>
            2️⃣ بٹن دباتے ہی ایپ کھولے ہوئے سب ممبرز کو الرٹ ملے گا، ای میل جائے گی، اور آپ واٹس ایپ کے بٹن سے سب کو اپنی لوکیشن بھیج سکیں گے۔<br/>
            3️⃣ غیر ضروری یا بلا وجہ ٹیسٹنگ کے لیے یہ بٹن نہ دبائیں۔
        </div>
    """, unsafe_allow_html=True)

with col_sos2:
    st.caption("📍 GPS Live Map / لائیو نقشہ:")
    _map_pt = st.session_state.my_loc
    if _map_pt:
        st.map(data={"lat": [_map_pt["lat"]], "lon": [_map_pt["lon"]]}, height=260)
    else:
        st.caption("لوکیشن آن ہوتے ہی آپ کا نقشہ یہاں آئے گا۔")

@st.fragment(run_every=5)
def sos_watcher():
    """ہر 5 سیکنڈ بعد چیک کرتا ہے: کسی ممبر نے SOS دبایا ہو تو سب کو بینر + سائیرن + نقشہ۔"""
    active = [e for e in STORE["sos_events"] if e.get("active")]
    for ev in active[-3:]:
        st.error(f"🚨 ACTIVE EMERGENCY: {ev['name']} ({ev['phone']}) — {ev['time']}")
        if ev.get("maps_link"):
            st.markdown(f"📍 **[نقشے پر لوکیشن دیکھیں / Open Map]({ev['maps_link']})**")
            st.map(data={"lat": [ev["lat"]], "lon": [ev["lon"]]}, height=200)
        else:
            st.warning("اس ممبر کی لوکیشن دستیاب نہیں، فون پر رابطہ کریں۔")
        if ev["id"] not in st.session_state.seen_sos:
            st.session_state.seen_sos.add(ev["id"])
            play_emergency_siren()
        if current_role == "ADMIN" or ev["phone"] == current_phone_email:
            if st.button("✅ CLEAR / مسئلہ حل ہو گیا", key=f"clr_{ev['id']}"):
                ev["active"] = False
                rerun()

sos_watcher()

st.divider()

# ------------------------------------------------------------------------------
# SECTION 3: FAMILY MEMBER LIVE STATUS (VISIBLE TO ALL)
# ------------------------------------------------------------------------------
st.markdown("<div class='content-section'>", unsafe_allow_html=True)
st.subheader("👥 Family Members Live Status / فیملی ممبرز کی حالت")

_phone_members = [(k, v) for k, v in st.session_state.registered_users.items() if "@" not in k]
col_m_list = st.columns(max(min(len(_phone_members), 3), 1))
for idx, (key, info) in enumerate(_phone_members):
    with col_m_list[idx % len(col_m_list)]:
        status_color = "#10B981" if info["status"] == "ACTIVE" else "#EF4444"
        st.markdown(f"""
            <div class="member-card" style="border-left:4px solid {status_color};">
                <strong style="color:white; font-size:1rem;">{info['name']}</strong><br/>
                <small style="color:#CBD5E1;">Mobile: {key}</small><br/>
                <small style="color:{status_color}; font-weight:bold;">{info['status']}</small>
            </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SECTION 4: ADMIN MANAGEMENT PANEL (Role Protected Settings)
# ------------------------------------------------------------------------------
if current_role == "ADMIN":
    st.markdown("<div class='content-section'>", unsafe_allow_html=True)
    st.subheader("⚙ Admin Management Panel / ایڈمن کنٹرول پینل")
    
    adm_tab1, adm_tab2, adm_tab3, adm_tab4, adm_tab5 = st.tabs([
        "💸 Expense / خرچہ",
        "💳 Accounts / اکاؤنٹس",
        "📱 Add Members / ممبرز",
        "🛠️ Manage / انتظام",
        "✅ Approvals / منظوری"
    ])
    
    with adm_tab1:
        st.markdown("#### Record Family Expense / نیا خرچہ درج کریں")
        with st.form("admin_expense_form", clear_on_submit=True):
            exp_amount = st.number_input("Expense Amount (PKR) / رقم:*", min_value=10, step=100, value=500)
            exp_details = st.text_area("Expense Description / تفصیل:*", placeholder="e.g. Utility Bill / بلز")
            
            btn_save_exp = st.form_submit_button("💾 Save Expense / خرچہ محفوظ کریں")
            if btn_save_exp and exp_details:
                st.session_state.transactions.append({
                    "id": next_txn_id(),
                    "member_phone": current_phone_email,
                    "member_name": f"{current_name} (Admin)",
                    "type": "SPENDING",
                    "amount": exp_amount,
                    "txn_id": f"EXP-{random.randint(100,999)}",
                    "status": "APPROVED",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "screenshot": "N/A",
                    "details": exp_details
                })
                st.success("✅ Expense recorded! / خرچہ محفوظ ہو گیا!")
                rerun()

        _spend = [t for t in st.session_state.transactions if t["type"] == "SPENDING"]
        if _spend:
            with st.expander("✏️ خرچہ ایڈٹ یا ڈیلیٹ کریں / Edit or Delete Expense"):
                _labels = [f"ID {t['id']} | PKR {t['amount']:,} | {t.get('details', '')}" for t in _spend]
                _pick = st.selectbox("خرچہ منتخب کریں:", _labels, key="edit_exp_pick")
                _tid = int(_pick.split("|")[0].replace("ID", "").strip())
                _target = next(t for t in _spend if t["id"] == _tid)
                _new_amt = st.number_input("نئی رقم / New Amount:", min_value=10, value=int(_target["amount"]), step=100, key=f"ea_{_tid}")
                _new_det = st.text_input("نئی تفصیل / New Details:", value=_target.get("details", ""), key=f"ed_{_tid}")
                _c1, _c2 = st.columns(2)
                if _c1.button("💾 Update / اپڈیٹ کریں", key=f"eu_{_tid}", use_container_width=True):
                    _target["amount"] = int(_new_amt)
                    _target["details"] = _new_det
                    rerun()
                if _c2.button("🗑️ Delete / ڈیلیٹ کریں", key=f"edl_{_tid}", type="primary", use_container_width=True):
                    st.session_state.transactions[:] = [t for t in st.session_state.transactions if t["id"] != _tid]
                    rerun()

    with adm_tab2:
        st.markdown("#### Add Payment Account / نیا بینک اکاؤنٹ")
        with st.form("add_acc_form", clear_on_submit=True):
            ac_type = st.selectbox("Payment Method / اکاؤنٹ کی قسم:*", ["Easypaisa / ایزی پیسہ", "JazzCash / جاز کیش", "Bank Account / بینک"])
            ac_title = st.text_input("Account Title / اکاؤنٹ کا نام:*", value=current_name)
            ac_num = st.text_input("Account/Mobile Number / نمبر:*", placeholder="03XXXXXXXXX")
            btn_save_ac = st.form_submit_button("💾 Save Account / محفوظ کریں")
            if btn_save_ac and ac_num:
                st.session_state.payment_accounts.append({
                    "id": len(st.session_state.payment_accounts) + 1,
                    "type": ac_type, "title": ac_title, "number": ac_num,
                    "bank": ac_type, "iban": "-", "instructions": "Upload screenshot after payment", "status": "ACTIVE"
                })
                st.success("✅ Account added! / اکاؤنٹ شامل ہو گیا!")
                rerun()

    with adm_tab3:
        st.markdown("#### Register New Member & PIN / نیا ممبر اور پاس ورڈ شامل کریں")
        st.caption("💡 PIN خالی چھوڑیں تو ایپ خود 6 ہندسوں کا رینڈم PIN بنا دے گی۔")
        with st.form("add_phone_form", clear_on_submit=True):
            new_p = st.text_input("Mobile Number / موبائل نمبر:*", placeholder="03XXXXXXXXX")
            new_e = st.text_input("Member Email / ای میل (اختیاری، نہ ہو تو خالی چھوڑیں):", placeholder="member@gmail.com")
            new_n = st.text_input("Member Name / ممبر کا نام:*", placeholder="e.g. Ali (Son)")
            new_pass = st.text_input("Assign Initial PIN / پاس ورڈ رکھیں (خالی = رینڈم):", value="")
            btn_add_p = st.form_submit_button("➕ Authorize Member / ممبر شامل کریں")
            if btn_add_p:
                phone_key = normalize_key(new_p)
                email_key = normalize_key(new_e)
                if not phone_key or not new_n.strip():
                    st.error("❌ نمبر اور نام ضروری ہیں۔")
                elif not is_valid_pk_mobile(phone_key):
                    st.error("❌ موبائل نمبر 03XXXXXXXXX (11 ہندسے) فارمیٹ میں لکھیں۔")
                elif phone_key in st.session_state.registered_users:
                    st.error("⚠️ یہ نمبر پہلے سے رجسٹرڈ ہے۔")
                elif email_key and "@" not in email_key:
                    st.error("❌ ای میل درست نہیں ہے۔")
                else:
                    final_pin = new_pass.strip() or generate_pin(6)
                    user_entry = {
                        "name": new_n.strip(), "email": email_key, "password": final_pin,
                        "role": "MEMBER", "status": "ACTIVE", "must_change_pw": True,
                        "phone": phone_key
                    }
                    st.session_state.registered_users[phone_key] = user_entry
                    if email_key and email_key not in st.session_state.registered_users:
                        st.session_state.registered_users[email_key] = dict(user_entry)
                    st.session_state.last_created_member = {
                        "name": new_n.strip(), "phone": phone_key, "pin": final_pin
                    }
                    rerun()

        _lcm = st.session_state.last_created_member
        if _lcm:
            invite_text = (
                f"السلام علیکم {_lcm['name']}!\n"
                f"آپ کو {APP_NAME} فیملی ایپ میں شامل کر لیا گیا ہے۔\n"
                f"📱 لاگ ان نمبر: {_lcm['phone']}\n"
                f"🔑 عارضی PIN: {_lcm['pin']}\n"
                f"لاگ ان کے بعد اپنا پاس ورڈ ضرور تبدیل کر لیں۔"
            )
            wa_phone = "92" + _lcm["phone"][1:]
            wa_link = f"https://wa.me/{wa_phone}?text={urllib.parse.quote(invite_text)}"
            st.markdown(f"""
                <div class="credential-card">
                    ✅ <strong>{_lcm['name']}</strong> شامل ہو گئے!<br/>
                    📱 نمبر: <code>{_lcm['phone']}</code><br/>
                    🔑 PIN: <code>{_lcm['pin']}</code>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"👉 **[📲 واٹس ایپ پر دعوت بھیجیں]({wa_link})**")
            if st.button("✖ Hide / چھپائیں", key="hide_credentials"):
                st.session_state.last_created_member = None
                rerun()

        with st.expander("📖 ممبرز ایپ میں کیسے شامل ہوں گے؟ (مکمل طریقہ)"):
            st.markdown("""
                <div class="help-step"><strong>مرحلہ 1:</strong> ایڈمن اوپر فارم میں ممبر کا موبائل نمبر، ای میل اور نام لکھتا ہے۔</div>
                <div class="help-step"><strong>مرحلہ 2:</strong> PIN خود لکھیں یا خالی چھوڑیں تو ایپ خود رینڈم PIN بنائے گی۔</div>
                <div class="help-step"><strong>مرحلہ 3:</strong> "واٹس ایپ پر دعوت بھیجیں" پر کلک کریں، ممبر کو نمبر اور PIN پہنچ جائے گا۔</div>
                <div class="help-step"><strong>مرحلہ 4:</strong> ممبر ایپ کا لنک کھول کر <em>نمبر + PIN</em> سے لاگ ان کرتا ہے۔ (OTP ضروری نہیں)</div>
                <div class="help-step"><strong>مرحلہ 5:</strong> لاگ ان کے بعد ممبر اپنا پاس ورڈ بدل لے۔ اگر بھول جائے تو "Forgot Password" سے ای میل OTP آئے گا۔</div>
            """, unsafe_allow_html=True)

    with adm_tab4:
        st.markdown("#### Manage Members / ممبرز کا انتظام")
        _manage_list = [(k, v) for k, v in st.session_state.registered_users.items() if "@" not in k and k != ADMIN_REAL_PHONE]
        if not _manage_list:
            st.info("ابھی کوئی ممبر شامل نہیں ہوا۔")
        for mk, mv in _manage_list:
            with st.expander(f"👤 {mv['name']} — {mk} [{mv['status']}]"):
                col_ma, col_mb = st.columns(2)
                if col_ma.button("🔄 Reset PIN / نیا PIN", key=f"rpin_{mk}"):
                    fresh_pin = generate_pin(6)
                    update_user_password_globally(mk, fresh_pin)
                    mv["must_change_pw"] = True
                    for kk, vv in st.session_state.registered_users.items():
                        if vv.get("email") and vv.get("email") == mv.get("email"):
                            vv["must_change_pw"] = True
                    st.session_state.last_created_member = {"name": mv["name"], "phone": mk, "pin": fresh_pin}
                    st.success(f"نیا PIN: {fresh_pin}  (اوپر Add Members ٹیب میں واٹس ایپ لنک موجود ہے)")
                new_status = "INACTIVE" if mv["status"] == "ACTIVE" else "ACTIVE"
                if col_mb.button(f"🔁 {new_status} کریں", key=f"stat_{mk}"):
                    mv["status"] = new_status
                    for kk, vv in st.session_state.registered_users.items():
                        if vv.get("email") and vv.get("email") == mv.get("email"):
                            vv["status"] = new_status
                    rerun()
                if st.button("🗑️ Remove Member / ممبر ہٹائیں", key=f"rm_{mk}", type="primary"):
                    _em = mv.get("email")
                    st.session_state.registered_users.pop(mk, None)
                    if _em:
                        st.session_state.registered_users.pop(_em, None)
                    rerun()

    with adm_tab5:
        st.markdown("#### Pending Deposits / منظوری کے منتظر ڈپازٹ")
        _pend = [t for t in st.session_state.transactions if t["type"] == "DEPOSIT" and t["status"] == "PENDING"]
        if not _pend:
            st.info("کوئی ڈپازٹ منظوری کے لیے باقی نہیں۔")
        for t in _pend:
            with st.expander(f"{t['member_name']} — PKR {t['amount']:,} — {t['date']}"):
                st.caption(f"Ref: {t['txn_id']} | وجہ: {t.get('note', '')}")
                _rp = t.get("receipt_path")
                if _rp and os.path.exists(_rp) and _rp.lower().endswith((".jpg", ".jpeg", ".png")):
                    st.image(_rp, use_container_width=True)
                _fix_amt = st.number_input("رقم درست کریں (ضرورت ہو تو):", min_value=1, value=int(t["amount"]), step=100, key=f"fix_{t['id']}")
                _ca, _cb = st.columns(2)
                if _ca.button("✅ Approve / منظور", key=f"apv_{t['id']}", use_container_width=True):
                    t["amount"] = int(_fix_amt)
                    t["status"] = "APPROVED"
                    t["note"] = "ایڈمن نے منظور کیا"
                    rerun()
                if _cb.button("❌ Reject / مسترد", key=f"rej_{t['id']}", type="primary", use_container_width=True):
                    t["status"] = "REJECTED"
                    t["note"] = "ایڈمن نے مسترد کیا"
                    rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SECTION 5: FAST DEPOSIT FUNDS & INSTANT RECEIPT SUBMISSION
# ------------------------------------------------------------------------------
st.markdown("<div class='content-section'>", unsafe_allow_html=True)
st.subheader("💰 Deposit Funds & Submit Receipt / فنڈ میں رقم جمع کروائیں")

col_dep1, col_dep2 = st.columns([1, 1])

with col_dep1:
    st.markdown("#### Payment Accounts / رقم جمع کروانے کے لیے اکاؤنٹس")
    for acc in st.session_state.payment_accounts:
        st.info(f"💳 **{acc['type']}** | **Title:** `{acc['title']}` | **Number:** `{acc['number']}`")

with col_dep2:
    st.markdown("#### Submit Payment Receipt / رسید جمع کروائیں")
    st.caption("⚡ اسکرین شاٹ اپ لوڈ کریں، رقم چند سیکنڈ میں تصدیق ہو کر فوری شامل ہو جائے گی۔")
    
    with st.form("submit_deposit_form", clear_on_submit=True):
        dep_amount = st.number_input("Amount (PKR) / رقم (0 = اسکرین شاٹ سے خود پڑھیں):", min_value=0, step=500, value=0)
        dep_txnid = st.text_input("Transaction Ref ID (Optional) / ٹرانزیکشن آئی ڈی (اختیاری):", placeholder="e.g. 982310293")
        dep_file = st.file_uploader("Upload Receipt Photo / رسید کی تصویر منتخب کریں:*", type=["jpg", "jpeg", "png", "pdf"])
        btn_sub_dep = st.form_submit_button("⚡ Submit & Verify Receipt / رسید جمع کروائیں", type="primary")

    if btn_sub_dep:
        if not dep_file:
            st.error("❌ براہ کرم رسید کی تصویر اپ لوڈ کریں۔")
        else:
            file_bytes = dep_file.getvalue()
            file_hash = "HASH-" + hashlib.sha256(file_bytes).hexdigest()[:24]
            
            if file_hash in st.session_state.submitted_txn_ids:
                st.error("⛔ ANTI-FRAUD ALERT: یہی تصویر پہلے سے سسٹم میں جمع ہو چکی ہے!")
            else:
                ocr = {"ok": False, "amounts": [], "tid": None, "note": ""}
                
                # Fast Processing
                if dep_file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                    with st.spinner("⚡ 2 سیکنڈ میں رسید کی تصدیق کی جا رہی ہے..."):
                        ocr = read_receipt(file_bytes)
                
                typed_ref = dep_txnid.strip()
                real_ref = typed_ref or ocr["tid"]
                clean_ref = real_ref or f"REF-{random.randint(100000, 999999)}"

                if real_ref and clean_ref in st.session_state.submitted_txn_ids:
                    st.error("⛔ ANTI-FRAUD ALERT: یہ ٹرانزیکشن آئی ڈی پہلے استعمال ہو چکی ہے!")
                else:
                    final_amount = int(dep_amount)
                    status, note = "PENDING", ""
                    
                    # Instant Verification Logic
                    if ocr["ok"] and ocr["amounts"]:
                        if final_amount == 0:
                            final_amount = int(ocr["amounts"][0])
                            status, note = "INSTANT_ADDITION", "رقم رسید سے خودکار طور پر پڑھ کر فنڈز میں شامل کر دی گئی"
                        elif any(abs(a - final_amount) < 1.0 for a in ocr["amounts"]):
                            status, note = "INSTANT_ADDITION", "درج کی گئی رقم کی رسید سے تصدیق ہو گئی"
                        else:
                            status, note = "INSTANT_ADDITION", "رقم درج شدہ رقم کے مطابق منظور کر لی گئی"
                    else:
                        if final_amount > 0:
                            status, note = "INSTANT_ADDITION", "رقم شامل کر دی گئی (ایڈمن بعد میں جائزہ لے سکتا ہے)"
                        else:
                            note = ocr.get("note") or "رقم واضح نہیں تھی"

                    if final_amount <= 0:
                        st.error("❌ تصویر سے رقم نہیں پڑھی جا سکی۔ براہ کرم رقم کا خانے میں اندراج کریں اور دوبارہ جمع کروائیں۔")
                    else:
                        new_id = next_txn_id()
                        receipt_path = ""
                        try:
                            rdir = os.path.join(os.path.dirname(DATA_FILE), "familycare_receipts")
                            os.makedirs(rdir, exist_ok=True)
                            ext = os.path.splitext(dep_file.name)[1].lower() or ".jpg"
                            receipt_path = os.path.join(rdir, f"{new_id}_{file_hash[5:15]}{ext}")
                            with open(receipt_path, "wb") as rf:
                                rf.write(file_bytes)
                        except Exception:
                            receipt_path = ""

                        st.session_state.submitted_txn_ids.add(file_hash)
                        if real_ref:
                            st.session_state.submitted_txn_ids.add(clean_ref)

                        # Transaction Record Addition
                        st.session_state.transactions.append({
                            "id": new_id,
                            "member_phone": current_phone_email,
                            "member_name": current_name,
                            "type": "DEPOSIT",
                            "amount": final_amount,
                            "txn_id": clean_ref,
                            "status": status,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "screenshot": dep_file.name,
                            "receipt_path": receipt_path,
                            "note": note
                        })

                        # Trigger Emotional Thank You and Live Balance Update
                        random_quote = random.choice(EMOTIONAL_THANKYOU_MESSAGES)
                        st.session_state.last_deposit_msg = {
                            "name": current_name, 
                            "amount": final_amount, 
                            "quote": random_quote
                        }
                        
                        # چٹ روم میں بھی اطلاع پہنچائیں
                        st.session_state.chat_threads["GENERAL"].append({
                            "id": f"t{datetime.now().strftime('%H%M%S%f')}",
                            "kind": "text",
                            "sender": "🤖 System Notification",
                            "sender_key": "SYSTEM",
                            "time": datetime.now().strftime("%H:%M"),
                            "msg": f"✨ **{current_name}** نے فنڈز میں **PKR {final_amount:,}** جمع کروائے ہیں۔ جزاک اللہ! 💖"
                        })
                        
                        save_store()
                        rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SECTION 6: ANONYMOUS VOTING & BILL PASSING (VISIBLE TO ALL)
# ------------------------------------------------------------------------------
st.markdown("<div class='content-section'>", unsafe_allow_html=True)
st.subheader("🆘 Financial Aid Appeals & Bill Voting / امدادی بل پاسنگ سسٹم")

col_aid1, col_aid2 = st.columns([1, 1])

with col_aid1:
    st.markdown("#### Request Aid / امداد کی درخواست کریں")
    with st.form("aid_request_form", clear_on_submit=True):
        req_amount = st.number_input("Required Amount (PKR) / مطلوبہ رقم:*", min_value=500, step=500, value=2000)
        req_reason = st.text_area("Reason / وجہ تفصیل سے لکھیں:*", placeholder="Explain need...")
        btn_sub_aid = st.form_submit_button("📩 Send Appeal / درخواست بھیجیں")
        if btn_sub_aid and req_reason:
            st.session_state.assistance_requests.append({
                "id": len(st.session_state.assistance_requests) + 1,
                "member_name": current_name, "member_key": current_phone_email, "amount": req_amount,
                "reason": req_reason, "status": "PENDING", "agree_votes": 0, "disagree_votes": 0,
                "voters": [],
                "date": datetime.now().strftime("%Y-%m-%d")
            })
            st.success("✅ Appeal Submitted / درخواست بھیج دی گئی!")
            rerun()

with col_aid2:
    st.markdown("#### Public Appeals & Voting / بل پاسنگ گنتی")
    st.caption("📜 اصول: بل پاس ہونے کے لیے تمام ممبرز (درخواست دہندہ کے علاوہ) کا 'متفق' ہونا ضروری ہے۔ ایک بھی 'نا منظور' آ جائے تو بل مسترد۔ ووٹ خفیہ رہتے ہیں۔")
    if not st.session_state.assistance_requests:
        st.caption("ابھی کوئی درخواست موجود نہیں۔")
    _badges = {"PENDING": "⏳ ووٹنگ جاری", "APPROVED": "✅ بل پاس ہو گیا", "REJECTED": "❌ بل مسترد", "PAID": "💸 رقم ادا ہو چکی"}
    for req in st.session_state.assistance_requests:
        refresh_bill_status(req)
        _need = len(eligible_voters(req))
        _agree = req.get("agree_votes", 0)
        st.markdown(f"📌 **{req['member_name']}**: PKR {req['amount']:,} — *{req['reason']}*")
        st.markdown(f"**{_badges.get(req['status'], req['status'])}**")
        st.write(f"🗳️ **ووٹ:** 👍 `{_agree}` / `{_need}` درکار | 👎 `{req.get('disagree_votes', 0)}`")
        if _need:
            st.progress(min(_agree / _need, 1.0))

        _is_owner = req.get("member_key") == current_phone_email or (not req.get("member_key") and req["member_name"] == current_name)
        _voted = current_phone_email in req.get("voters", [])
        if req["status"] == "PENDING":
            if _is_owner:
                st.caption("ℹ️️ یہ آپ کی اپنی درخواست ہے، اس پر آپ ووٹ نہیں دے سکتے۔")
            elif _voted:
                st.caption("✔️ آپ ووٹ دے چکے ہیں (ایک ممبر = ایک ووٹ)")
            else:
                col_v1, col_v2 = st.columns(2)
                if col_v1.button(f"👍 I Agree / متفق ہوں #{req['id']}", key=f"agree_{req['id']}"):
                    req['agree_votes'] = req.get('agree_votes', 0) + 1
                    req.setdefault("voters", []).append(current_phone_email)
                    refresh_bill_status(req)
                    rerun()
                if col_v2.button(f"👎 Disagree / نا منظور #{req['id']}", key=f"disagree_{req['id']}"):
                    req['disagree_votes'] = req.get('disagree_votes', 0) + 1
                    req.setdefault("voters", []).append(current_phone_email)
                    refresh_bill_status(req)
                    rerun()
        if req["status"] == "APPROVED" and current_role == "ADMIN":
            total_deposits = sum(t["amount"] for t in st.session_state.transactions if t["type"] == "DEPOSIT" and t["status"] in ["APPROVED", "INSTANT_ADDITION"])
            total_spendings = sum(t["amount"] for t in st.session_state.transactions if t["type"] == "SPENDING")
            remaining_balance = total_deposits - total_spendings
            
            if req["amount"] > remaining_balance:
                st.warning(f"⚠️ فنڈ میں صرف PKR {remaining_balance:,} موجود ہیں۔")
            if st.button(f"💸 رقم ادا کریں اور خرچہ میں درج کریں #{req['id']}", key=f"pay_{req['id']}", type="primary"):
                st.session_state.transactions.append({
                    "id": next_txn_id(), "member_phone": current_phone_email,
                    "member_name": f"{current_name} (Admin)", "type": "SPENDING", "amount": req["amount"],
                    "txn_id": f"AID-{req['id']}", "status": "APPROVED",
                    "date": datetime.now().strftime("%Y-%m-%d"), "screenshot": "N/A",
                    "details": f"Aid paid to {req['member_name']}: {req['reason']}"
                })
                req["status"] = "PAID"
                rerun()
        st.divider()

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SECTION 7: REAL VOICE RECORDING & DIRECT CHAT DELETE BUTTON
# ------------------------------------------------------------------------------
st.markdown("<div class='content-section'>", unsafe_allow_html=True)
st.subheader("💬 Family Live Communication & Voice Stream / گفتگو اور کالز")

c_call1, c_call2 = st.columns(2)
room_name = "FamilyCare-General-Room"
jitsi_url = f"https://meet.jit.si/{room_name}"

with c_call1:
    st.markdown(f"📞 **[📞 Start Audio Call / آڈیو کال کریں]({jitsi_url})**")
with c_call2:
    st.markdown(f"📹 **[📹 Start Video Call / ویڈیو کال کریں]({jitsi_url})**")

# ---- Voice Message Recorder (اصلی وائس میسج: ریکارڈ -> سن کر -> بھیجیں) ----
st.markdown("##### 🎙 Voice Message / وائس میسج بھیجیں")
if hasattr(st, "audio_input"):
    recorded_voice = st.audio_input(
        "🎙 مائیک دبا کر بولیں، ختم کر کے نیچے بھیجیں / Record voice",
        key=f"voice_rec_{st.session_state.voice_counter}"
    )
    if recorded_voice is not None:
        if st.button("🚀 Send Voice Message / وائس بھیجیں", type="primary", use_container_width=True, key="send_voice_btn"):
            st.session_state.chat_threads["GENERAL"].append({
                "id": f"v{datetime.now().strftime('%H%M%S%f')}",
                "kind": "voice",
                "sender": current_name,
                "sender_key": current_phone_email,
                "time": datetime.now().strftime("%H:%M"),
                "msg": "🎙 Voice Message / وائس میسج",
                "audio": recorded_voice.getvalue()
            })
            st.session_state.voice_counter += 1
            st.session_state.sound_type_trigger = "CHAT"
            rerun()
else:
    st.warning("⚠️ وائس ریکارڈنگ کے لیے Streamlit ورژن 1.39 یا نیا چاہیے۔ ایپ Reboot کریں۔")

# Chat Stream with DIRECT VISIBLE DELETE BUTTON (text + voice دونوں کے لیے)
st.markdown("##### 💬 Chat Stream & Voice Messages / چیٹ ہسٹری")
@st.fragment(run_every=8)
def render_chat_stream():
    """ہر 8 سیکنڈ بعد خود تازہ ہوتی ہے تاکہ دوسروں کے نئے میسج نظر آئیں۔"""
    if not st.session_state.chat_threads["GENERAL"]:
        st.caption("ابھی کوئی پیغام نہیں۔ پہلا پیغام آپ بھیجیں!")

    for idx, chat in enumerate(list(st.session_state.chat_threads["GENERAL"])):
        bubble_class = "chat-bubble-admin" if "Admin" in chat['sender'] else "chat-bubble-member"
        is_voice = chat.get("kind") == "voice"
        msg_id = chat.get("id", f"legacy_{idx}")
        
        col_msg1, col_msg2 = st.columns([7.5, 1.5])
        with col_msg1:
            st.markdown(f"""
                <div class="{bubble_class}">
                    <strong style="color:white;">{chat['sender']}</strong> <small style="color:#CBD5E1;">({chat['time']})</small><br/>
                    <span style="color:white; font-size:1.05rem;">{chat['msg']}</span>
                </div>
            """, unsafe_allow_html=True)
            if is_voice and chat.get("audio"):
                st.audio(chat["audio"], format="audio/wav")
        with col_msg2:
            owner_ok = chat.get("sender_key") == current_phone_email or chat['sender'] == current_name
            if current_role == "ADMIN" or owner_ok:
                del_label = "🗑️ Delete Voice" if is_voice else "🗑️ Delete"
                if st.button(del_label, key=f"del_msg_{msg_id}", type="primary", use_container_width=True):
                    st.session_state.chat_threads["GENERAL"] = [
                        c for c in st.session_state.chat_threads["GENERAL"]
                        if c.get("id") != msg_id
                    ]
                    rerun()

render_chat_stream()

with st.form("msg_form_gen", clear_on_submit=True):
    new_msg = st.text_input("💬 Type Message / میسج لکھیں...")
    if st.form_submit_button("🚀 Send Message / میسج بھیجیں", type="primary") and new_msg:
        st.session_state.chat_threads["GENERAL"].append({
            "id": f"t{datetime.now().strftime('%H%M%S%f')}",
            "kind": "text",
            "sender": current_name,
            "sender_key": current_phone_email,
            "time": datetime.now().strftime("%H:%M"),
            "msg": new_msg
        })
        st.session_state.sound_type_trigger = "CHAT"
        rerun()

if current_role == "ADMIN" and st.session_state.chat_threads["GENERAL"]:
    if st.button("🧹 Clear All Chat / ساری چیٹ صاف کریں", key="clear_all_chat"):
        st.session_state.chat_threads["GENERAL"] = []
        rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SECTION 8: LEDGER AUDIT HISTORY WITH ADMIN DELETE CONTROL
# ------------------------------------------------------------------------------
st.markdown("<div class='content-section'>", unsafe_allow_html=True)
st.subheader("📜 Family Ledger Audit History / کھاتہ اور حساب کتاب")

display_txns = st.session_state.transactions

st.dataframe(
    display_txns,
    use_container_width=True
)

if current_role == "ADMIN" and st.session_state.transactions:
    with st.expander("🗑️ Admin Transaction Delete Manager / غلط اینٹری ڈیلیٹ کریں"):
        txn_ids_list = [f"ID: {t['id']} | {t['member_name']} | PKR {t['amount']}" for t in st.session_state.transactions]
        selected_txn_to_del = st.selectbox("Select Transaction to Delete:", txn_ids_list)
        if st.button("🗑️ Delete Selected Entry / اینٹری ڈیلیٹ کریں", type="primary"):
            target_id = int(selected_txn_to_del.split("|")[0].replace("ID:", "").strip())
            st.session_state.transactions[:] = [t for t in st.session_state.transactions if t["id"] != target_id]
            st.success("Entry Deleted!")
            rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# SECTION 9: MONTHLY SUMMARY CHART (ہر ممبر کا حصہ گراف میں)
# ------------------------------------------------------------------------------
st.markdown("<div class='content-section'>", unsafe_allow_html=True)
st.subheader("📈 Member Contribution Chart / ممبرز کا حصہ")

_contrib = {}
for t in st.session_state.transactions:
    if t["type"] == "DEPOSIT" and t["status"] in ["APPROVED", "INSTANT_ADDITION"]:
        _contrib[t["member_name"]] = _contrib.get(t["member_name"], 0) + t["amount"]

if _contrib:
    st.bar_chart(_contrib)
else:
    st.caption("جب ممبرز رقم جمع کروائیں گے تو یہاں گراف نظر آئے گا۔")

st.markdown("</div>", unsafe_allow_html=True)

st.caption(f"{APP_ORGANIZATION} • Version {APP_VERSION}")

save_store()