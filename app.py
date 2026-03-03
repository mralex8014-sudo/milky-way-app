import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Конфигурация
st.set_page_config(page_title="MilkyGram", page_icon="📸", layout="wide")

# --- УЛУЧШЕННЫЙ ТЕМНЫЙ CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #262626; }
    .stButton>button {
        background-color: #0095f6; color: white; border-radius: 8px; border: none; width: 100%;
        font-weight: bold; margin-bottom: 10px;
    }
    .stButton>button:hover { background-color: #1877f2; border: none; color: white; }
    /* Стиль для активной "кнопки" меню */
    .menu-item { padding: 10px; border-radius: 8px; cursor: pointer; margin-bottom: 5px; }
    .stTextInput>div>div>input { background-color: #121212; color: white; border: 1px solid #363636; }
    </style>
    """, unsafe_allow_html=True)

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"

# --- ФУНКЦИИ ---
def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

def add_notif(to_u, txt):
    requests.post(f"{DB_URL}notifications/{to_u}.json", 
                  json={"from": st.session_state.username, "text": txt, "time": datetime.now().strftime("%H:%M"), "read": False})

# --- АВТОРИЗАЦИЯ ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("📸 MilkyGram")
    tab_in, tab_reg = st.tabs(["Вход", "Регистрация"])
    with tab_in:
        u = st.text_input("Username", key="u1")
        p = st.text_input("Password", type="password", key="p1")
        if st.button("Войти"):
            res = requests.get(f"{DB_URL}users/{u}.json").json()
            if res and res['password'] == hash_pass(p):
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
    with tab_reg:
        u2 = st.text_input("Придумайте ник", key="u2")
        p2 = st.text_input("Придумайте пароль", type="password", key="p2")
        if st.button("Создать аккаунт"):
            requests.put(f"{DB_URL}users/{u2}.json", json={"password": hash_pass(p2), "avatar": "https://cdn-icons-png.flaticon.com/512/149/149071.png", "bio": "Я в MilkyGram!"})
            st.success("Готово! Теперь войдите.")
    st.stop()

# --- БОКОВОЕ МЕНЮ (SIDEBAR) ---
with st.sidebar:
    st.title("MilkyGram")
    st.write(f"👤 **@{st.session_state.username}**")
    st.write("---")
    
    # Кнопки навигации
    if st.button("🌎 Лента"): st.session_state.page = "feed"
    if st.button("🔍 Поиск"): st.session_state.page = "search"
    if st.button("✉️ Директ"): st.session_state.page = "dm"
    
    # Считаем уведомления для кнопки
    notifs = requests.get(f"{DB_URL}notifications/{st.session_state.username}.json").json() or {}
    unread = len([n for n in notifs.values() if not n.get('read')])
    notif_btn_text = f"🔔 Уведомления ({unread})" if unread > 0 else "🔔 Уведомления"
    
    if st.button(notif_btn_text): st.session_state.page = "notifs"
    if st.button("👤 Профиль"): st.session_state.page = "profile"
    
    st.write("---")
    if st.button("🚪 Выход"):
        st.session_state.logged_in = False
        st.rerun()

# Установка страницы по умолчанию
if 'page' not in st.session_state: st.session_state.page = "feed"

# --- ОСНОВНОЙ КОНТЕНТ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}

# 1. ЛЕНТА
if st.session_state.page == "feed":
    st.header("Ваша лента")
    with st.expander("➕ Новый пост"):
        img = st.text_input("Ссылка на картинку")
        txt = st.text_area("Описание")
        if st.button("Опубликовать"):
            requests.post(f"{DB_URL}posts.json", json={"author": st.session_state.username, "img": img, "text": txt, "time": datetime.now().strftime("%H:%M")})
            st.rerun()
    
    posts = requests.get(f"{DB_URL}posts.json").json()
    if posts:
        for p in reversed(list(posts.values())):
            with st.container(border=True):
                st.write(f"**@{p['author']}**")
                if p.get('img'): st.image(p['img'], use_container_width=True)
                st.write(p['text'])

# 2. ПОИСК
elif st.session_state.page == "search":
    st.header("Поиск людей")
    q = st.text_input("Кого ищем?")
    for name, data in all_users.items():
        if q.lower() in name.lower():
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 2])
                c1.image(data.get('avatar'), width=50)
                c2.write(f"**{name}**")
                if c3.button("В друзья", key=f"f_{name}"):
                    add_notif(name, "отправил запрос в друзья! 🤝")
                    st.success("Запрос улетел!")

# 3. УВЕДОМЛЕНИЯ
elif st.session_state.page == "notifs":
    st.header("Уведомления")
    if notifs:
        for nid, n in reversed(list(notifs.items())):
            with st.container(border=True):
                st.write(f"**{n['from']}**: {n['text']} (🕒 {n['time']})")
                if not n.get('read'):
                    if st.button("Прочитано", key=nid):
                        requests.patch(f"{DB_URL}notifications/{st.session_state.username}/{nid}.json", json={"read": True})
                        st.rerun()
    else: st.write("Тишина...")

# 4. ДИРЕКТ
elif st.session_state.page == "dm":
    st.header("Сообщения")
    target = st.selectbox("Собеседник", [u for u in all_users.keys() if u != st.session_state.username])
    msg = st.text_input("Сообщение...")
    if st.button("Отправить"):
        requests.post(f"{DB_URL}messages.json", json={"from": st.session_state.username, "to": target, "text": msg, "time": datetime.now().strftime("%H:%M")})
        add_notif(target, f"написал вам: {msg[:15]}...")
        st.rerun()

# 5. ПРОФИЛЬ
elif st.session_state.page == "profile":
    me = all_users.get(st.session_state.username, {})
    st.header(f"Профиль @{st.session_state.username}")
    st.image(me.get('avatar'), width=150)
    new_a = st.text_input("Ссылка на фото", value=me.get('avatar'))
    new_b = st.text_area("О себе", value=me.get('bio'))
    if st.button("Сохранить"):
        requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"avatar": new_a, "bio": new_b})
        st.rerun()
