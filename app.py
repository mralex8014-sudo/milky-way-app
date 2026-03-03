import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка страницы
st.set_page_config(page_title="MilkyGram", page_icon="🌌", layout="centered")

# --- ИНИЦИАЛИЗАЦИЯ (Защита от пропадания интерфейса) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'page' not in st.session_state: st.session_state.page = "feed"
if 'viewing_profile' not in st.session_state: st.session_state.viewing_profile = None
if 'theme' not in st.session_state: st.session_state.theme = "Dark"

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- КОМПАКТНЫЙ СТИЛЬ ---
bg, txt, brd, inp = ("#050505", "#D0D0D0", "#1B1B3A", "#0F0F1B") if st.session_state.theme == "Dark" else ("#FFFFFF", "#262626", "#DBDBDB", "#F0F2F6")
st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-size: 14px !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {inp}; border-right: 1px solid {brd}; }}
    .stButton>button {{ border-radius: 10px; padding: 2px 10px; font-size: 12px !important; background-color: #2D2D4D; color: white; }}
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {inp} !important; border: 1px solid {brd} !important; border-radius: 10px; padding: 10px !important;
    }}
    .comment-box {{ font-size: 12px; background: {bg}; padding: 5px; border-radius: 5px; margin-top: 3px; border: 1px solid {brd}; }}
    </style>
    """, unsafe_allow_html=True)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ЛОГИКА ВХОДА ---
if not st.session_state.logged_in:
    st.title("🌌 MilkyGram")
    u = st.text_input("Позывной")
    p = st.text_input("Код", type="password")
    if st.button("Войти"):
        res = requests.get(f"{DB_URL}users/{u}.json").json()
        if res and res.get('password') == hash_pass(p):
            st.session_state.logged_in, st.session_state.username = True, u
            st.rerun()
    st.stop()

# --- ЗАГРУЗКА ДАННЫХ (После входа) ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
# Глобально определяем спутников, чтобы не было UnboundLocalError
st.session_state.my_satellites = all_users.get(st.session_state.username, {}).get('satellites', [])
if not isinstance(st.session_state.my_satellites, list): st.session_state.my_satellites = []

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
            # Используем session_state для проверки
            if name in st.session_state.my_satellites:
                if st.button("💥 Разорвать связь"):
                    st.session_state.my_satellites.remove(name)
                    requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": st.session_state.my_satellites})
                    st.rerun()
            else:
                if st.button("🔗 Установить связь"):
                    st.session_state.my_satellites.append(name)
                    requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": st.session_state.my_satellites})
                    st.rerun()

# --- МЕНЮ ---
with st.sidebar:
    st.write(f"### @{st.session_state.username}")
    if st.toggle("🌙", value=(st.session_state.theme == "Dark")): st.session_state.theme = "Dark"
    else: st.session_state.theme = "Light"
    
    st.write("---")
    if st.button("📡 Лента"): st.session_state.page, st.session_state.viewing_profile = "feed", None; st.rerun()
    if st.button("🔍 Поиск"): st.session_state.page, st.session_state.viewing_profile = "search", None; st.rerun()
    if st.button("📟 Радио"): st.session_state.page, st.session_state.viewing_profile = "dm", None; st.rerun()
    if st.button("🌌 Связи"): st.session_state.page, st.session_state.viewing_profile = "galaxy", None; st.rerun()
    if st.button("👨‍🚀 Профиль"): st.session_state.page, st.session_state.viewing_profile = "my_profile", None; st.rerun()
    if st.button("🚪 Выход"): st.session_state.logged_in = False; st.rerun()

# --- КОНТЕНТ ---
if st.session_state.viewing_profile:
    show_user_profile(st.session_state.viewing_profile)
    if st.button("← Назад"): st.session_state.viewing_profile = None; st.rerun()

elif st.session_state.page == "feed":
    st.title("Лента")
    with st.expander("📝 Создать пост"):
        img = st.text_input("URL фото")
        txt_post = st.text_area("Текст", height=60)
        if st.button("Отправить"):
            requests.post(f"{DB_URL}posts.json", json={"author": st.session_state.username, "img": img, "text": txt_post, "time": datetime.now().strftime("%H:%M"), "likes": 0})
            st.rerun()
    
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        with st.container(border=True):
            h1, h2 = st.columns([3, 1])
            if h1.button(f"@{p.get('author')}", key=f"f_{pid}"):
                st.session_state.viewing_profile = p.get('author'); st.rerun()
            h2.caption(p.get('time'))
            if p.get('img'): st.image(p['img'], width=300)
            st.write(p.get('text', ''))
            
            l1, l2 = st.columns([1, 5])
            if l1.button(f"✨ {p.get('likes', 0)}", key=f"lk_{pid}"):
                requests.patch(f"{DB_URL}posts/{pid}.json", json={"likes": p.get('likes', 0) + 1}); st.rerun()
            
            with st.expander("💬"):
                coms = p.get('comments', {})
                for c in coms.values():
                    st.markdown(f"<div class='comment-box'><b>{c['user']}</b> {c['txt']}</div>", unsafe_allow_html=True)
                c_in = st.text_input("...", key=f"in_{pid}", label_visibility="collapsed")
                if st.button("OK", key=f"s_{pid}"):
                    requests.post(f"{DB_URL}posts/{pid}/comments.json", json={"user": st.session_state.username, "txt": c_in}); st.rerun()

elif st.session_state.page == "dm":
    st.title("Радиоэфир")
    target = st.selectbox("Собеседник", [u for u in all_users.keys() if u != st.session_state.username])
    chat_id = "".join(sorted([st.session_state.username, target]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    for m in msgs.values():
        align = "right" if m['from'] == st.session_state.username else "left"
        st.markdown(f"<div style='text-align:{align};'><span style='background:#2D2D4D; padding:5px; border-radius:5px;'>{m['text']}</span></div>", unsafe_allow_html=True)
    m_in = st.text_input("Сообщение...")
    if st.button("Послать"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={"from": st.session_state.username, "text": m_in, "time": datetime.now().strftime("%H:%M")}); st.rerun()

elif st.session_state.page == "galaxy":
    st.title("Спутники")
    for s in st.session_state.my_satellites:
        if st.button(f"🛰️ @{s}", key=f"gal_{s}"): st.session_state.viewing_profile = s; st.rerun()

elif st.session_state.page == "my_profile":
    st.title("Настройки")
    new_a = st.text_input("Аватар URL", value=my_data.get('avatar', DEFAULT_AVA))
    new_b = st.text_area("О себе", value=my_data.get('bio', ''))
    if st.button("Сохранить"):
        requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"avatar": new_a, "bio": new_b}); st.rerun()
