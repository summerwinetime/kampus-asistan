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
# 2. AYARLAR (REKLAM & VİDEO)
# ==============================================================================
CONFIG = {
    # ARKA PLAN VİDEOSU (app.py ile aynı klasörde olmalı)
    "bg_video": "",
    
    # REKLAM AYARLARI
    "footer_ad": {
        "bg_file": "mcc.gif",
        "title": {"tr": "✨ Ana Sponsor", "en": "✨ Main Sponsor"}
    },
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

def set_background_video(video_file):
    """Videoyu okur ve arka plana yerleştirir."""
    video_b64 = get_base64_of_bin_file(video_file)
    if not video_b64:
        # Video yoksa düz siyah yap
        st.markdown(
            """<style>.stApp { background: #000; }</style>""", 
            unsafe_allow_html=True
        )
        return

    # HTML/CSS: Video en altta, üstünde siyah perde, en üstte içerik
    video_html = f"""
    <style>
    .stApp {{
        background: rgba(0,0,0,0); /* Streamlit arka planını şeffaf yap */
    }}
    #my-video-container {{
        position: fixed;
        right: 0; 
        bottom: 0;
        min-width: 100%; 
        min-height: 100%;
        z-index: -2;
    }}
    #video-overlay {{
        position: fixed;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.7); /* %70 Siyah Perde (Yazı okunurluğu için) */
        z-index: -1;
    }}
    </style>
    <video autoplay muted loop id="my-video-container">
        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
    </video>
    <div id="video-overlay"></div>
    """
    st.markdown(video_html, unsafe_allow_html=True)

def get_ad_html_for_intent(intent, lang):
    if not CONFIG["show_response_ad"]: return ""
    ad_data = CONFIG["responses_ad"].get(intent, CONFIG["responses_ad"]["default"])
    img_b64 = get_base64_of_bin_file(ad_data["image"])
    if not img_b64: return ""
    title_text = ad_data["title"][lang]
    return f"""
    <div class="ad-card-internal">
        <span class="ad-label">{title_text}</span>
        <img src="data:image/png;base64,{img_b64}" class="ad-img-internal">
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
        "btn_bus": "🚌 Merkez Otobüs",
        "btn_grade": "🧮 Not Hesaplam",
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
# 5. CSS TASARIM (ŞEFFAF KATMANLAR)
# ==============================================================================
st.markdown("""
<style>
/* FONT VE RENKLER */
.stApp { color:white; font-family: sans-serif; }

/* HEADER */
.header { text-align:center; padding-top: 10px; padding-bottom: 5px; }
.header h1 { font-size: 24px; font-weight: 800; margin: 0; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
.header p { font-size: 12px; color: #ccc; margin-top: 5px; }

/* KARŞILAMA */
.welcome-container { text-align: center; padding: 50px 20px; animation: fadeIn 0.5s; }
.welcome-title { font-size: 28px; font-weight: 800; color: #fff; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }
.welcome-desc { font-size: 14px; color: #ddd; margin-bottom: 40px; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }
.welcome-icon { font-size: 60px; margin-bottom: 20px; display:block; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); }

/* BUTONLAR (YARI ŞEFFAF ARKA PLAN) */
.quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
.quick-btn {
    background: rgba(255, 255, 255, 0.9); /* Hafif şeffaf beyaz */
    color: black; border: none; border-radius: 12px;
    padding: 15px 5px; font-weight: 700; font-size: 13px; cursor: pointer; width: 100%;
    backdrop-filter: blur(5px);
}
.greeting-text { text-align: center; color: #eee; font-size: 14px; margin-bottom: 15px; font-weight: 500; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }

/* KARTLAR (GLASSMORPHISM EFFECT) */
.menu-card { 
    background: rgba(20, 20, 20, 0.85); /* Çok koyu yarı şeffaf */
    border-left: 4px solid #00b894; 
    border-radius: 8px; padding: 15px; margin-top: 15px; 
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.menu-card h3 { color: #00b894; font-size: 15px; margin: 0 0 10px 0; font-weight:bold; }
.menu-card ul { padding: 0; margin: 0; list-style: none; }
.menu-card li { border-bottom: 1px solid #444; padding: 5px 0; font-size: 13px; color: #ddd; }
.menu-card li:last-child { border-bottom: none; }

/* INPUT (YARI ŞEFFAF) */
div[data-testid="stTextInput"] { margin-top: 10px; }
div[data-testid="stTextInput"] input {
    background-color: rgba(30, 30, 30, 0.8) !important; 
    color: white !important; border: 1px solid #555 !important;
    border-radius: 50px !important; padding: 15px 20px !important; font-size: 14px;
    backdrop-filter: blur(5px);
}

/* CEVAP İÇİ REKLAM */
.ad-card-internal {
    text-align: center; margin-bottom: 15px; border-bottom: 1px dashed #555; padding-bottom: 10px;
}
.ad-label {
    display: block; font-size: 10px; color: #00b894; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; text-shadow: 0 1px 2px rgba(0,0,0,1);
}
.ad-img-internal { width: 100%; max-width: 250px; border-radius: 10px; }

/* FOOTER REKLAM */
.ad-wrapper {
    margin-top: 30px; text-align: center; border-top: 1px solid #555; padding-top: 10px;
}
.ad-title {
    font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; display: block; text-shadow: 0 1px 2px rgba(0,0,0,1);
}
.ad-img {
    width: 100%; max-width: 300px; border-radius: 15px; border: 2px solid transparent;
    animation: glow 2s infinite alternate;
}
@keyframes glow {
    0% { border-color: #444; box-shadow: 0 0 5px rgba(255, 255, 255, 0.1); }
    100% { border-color: #fff; box-shadow: 0 0 20px rgba(255, 255, 255, 0.4); }
}
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
        total = (s[0]*0.30) + (s[1]*0.10) + (s[2]*0.10) + (s[3]*0.10) + (s[4]*0.40)
        status = self.txt["res_pass"] if total >= 64.5 else self.txt["res_fail"]
        return f"Ortalama: **{total:.2f}**\nDurum: **{status}**"

    def detect_intent(self, text):
        text = text.lower()
        for intent, keywords in INTENT_LIB.items():
            if any(k in text for k in keywords):
                return intent
        return None

# ==============================================================================
# 7. UYGULAMA AKIŞI
# ==============================================================================

# VİDEO YÜKLE
set_background_video(CONFIG["bg_video"])

# A) DİL SEÇİLMEMİŞSE
if st.session_state.language is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="welcome-container">
        <span class="welcome-icon">🎓</span>
        <div class="welcome-title">{LOCALE['tr']['welcome_title']}</div>
        <div class="welcome-desc">{LOCALE['tr']['welcome_desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        col_tr, col_en = st.columns(2)
        with col_tr:
            if st.button("🇹🇷 Türkçe", type="primary", use_container_width=True):
                st.session_state.language = "tr"
                st.query_params["lang"] = "tr"
                st.rerun()
        with col_en:
            if st.button("🇬🇧 English", type="primary", use_container_width=True):
                st.session_state.language = "en"
                st.query_params["lang"] = "en"
                st.rerun()

# B) DİL SEÇİLMİŞSE
else:
    lang = st.session_state.language
    txt = LOCALE[lang]
    bot = CampusLogic(lang)

    # HEADER & GREETING
    st.markdown(f"""
    <div class="header">
      <h1>🎓 {txt['welcome_title']}</h1>
      <p>{txt['welcome_desc']}</p>
    </div>
    <div class="greeting-text">{txt["greeting"]}</div>
    """, unsafe_allow_html=True)

    # HIZLI BUTONLAR
    st.markdown(f"""
    <form method="get">
      <input type="hidden" name="lang" value="{lang}">
      <div class="quick-grid">
        <button class="quick-btn" name="q" value="school">{txt['btn_school']}</button>
        <button class="quick-btn" name="q" value="dorm">{txt['btn_dorm']}</button>
        <button class="quick-btn" name="q" value="bus">{txt['btn_bus']}</button>
        <button class="quick-btn" name="q" value="grade">{txt['btn_grade']}</button>
      </div>
    </form>
    """, unsafe_allow_html=True)

    # SIDEBAR
    with st.sidebar:
        st.header(txt["sidebar_calc"])
        if st.button("Change Lang / Dil Değiştir"):
            st.session_state.language = None
            st.query_params.clear()
            st.rerun()
        st.markdown("---")
        with st.expander(txt["sidebar_calc"], expanded=True):
            s1 = st.number_input("Vize %30", 0, 100)
            s2 = st.number_input("Portfolyo %10", 0, 100)
            s3 = st.number_input("Sınıf İçi %10", 0, 100)
            s4 = st.number_input("Diğer %10", 0, 100)
            s5 = st.number_input("Final %40", 0, 100)
            if st.button(txt["btn_calc"], type="primary"):
                st.success(bot.calculate_grade([s1, s2, s3, s4, s5]))
        st.caption("📢 Sponsor: Kampüs Burger")

    # MESAJ GEÇMİŞİ
    if "history" not in st.session_state:
        st.session_state.history = []

    # 1. BUTON CEVAPLARI + CEVAP İÇİ REKLAM
    q = st.query_params.get("q")
    if q:
        intent_map = {"bus": "transport", "grade": "grade", "school": "school", "dorm": "dorm"}
        target_intent = intent_map.get(q, "default")
        
        ad_html = get_ad_html_for_intent(target_intent, lang)
        
        if q == "school": resp = bot.get_menu_html("school")
        elif q == "dorm": resp = bot.get_menu_html("dorm")
        elif q == "bus": resp = bot.get_bus_html()
        else: resp = f"<div class='menu-card'><ul><li>{txt['calc_msg']}</li></ul></div>"
        
        full_resp = ad_html + resp
        st.session_state.history.append({"role": "assistant", "content": full_resp})
        st.query_params.clear()
        st.rerun()

    # 2. YAZARAK SOR CEVAPLARI
    user_input = st.text_input("", placeholder=txt["input_placeholder"], key="mid_input")

    if user_input:
        intent = bot.detect_intent(user_input)
        
        ad_html = get_ad_html_for_intent(intent, lang) if intent else get_ad_html_for_intent("default", lang)

        ans = ""
        if intent == "school": ans = bot.get_menu_html("school")
        elif intent == "dorm": ans = bot.get_menu_html("dorm")
        elif intent == "transport": ans = bot.get_bus_html()
        elif intent == "grade": ans = f"<div class='menu-card'><ul><li>{txt['calc_msg']}</li></ul></div>"
        elif intent == "greet": ans = f"<div class='menu-card'><ul><li>{txt['greeting']}</li></ul></div>"
        else: ans = f"<div class='menu-card'><ul><li>{txt['error_msg']}</li></ul></div>"
        
        full_ans = ad_html + ans if intent and intent != "greet" else ans
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.history.append({"role": "assistant", "content": full_ans})

    # CEVAPLARI GÖSTER
    for msg in reversed(st.session_state.history):
        if msg["role"] == "assistant":
            st.markdown(msg["content"], unsafe_allow_html=True)

    # 3. FOOTER REKLAM
    footer_img_b64 = get_base64_of_bin_file(CONFIG["footer_ad"]["image"])
    if footer_img_b64:
        st.markdown(f"""
        <div class="ad-wrapper">
            <span class="ad-title">{CONFIG['footer_ad']['title'][lang]}</span>
            <img src="data:image/png;base64,{footer_img_b64}" class="ad-img" alt="Main Sponsor">
        </div>

        """, unsafe_allow_html=True)
