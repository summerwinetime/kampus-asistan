import streamlit as st
import datetime
import base64
import os

# ==============================================================================
# 1. SAYFA AYARLARI
# ==============================================================================
st.set_page_config(
    page_title="Kampüs Asistanı",
    page_icon="🎓",
    layout="centered"
)

# URL DİL KONTROLÜ
qp = st.query_params
if "lang" in qp:
    st.session_state.language = qp["lang"]
elif "language" not in st.session_state:
    st.session_state.language = None

# ==============================================================================
# 2. AYARLAR
# ==============================================================================
CONFIG = {
    # --- FOOTER REKLAM (GIF BURAYA GELİYOR) ---
    "footer_ad": {
        "image": "mcc.gif",  # Hareketli GIF dosyasının adı
        "title": {"tr": "✨ Ana Sponsor", "en": "✨ Main Sponsor"}
    },

    # --- CEVAP İÇİ REKLAMLAR ---
    "responses_ad": {
        "school": { 
            "image": "choco.png",
            "title": {"tr": "🍔 Kampüs Burger - %20 İndirim!", "en": "🍔 20% Off at Campus Burger!"}
        },
        "dorm": { 
            "image": "choco.png",
            "title": {"tr": "🛏️ Yurt İhtiyaçların Burada", "en": "🛏️ Dorm Essentials"}
        },
        "transport": { 
            "image": "choco.png",
            "title": {"tr": "🎧 Yolculuk İçin Kulaklıklar", "en": "🎧 Headphones for Travel"}
        },
        "default": {
            "image": "choco.png",
            "title": {"tr": "📢 Haftanın Fırsatı", "en": "📢 Deal of the Week"}
        }
    },
    "show_response_ad": True 
}

# ==============================================================================
# 3. YARDIMCI FONKSİYONLAR
# ==============================================================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def get_mime_type(filename):
    """Dosya uzantısına göre türü belirler."""
    ext = filename.split('.')[-1].lower()
    if ext == 'gif': return 'image/gif'
    if ext == 'png': return 'image/png'
    if ext in ['jpg', 'jpeg']: return 'image/jpeg'
    return 'image/png'

def get_ad_html_for_intent(intent, lang):
    if not CONFIG["show_response_ad"]: return ""
    ad_data = CONFIG["responses_ad"].get(intent, CONFIG["responses_ad"]["default"])
    
    file_name = ad_data["image"]
    img_b64 = get_base64_of_bin_file(file_name)
    if not img_b64: return ""
    
    mime = get_mime_type(file_name)
    title_text = ad_data["title"][lang]
    
    return f"""
    <div class="ad-card-internal">
        <span class="ad-label">{title_text}</span>
        <img src="data:{mime};base64,{img_b64}" class="ad-img-internal">
    </div>
    """

# ==============================================================================
# 4. KELİME KÜTÜPHANESİ & LOCALE
# ==============================================================================
INTENT_LIB = {
    "school": ["okul", "yemekhane", "öğle", "öğlen", "kampüs yemek", "tabldot", "menü", "yemek listesi", "bugün ne var", "acıktım", "school", "lunch", "cafeteria"],
    "dorm": ["yurt", "kyk", "kahvaltı", "akşam", "yatakhane", "sabah", "akşam yemeği", "dorm", "breakfast", "dinner"],
    "transport": ["otobüs", "ring", "servis", "vasıta", "dolmuş", "merkez", "çarşı", "saat", "sefer", "kalkış", "bus", "shuttle", "schedule"],
    "grade": ["not", "hesap", "ortalama", "vize", "final", "büt", "geçme", "puan", "grade", "gpa", "exam"],
    "greet": ["merhaba", "selam", "slm", "naber", "günaydın", "hey", "hello", "hi"]
}

LOCALE = {
    "tr": {
        "welcome_title": "Kampüs Asistanı",
        "welcome_desc": "Yemek Menüleri • Otobüs Saatleri • Not Hesaplama",
        "greeting": "Merhaba! 👋 Ben asistanın. Aşağıdaki butonlarla anında bilgi alabilirsin.",
        "input_placeholder": "Bir şeyler yaz (Örn: 'Yemekhane', 'Ring')...",
        "btn_school": "🏫 Okul Menü",
        "btn_dorm": "🛏️ Yurt Menü",
        "btn_bus": "🚌 Merkez Oto",
        "btn_grade": "🧮 Notlar",
        "menu_school": "🏫 Okul Menüsü",
        "menu_dorm_b": "🍳 Yurt Kahvaltı",
        "menu_dorm_d": "🍲 Yurt Akşam",
        "calc_msg": "🧮 Not hesaplamak için lütfen sol üstteki ( > ) menüyü kullan.",
        "sidebar_calc": "Not Hesaplama",
        "sidebar_info": "Notlarını gir:",
        "btn_calc": "HESAPLA",
        "res_pass": "GEÇTİ",
        "res_fail": "KALDI",
        "error_msg": "Bunu tam anlayamadım. 🤷‍♂️ Lütfen butonları dene."
    },
    "en": {
        "welcome_title": "Campus Assistant",
        "welcome_desc": "Menus • Bus Schedules • Grades",
        "greeting": "Hello! 👋 I'm your assistant. Use buttons below for instant info.",
        "input_placeholder": "Type asking (e.g. 'Menu', 'Bus')...",
        "btn_school": "🏫 School Menu",
        "btn_dorm": "🛏️ Dorm Menu",
        "btn_bus": "🚌 City Bus",
        "btn_grade": "🧮 Grades",
        "menu_school": "🏫 School Menu",
        "menu_dorm_b": "🍳 Dorm Breakfast",
        "menu_dorm_d": "🍲 Dorm Dinner",
        "calc_msg": "🧮 For grades, please use the top-left ( > ) menu.",
        "sidebar_calc": "Grade Calculator",
        "sidebar_info": "Enter scores:",
        "btn_calc": "CALCULATE",
        "res_pass": "PASSED",
        "res_fail": "FAILED",
        "error_msg": "I didn't quite get that. 🤷‍♂️ Please use buttons."
    }
}

# ==============================================================================
# 5. CSS TASARIM (SADE, ŞIK VE KOMPAKT)
# ==============================================================================
st.markdown("""
<style>
/* GENEL VE RESET */
.stApp { background-color: #0e1117; color:white; font-family: sans-serif; }

/* --- KRİTİK: ÜST BOŞLUĞU KALDIRMA --- */
.block-container {
    padding-top: 1rem !important; /* Standart 6rem yerine 1rem */
    padding-bottom: 5rem !important; /* Alttan biraz boşluk kalsın */
}

/* HEADER */
.header { text-align:center; padding-top: 0px; padding-bottom: 10px; }
.header h1 { font-size: 26px; font-weight: 800; margin: 0; color: white; }
.header p { font-size: 13px; color: #888; margin-top: 5px; }

/* KARŞILAMA */
.welcome-container { text-align: center; padding: 20px 20px; animation: fadeIn 0.8s; }
.welcome-title { font-size: 30px; font-weight: 800; color: #fff; margin-bottom: 10px; }
.welcome-desc { font-size: 15px; color: #aaa; margin-bottom: 30px; }
.welcome-icon { font-size: 50px; margin-bottom: 15px; display:block; }

/* BUTONLAR */
.quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
.quick-btn {
    background: white; color: black; border: none; border-radius: 12px;
    padding: 15px 5px; font-weight: 700; font-size: 14px; cursor: pointer; width: 100%;
    transition: transform 0.1s;
}
.quick-btn:active { transform: scale(0.98); background: #eee; }
.greeting-text { text-align: center; color: #ddd; font-size: 14px; margin-bottom: 15px; font-weight: 500; }

/* KARTLAR */
.menu-card { 
    background: #1e1e1e; border-left: 4px solid #00b894; border-radius: 8px; padding: 15px; margin-top: 15px; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.menu-card h3 { color: #00b894; font-size: 16px; margin: 0 0 10px 0; font-weight:bold; }
.menu-card ul { padding: 0; margin: 0; list-style: none; }
.menu-card li { border-bottom: 1px solid #333; padding: 6px 0; font-size: 14px; color: #ddd; }
.menu-card li:last-child { border-bottom: none; }

/* INPUT (HAP ŞEKLİNDE) */
div[data-testid="stTextInput"] { margin-top: 15px; }
div[data-testid="stTextInput"] input {
    background-color: #1e1e1e !important; color: white !important; border: 1px solid #444 !important;
    border-radius: 50px !important; padding: 15px 25px !important; font-size: 14px;
}

/* REKLAMLAR */
.ad-card-internal { text-align: center; margin-bottom: 15px; border-bottom: 1px dashed #444; padding-bottom: 10px; }
.ad-label { display: block; font-size: 10px; color: #00b894; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
.ad-img-internal { width: 100%; max-width: 250px; border-radius: 10px; }

.ad-wrapper { margin-top: 30px; text-align: center; border-top: 1px solid #333; padding-top: 15px; }
.ad-title { font-size: 11px; color: #777; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; display: block; }
.ad-img { width: 100%; max-width: 320px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. VERİLER
# ==============================================================================
DATA_TEMPLATES = {
    "transport": {
        "ring": {"name": "🚌 16A Ring", "times": ["08:05","08:15","08:25","08:35","08:50","09:35","09:45","09:55","10:05","10:20","11:05","11:15","11:25","11:35","11:50","12:35","13:05","13:20","14:05","14:15","14:25","14:35","14:50","15:35","15:45","15:55","16:05","16:20","17:05"]},
        "merkez": {"name": "🚌 4A Merkez", "times": ["07:45","08:45","09:45","10:45","11:45","12:45","13:45","14:45","15:45","16:45","17:45","18:45"]}
    },
    "menus": {
        "school": {
            "2025-12-27": ["Hafta Sonu Kapalı"],
            "2025-12-29": ["Mercimek Çorba", "Misket Köfte", "Pirinç Pilavı", "Cacık"],
            "2025-12-30": ["Ezogelin Çorba", "Nohut", "Pirinç Pilavı", "Meyve"],
            "2025-12-31": ["Yayla Çorbası", "Rosto Köfte", "Bulgur Pilavı", "Salata"],
            "default": ["Veri yok / No Data"]
        },
        "dorm_breakfast": {
            "2025-12-27": ["Peynirli Omlet", "Simit", "Kaşar Peynir", "Zeytin", "Pekmez", "Ekmek", "Su"],
            "2025-12-28": ["Patates Kızartması", "Haşlanmış Yumurta", "Peynir", "Zeytin", "Sebze", "Ekmek", "Su"],
            "2025-12-29": ["Sade Omlet", "Milföy Börek", "Peynir", "Zeytin", "Meyve", "Ekmek", "Su"],
            "2025-12-30": ["Peynirli Börek", "Yumurta", "Kaşar", "Zeytin", "Çikolata", "Ekmek", "Su"],
            "2025-12-31": ["Patatesli Yumurta", "Simit", "Peynir", "Zeytin", "Sebze", "Ekmek", "Su"],
            "default": ["Yumurta", "Peynir", "Zeytin", "Reçel", "Ekmek", "Su"]
        },
        "dorm_dinner": {
            "2025-12-27": ["Ezogelin", "Nohut", "Pilav", "Şekerpare", "Su", "Ekmek"],
            "2025-12-28": ["Mercimek", "Adana Kebap", "Bulgur", "Ayran", "Su", "Ekmek"],
            "2025-12-29": ["Ezogelin", "Tavuk Burger", "Makarna", "Puding", "Su", "Ekmek"],
            "2025-12-30": ["Mercimek", "Et Sote", "Pilav", "Borani", "Su", "Ekmek"],
            "2025-12-31": ["Ezogelin", "Balık", "Helva", "Salata", "Su", "Ekmek"],
            "default": ["Akşam yemeği verisi yok / No Data"]
        }
    }
}

class CampusLogic:
    def __init__(self, lang="tr"):
        self.data = DATA_TEMPLATES
        self.lang = lang
        self.txt = LOCALE[lang]
        self.today = datetime.date.today().strftime("%Y-%m-%d")

    def get_menu_html(self, menu_type):
        t = self.today
        html = ""
        if menu_type == "school":
            items = self.data["menus"]["school"].get(t, self.data["menus"]["school"]["default"])
            html += f"<div class='menu-card'><h3>{self.txt['menu_school']} ({t})</h3><ul>" + "".join([f"<li>{x}</li>" for x in items]) + "</ul></div>"
        elif menu_type == "dorm":
            b = self.data["menus"]["dorm_breakfast"].get(t, self.data["menus"]["dorm_breakfast"]["default"])
            d = self.data["menus"]["dorm_dinner"].get(t, self.data["menus"]["dorm_dinner"]["default"])
            html += f"<div class='menu-card'><h3>{self.txt['menu_dorm_b']}</h3><ul>" + "".join([f"<li>{x}</li>" for x in b]) + "</ul></div>"
            html += f"<div class='menu-card'><h3>{self.txt['menu_dorm_d']}</h3><ul>" + "".join([f"<li>{x}</li>" for x in d]) + "</ul></div>"
        return html

    def get_bus_html(self):
        times = self.data["transport"]["merkez"]["times"]
        now = datetime.datetime.now().strftime("%H:%M")
        next_bus = next((t for t in times if t > now), "Sefer Bitti")
        return f"<div class='menu-card'><h3>{self.data['transport']['merkez']['name']}</h3><ul><li>⏱️: <b>{next_bus}</b></li></ul></div>"

    def calculate_grade(self, s):
        total = (s[0]*0.30) + (s[1]*0.10) + (s
