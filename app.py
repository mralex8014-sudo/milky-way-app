import streamlit as st
import requests
from datetime import datetime
import hashlib
import base64

# 1. Конфигурация страницы
st.set_page_config(page_title="MilkyGram", page_icon="📸", layout="centered")

# --- КАСТОМНЫЙ CSS (DARK INSTAGRAM STYLE) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; border-bottom: 1px solid #262626; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #FFFFFF !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #121212 !important; color: #FFFFFF !important; border: 1px solid #363636 !important;
    }
    .stButton>button {
        background-color: #0095f6 !important; color: white !important; border-radius: 8px !important; border: none !important; width: 100%;
    }
    .stExpander { background-color: #000000 !important; border: 1px solid #262626 !important; }
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
        background-color: #000000 !important; border: 1px solid #262626 !important; border-radius: 10px; padding: 10px;
    }
    hr { border: 0.5px solid #262626; }
    </style>
    """, unsafe_allow_html=True)

# Ссылки на Firebase
URL_POSTS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"
URL_USERS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/users.json"
URL_MESSAGES = "https://milky-way-8ea60-default-rtdb.firebaseio.com/messages.json"

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- СИСТЕМА ВХОДА ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Верхняя панель
col_head, col_log = st.columns([2, 1])
with col_head:
    st.header("📸 MilkyGram")

with col_log:
    if not st.session_state.logged_in:
        with st.expander("🔑 Вход"):
            mode = st.radio("Действие", ["Вход", "Регистрация"], label_visibility="collapsed")
            u_in = st.text_input("Никнейм", key="reg_u")
            p_in = st.text_input("Пароль", type="password", key="reg_p")
            if st.button("ОК"):
                user_url = f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{u_in}.json"
                if mode == "Регистрация":
                    requests.put(user_url, json={
                        "password": hash_pass(p_in),
                        "avatar": "https://cdn-icons-png.flaticon.com/512/149/149071.png",
                        "bio": "Космический странник",
                        "album": []
                    })
                    st.success("Готово! Войдите.")
                else:
                    data = requests.get(user_url).json()
                    if data and data['password'] == hash_pass(p_in):
                        st.session_state.logged_in = True
                        st.session_state.username = u_in
                        st.rerun()
                    else: st.error("Ошибка!")
    else:
        st.write(f"Привет, **{st.session_state.username}**")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

if not st.session_state.logged_in:
    st.stop()

# --- ГЛАВНАЯ НАВИГАЦИЯ ---
st.write("---")
page = st.selectbox("Меню", ["🌎 Лента", "🔍 Поиск людей", "👤 Мой Профиль", "✉️ Директ"], label_visibility="collapsed")
st.write("---")

all_users = requests.get(URL_USERS).json() or {}

# --- 1. ЛЕНТА ---
if page == "🌎 Лента":
    with st.expander("➕ Что нового?"):
        img = st.text_input("Ссылка на фото")
        txt = st.text_area("Описание")
        if st.button("Поделиться"):
            requests.post(URL_POSTS, json={
                "author": st.session_state.username,
                "img": img,
                "text": txt,
                "time": datetime.now().strftime("%H:%M")
            })
            st.rerun()

    posts = requests.get(URL_POSTS).json()
    if posts:
        for p_id in reversed(list(posts.keys())):
            p = posts[p_id]
            with st.container(border=True):
                st.markdown(f"**@{p['author']}**")
                if p.get('img'):
                    st.image(p['img'], use_container_width=True)
                st.write(p['text'])
                st.caption(f"🕒 {p['time']}")

# --- 2. ПОИСК ЛЮДЕЙ ---
elif page == "🔍 Поиск людей":
    st.subheader("Найти друзей")
    q = st.text_input("Введите никнейм для поиска...", placeholder="Например: admin")
    
    if q:
        filtered = {n: d for n, d in all_users.items() if q.lower() in n.lower()}
        if filtered:
            for n, d in filtered.items():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 4, 2])
                    c1.image(d.get('avatar'), width=50)
                    c2.write(f"**{n}**")
                    c2.caption(d.get('bio'))
                    if c3.button("В профиль", key=f"go_{n}"):
                        st.info(f"Это профиль @{n}") # В будущем сделаем переход
        else:
            st.warning("Никого не нашли...")
    else:
        # Показываем всех, если поиск пустой
        for n, d in list(all_users.items())[:10]:
            with st.container(border=True):
                c1, c2 = st.columns([1, 5])
                c1.image(d.get('avatar'), width=50)
                c2.write(f"**{n}**")

# --- 3. МОЙ ПРОФИЛЬ ---
elif page == "👤 Мой Профиль":
    me = all_users.get(st.session_state.username, {})
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(me.get('avatar'), width=150)
        new_a = st.text_input("Ссылка на аватар")
        if st.button("Сменить фото"):
            requests.patch(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{st.session_state.username}.json", json={"avatar": new_a})
            st.rerun()
    with col2:
        st.header(st.session_state.username)
        st.write(me.get('bio'))
        new_b = st.text_input("Новый статус")
        if st.button("Обновить био"):
            requests.patch(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{st.session_state.username}.json", json={"bio": new_b})
            st.rerun()

    st.divider()
    st.subheader("🖼️ Галерея")
    new_img = st.text_input("Добавить фото в альбом (URL)")
    if st.button("Добавить"):
        alb = me.get('album', [])
        if isinstance(alb, dict): alb = list(alb.values())
        alb.append(new_img)
        requests.patch(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{st.session_state.username}.json", json={"album": alb})
        st.rerun()
    
    alb_data = me.get('album', [])
    if alb_data:
        cols = st.columns(3)
        for i, img_url in enumerate(alb_data):
            cols[i % 3].image(img_url, use_container_width=True)

# --- 4. ДИРЕКТ ---
elif page == "✉️ Директ":
    st.subheader("Мессенджер")
    target = st.selectbox("Собеседник", [u for u in all_users.keys() if u != st.session_state.username])
    m_txt = st.text_input("Сообщение...")
    if st.button("Отправить"):
        requests.post(URL_MESSAGES, json={
            "from": st.session_state.username, "to": target, "text": m_txt, "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()

    st.write("---")
    msgs = requests.get(URL_MESSAGES).json()
    if msgs:
        for m in reversed(list(msgs.values())):
            if m['to'] == st.session_state.username or m['from'] == st.session_state.username:
                st.write(f"**{m['from']}**: {m['text']} ({m['time']})")
