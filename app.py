import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Конфигурация страницы
st.set_page_config(page_title="MilkyGram", page_icon="📸", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЙ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = "feed"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"

# --- ДИНАМИЧЕСКИЙ CSS ---
if st.session_state.theme == "Dark":
    bg_col, txt_col, brd_col, input_bg = "#000000", "#FFFFFF", "#262626", "#121212"
else:
    bg_col, txt_col, brd_col, input_bg = "#FFFFFF", "#000000", "#DBDBDB", "#FAFAFA"

# ВАЖНО: Используем двойные {{ }} для CSS, чтобы не было ошибки format
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_col}; color: {txt_col}; }}
    [data-testid="stSidebar"] {{ background-color: {input_bg}; border-right: 1px solid {brd_col}; }}
    h1, h2, h3, h4, p, span, label {{ color: {txt_col} !important; }}
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {input_bg} !important; color: {txt_col} !important; border: 1px solid {brd_col} !important;
    }}
    
    .stButton>button {{
        background-color: #0095f6; color: white; border-radius: 8px; border: none; width: 100%;
        font-weight: bold; transition: 0.3s;
    }}
    
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {bg_col} !important; border: 1px solid {brd_col} !important; border-radius: 10px; padding: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ЛОГИКА ВХОДА ---
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
            else: st.error("Ошибка входа")
    with t2:
        u2 = st.text_input("Ник", key="u_reg")
        p2 = st.text_input("Пароль", type="password", key="p_reg")
        if st.button("Создать"):
            requests.put(f"{DB_URL}users/{u2}.json", json={"password": hash_pass(p2), "avatar": "https://cdn-icons-png.flaticon.com/512/149/149071.png", "bio": "Привет!"})
            st.success("Готово!")
    st.stop()

# --- МЕНЮ (SIDEBAR) ---
with st.sidebar:
    st.title("MilkyGram")
    st.write(f"👤 **@{st.session_state.username}**")
    
    theme_on = st.toggle("🌙 Темная тема", value=(st.session_state.theme == "Dark"))
    st.session_state.theme = "Dark" if theme_on else "Light"
    
    st.write("---")
    if st.button("🌎 Лента"): st.session_state.page = "feed"
    if st.button("🔍 Поиск"): st.session_state.page = "search"
    if st.button("✉️ Директ"): st.session_state.page = "dm"
    
    # Безопасное получение уведомлений
    notifs_raw = requests.get(f"{DB_URL}notifications/{st.session_state.username}.json").json()
    notifs = notifs_raw if notifs_raw else {}
    unread = len([n for n in notifs.values() if isinstance(n, dict) and not n.get('read')])
    
    if st.button(f"🔔 Уведомления ({unread})" if unread > 0 else "🔔 Уведомления"): st.session_state.page = "notifs"
    if st.button("👤 Профиль"): st.session_state.page = "profile"
    
    st.write("---")
    if st.button("🚪 Выход"):
        st.session_state.logged_in = False
        st.rerun()

# --- КОНТЕНТ ---
# Защита от пустого списка пользователей
all_users = requests.get(f"{DB_URL}users.json").json() or {}

if st.session_state.page == "feed":
    st.header("Лента")
    with st.expander("➕ Поделиться моментом"):
        img_url = st.text_input("Ссылка на фото")
        cap = st.text_area("Описание")
        if st.button("Опубликовать"):
            requests.post(f"{DB_URL}posts.json", json={"author": st.session_state.username, "img": img_url, "text": cap, "time": datetime.now().strftime("%H:%M")})
            st.rerun()

    posts = requests.get(f"{DB_URL}posts.json").json()
    if posts:
        for p in reversed(list(posts.values())):
            with st.container(border=True):
                st.write(f"**@{p.get('author', 'unknown')}**")
                if p.get('img'): st.image(p['img'], use_container_width=True)
                st.write(p.get('text', ''))
    else: st.write("Лента пока пуста")

elif st.session_state.page == "search":
    st.header("Поиск")
    q = st.text_input("Кого ищем?")
    if q:
        for n, d in all_users.items():
            if q.lower() in n.lower():
                with st.container(border=True):
                    st.write(f"👤 **{n}**")
                    if st.button("Перейти в чат", key=n):
                        st.session_state.page = "dm"
                        st.rerun()

elif st.session_state.page == "profile":
    me = all_users.get(st.session_state.username, {})
    st.header("Профиль")
    st.image(me.get('avatar', 'https://via.placeholder.com/150'), width=150)
    new_a = st.text_input("Фото (URL)", value=me.get('avatar', ''))
    new_b = st.text_area("О себе", value=me.get('bio', ''))
    if st.button("Сохранить изменения"):
        requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"avatar": new_a, "bio": new_b})
        st.success("Обновлено!")
        st.rerun()

elif st.session_state.page == "notifs":
    st.header("Уведомления")
    if notifs:
        for nid, n in reversed(list(notifs.items())):
            st.info(f"{n.get('from', 'System')}: {n.get('text', '')} ({n.get('time', '')})")
    else: st.write("Новых уведомлений нет.")

elif st.session_state.page == "dm":
    st.header("Директ")
    st.write("Мессенджер в разработке...")
