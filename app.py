import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Конфигурация
st.set_page_config(page_title="MilkyGram", page_icon="📸", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЙ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = "feed"
if 'theme' not in st.session_state: st.session_state.theme = "Dark" # По умолчанию темная

# --- ДИНАМИЧЕСКИЙ CSS (Светлая / Темная темы) ---
if st.session_state.theme == "Dark":
    bg_col, txt_col, brd_col, input_bg = "#000000", "#FFFFFF", "#262626", "#121212"
else:
    bg_col, txt_col, brd_col, input_bg = "#FFFFFF", "#000000", "#DBDBDB", "#FAFAFA"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_col}; color: {txt_col}; }}
    [data-testid="stSidebar"] {{ background-color: {input_bg}; border-right: 1px solid {brd_col}; }}
    h1, h2, h3, p, span, label {{ color: {txt_col} !important; }}
    
    /* Поля ввода */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {input_bg} !important; color: {txt_col} !important; border: 1px solid {brd_col} !important;
    }}
    
    /* Кнопки навигации и действий */
    .stButton>button {{
        background-color: #0095f6; color: white; border-radius: 8px; border: none; width: 100%;
        font-weight: bold; transition: 0.3s;
    }}
    .stButton>button:hover {{ background-color: #1877f2; color: white; border: none; }}
    
    /* Карточки постов */
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {bg_col} !important; border: 1px solid {brd_col} !important; border-radius: 10px; padding: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"

# --- ФУНКЦИИ ---
def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()
def add_notif(to_u, txt):
    requests.post(f"{DB_URL}notifications/{to_u}.json", 
                  json={{"from": st.session_state.username, "text": txt, "time": datetime.now().strftime("%H:%M"), "read": False}})

# --- АВТОРИЗАЦИЯ ---
if not st.session_state.logged_in:
    st.title("📸 MilkyGram")
    t1, t2 = st.tabs(["Вход", "Регистрация"])
    with t1:
        u = st.text_input("Username", key="u_in")
        p = st.text_input("Password", type="password", key="p_in")
        if st.button("Войти"):
            res = requests.get(f"{DB_URL}users/{u}.json").json()
            if res and res['password'] == hash_pass(p):
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
    with t2:
        u2 = st.text_input("Никнейм", key="u_reg")
        p2 = st.text_input("Пароль", type="password", key="p_reg")
        if st.button("Создать"):
            requests.put(f"{DB_URL}users/{u2}.json", json={{"password": hash_pass(p2), "avatar": "https://cdn-icons-png.flaticon.com/512/149/149071.png", "bio": "Привет!"}})
            st.success("Аккаунт создан!")
    st.stop()

# --- БОКОВОЕ МЕНЮ (SIDEBAR) ---
with st.sidebar:
    st.title("MilkyGram")
    st.write(f"👤 **@{st.session_state.username}**")
    
    # ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ
    st.write("---")
    theme_choice = st.toggle("🌙 Темная тема", value=(st.session_state.theme == "Dark"))
    new_theme = "Dark" if theme_choice else "Light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
    st.write("---")
    
    # Кнопки навигации
    if st.button("🌎 Лента"): st.session_state.page = "feed"
    if st.button("🔍 Поиск"): st.session_state.page = "search"
    if st.button("✉️ Директ"): st.session_state.page = "dm"
    
    notifs = requests.get(f"{DB_URL}notifications/{st.session_state.username}.json").json() or {}
    unread = len([n for n in notifs.values() if not n.get('read')])
    if st.button(f"🔔 Уведомления ({unread})" if unread > 0 else "🔔 Уведомления"): st.session_state.page = "notifs"
    
    if st.button("👤 Профиль"): st.session_state.page = "profile"
    
    st.write("---")
    if st.button("🚪 Выйти"):
        st.session_state.logged_in = False
        st.rerun()

# --- КОНТЕНТ (Упрощенно для примера структуры) ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}

if st.session_state.page == "feed":
    st.header("Лента")
    # ... тут твой код ленты из прошлого шага ...
    posts = requests.get(f"{DB_URL}posts.json").json()
    if posts:
        for p in reversed(list(posts.values())):
            with st.container(border=True):
                st.write(f"**@{p['author']}**")
                if p.get('img'): st.image(p['img'], use_container_width=True)
                st.write(p['text'])

elif st.session_state.page == "search":
    st.header("Поиск")
    q = st.text_input("Найти...")
    for name, data in all_users.items():
        if q.lower() in name.lower():
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 2])
                c1.image(data.get('avatar'), width=50)
                c2.write(f"**{name}**")
                if c3.button("В друзья", key=name):
                    add_notif(name, "хочет дружить!")
                    st.success("Запрос отправлен")

elif st.session_state.page == "profile":
    me = all_users.get(st.session_state.username, {})
    st.header("Мой профиль")
    st.image(me.get('avatar'), width=150)
    st.write(f"**Био:** {me.get('bio')}")
    # ... тут твой код профиля ...

elif st.session_state.page == "notifs":
    st.header("Уведомления")
    for nid, n in reversed(list(notifs.items())):
        st.info(f"{n['from']}: {n['text']} ({n['time']})")

elif st.session_state.page == "dm":
    st.header("Директ")
    # ... тут твой код сообщений ...
