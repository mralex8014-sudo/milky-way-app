import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка Вселенной
st.set_page_config(page_title="MilkyGram", page_icon="🌌", layout="centered")

# --- ГЛОБАЛЬНЫЕ КОНСТАНТЫ ---
DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ИНИЦИАЛИЗАЦИЯ SESSION STATE ---
for key, val in {
    'logged_in': False, 'username': "", 'page': "feed", 
    'viewing_profile': None, 'theme': "Dark"
}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- УЛЬТРА-КОМПАКТНЫЙ CSS ---
bg, txt, brd, inp = ("#050505", "#D0D0D0", "#1B1B3A", "#0F0F1B") if st.session_state.theme == "Dark" else ("#FFFFFF", "#262626", "#DBDBDB", "#F0F2F6")

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-size: 14px !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {inp}; border-right: 1px solid {brd}; width: 200px !important; }}
    
    /* Уменьшение заголовков */
    h1 {{ font-size: 1.5rem !important; margin-bottom: 0.5rem !important; }}
    h2 {{ font-size: 1.2rem !important; }}
    h3 {{ font-size: 1rem !important; }}
    
    /* Компактные кнопки */
    .stButton>button {{ 
        border-radius: 12px; padding: 2px 10px; font-size: 12px !important; 
        background-color: #2D2D4D; color: white; border: 1px solid {brd};
    }}
    
    /* Карточки постов */
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {inp} !important; border: 1px solid {brd} !important; 
        border-radius: 10px; padding: 10px !important; margin-bottom: 10px;
    }}
    
    /* Поля ввода */
    .stTextInput>div>div>input {{ padding: 5px !important; }}
    
    /* Чат и комментарии */
    .comment-box {{ font-size: 12px; background: {bg}; padding: 5px 8px; border-radius: 8px; margin-top: 3px; border: 1px solid {brd}; }}
    .msg-cloud {{ padding: 5px 10px; border-radius: 10px; margin-bottom: 5px; max-width: 80%; font-size: 13px; }}
    </style>
    """, unsafe_allow_html=True)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ЛОГИКА ВХОДА ---
if not st.session_state.logged_in:
    st.title("🌌 MilkyGram")
    with st.container(border=True):
        u = st.text_input("Позывной", key="login_u")
        p = st.text_input("Код", type="password", key="login_p")
        if st.button("Войти"):
            res = requests.get(f"{DB_URL}users/{u}.json").json()
            if res and res.get('password') == hash_pass(p):
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
    st.stop()

# --- ПОЛУЧЕНИЕ ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})
my_satellites = my_data.get('satellites', []) or []

# --- ФУНКЦИИ ---
def show_user_profile(name):
    u = all_users.get(name)
    if not u: return
    st.subheader(f"Профиль @{name}")
    c1, c2 = st.columns([1, 3])
    c1.image(u.get('avatar', DEFAULT_AVA), width=80)
    with c2:
        st.caption(u.get('bio', 'Исследователь'))
        if name != st.session_state.username:
            if name in my_satellites:
                if st.button("Разорвать связь"):
                    my_satellites.remove(name); requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites}); st.rerun()
            else:
                if st.button("Установить связь"):
                    my_satellites.append(name); requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites}); st.rerun()

# --- МЕНЮ (САЙДБАР) ---
with st.sidebar:
    st.markdown(f"### @{st.session_state.username}")
    theme_on = st.toggle("🌙", value=(st.session_state.theme == "Dark"))
    if theme_on != (st.session_state.theme == "Dark"):
        st.session_state.theme = "Dark" if theme_on else "Light"; st.rerun()
    
    st.write("---")
    pages = {"📡 Лента": "feed", "🔍 Поиск": "search", "📟 Радио": "dm", "🌌 Связи": "galaxy", "👨‍🚀 Я": "my_profile"}
    for label, pg in pages.items():
        if st.button(label): st.session_state.page, st.session_state.viewing_profile = pg, None; st.rerun()
    if st.button("🚪 Выход"): st.session_state.logged_in = False; st.rerun()

# --- КОНТЕНТ ---
if st.session_state.viewing_profile:
    show_user_profile(st.session_state.viewing_profile)
    if st.button("← Назад"): st.session_state.viewing_profile = None; st.rerun
