import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка страницы
st.set_page_config(page_title="MilkyGram", page_icon="📸", layout="wide")

# --- СОСТОЯНИЯ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = "feed"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"

# Стандартная аватарка, если в базе пусто
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# --- CSS С ДВОЙНЫМИ СКОБКАМИ (чтобы не было AttributeError) ---
bg, txt, brd, inp = ("#000000", "#FFFFFF", "#262626", "#121212") if st.session_state.theme == "Dark" else ("#FFFFFF", "#000000", "#DBDBDB", "#FAFAFA")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {inp}; border-right: 1px solid {brd}; }}
    h1, h2, h3, h4, p, span, label {{ color: {txt} !important; }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {inp} !important; color: {txt} !important; border: 1px solid {brd} !important;
    }}
    .stButton>button {{
        background-color: #0095f6; color: white; border-radius: 8px; border: none; width: 100%; font-weight: bold;
    }}
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {bg} !important; border: 1px solid {brd} !important; border-radius: 10px; padding: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ВХОД ---
if not st.session_state.logged_in:
    st.title("📸 MilkyGram")
    t1, t2 = st.tabs(["Вход", "Регистрация"])
    with t1:
        u = st.text_input("Username", key="u_log")
        p = st.text_input("Password", type="password", key="p_log")
        if st.button("Войти"):
            res = requests.get(f"{DB_URL}users/{u}.json").json()
            if res and res.get('password') == hash_pass(p):
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
            else: st.error("Ошибка!")
    with t2:
        u2 = st.text_input("Ник", key="u_reg")
        p2 = st.text_input("Пароль", type="password", key="p_reg")
        if st.button("Создать"):
            requests.put(f"{DB_URL}users/{u2}.json", json={"password": hash_pass(p2), "avatar": DEFAULT_AVA, "bio": "Новичок"})
            st.success("Аккаунт создан!")
    st.stop()

# --- МЕНЮ ---
with st.sidebar:
    st.title("MilkyGram")
    theme_on = st.toggle("🌙 Темная тема", value=(st.session_state.theme == "Dark"))
    st.session_state.theme = "Dark" if theme_on else "Light"
    
    st.write("---")
    if st.button("🌎 Лента"): st.session_state.page = "feed"
    if st.button("🔍 Поиск"): st.session_state.page = "search"
    
    notifs = requests.get(f"{DB_URL}notifications/{st.session_state.username}.json").json() or {}
    unread = len([n for n in notifs.values() if isinstance(n, dict) and not n.get('read')])
    if st.button(f"🔔 Уведомления ({unread})" if unread > 0 else "🔔 Уведомления"): st.session_state.page = "notifs"
    if st.button("👤 Профиль"): st.session_state.page = "profile"
    
    if st.button("🚪 Выход"):
        st.session_state.logged_in = False
        st.rerun()

# --- КОНТЕНТ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}

if st.session_state.page == "feed":
    st.header("Лента")
    with st.expander("➕ Пост"):
        img = st.text_input("URL картинки")
        cap = st.text_area("Текст")
        if st.button("Публикация"):
            requests.post(f"{DB_URL}posts.json", json={"author": st.session_state.username, "img": img, "text": cap, "time": datetime.now().strftime("%H:%M")})
            st.rerun()

    posts = requests.get(f"{DB_URL}posts.json").json()
    if posts:
        for p in reversed(list(posts.values())):
            with st.container(border=True):
                st.write(f"**@{p.get('author')}**")
                # ЗАЩИТА: проверяем, что ссылка не пустая
                p_img = p.get('img')
                if p_img and p_img.strip() != "":
                    st.image(p_img, use_container_width=True)
                st.write(p.get('text', ''))

elif st.session_state.page == "search":
    st.header("Поиск")
    q = st.text_input("Имя...")
    if q:
        for n, d in all_users.items():
            if q.lower() in n.lower():
                with st.container(border=True):
                    c1, c2 = st.columns([1, 5])
                    # ЗАЩИТА: если аватар пуст, ставим DEFAULT_AVA
                    ava = d.get('avatar') if d.get('avatar') else DEFAULT_AVA
                    c1.image(ava, width=50)
                    c2.write(f"**{n}**")

elif st.session_state.page == "profile":
    me = all_users.get(st.session_state.username, {})
    st.header("Профиль")
    # ЗАЩИТА АВАТАРА
    my_ava = me.get('avatar') if me.get('avatar') else DEFAULT_AVA
    st.image(my_ava, width=150)
    
    new_a = st.text_input("Новый аватар (URL)", value=my_ava)
    new_b = st.text_area("О себе", value=me.get('bio', ''))
    if st.button("Сохранить"):
        requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"avatar": new_a, "bio": new_b})
        st.rerun()

elif st.session_state.page == "notifs":
    st.header("Уведомления")
    if notifs:
        for nid, n in reversed(list(notifs.items())):
            st.info(f"{n.get('from')}: {n.get('text')}")
    else: st.write("Пусто")
