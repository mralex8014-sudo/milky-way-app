import streamlit as st
import requests
from datetime import datetime
import hashlib
import base64

# 1. Настройка страницы (Instagram Style)
st.set_page_config(page_title="MilkyGram", page_icon="📸", layout="centered")

# --- КАСТОМНЫЙ CSS ДЛЯ ТЕМНОЙ ТЕМЫ ---
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
    /* Стиль карточки поста */
    .post-card {
        border: 1px solid #262626; border-radius: 8px; padding: 15px; margin-bottom: 20px; background-color: #000000;
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

# --- ЛОГИКА АВТОРИЗАЦИИ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Шапка сайта
col_logo, col_auth = st.columns([2, 1])
with col_logo:
    st.header("📸 MilkyGram")

with col_auth:
    if not st.session_state.logged_in:
        with st.expander("🔐 Вход"):
            mode = st.radio("Действие", ["Вход", "Регистрация"], label_visibility="collapsed")
            u_in = st.text_input("Никнейм", key="login_u")
            p_in = st.text_input("Пароль", type="password", key="login_p")
            if st.button("Подтвердить"):
                user_url = f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{u_in}.json"
                if mode == "Регистрация":
                    requests.put(user_url, json={
                        "password": hash_pass(p_in),
                        "avatar": "https://cdn-icons-png.flaticon.com/512/149/149071.png",
                        "bio": "Новый участник системы",
                        "album": []
                    })
                    st.success("Аккаунт создан!")
                else:
                    user_data = requests.get(user_url).json()
                    if user_data and user_data['password'] == hash_pass(p_in):
                        st.session_state.logged_in = True
                        st.session_state.username = u_in
                        st.rerun()
                    else: st.error("Ошибка входа")
    else:
        st.write(f"👤 **{st.session_state.username}**")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

if not st.session_state.logged_in:
    st.info("Добро пожаловать в MilkyGram! Войдите, чтобы увидеть ленту.")
    st.stop()

# --- МЕНЮ НАВИГАЦИИ ---
st.write("---")
page = st.selectbox("Навигация", ["🌎 Лента", "👤 Мой Профиль", "✉️ Директ", "👥 Люди"], label_visibility="collapsed")
st.write("---")

# Загрузка данных пользователей для аватарок и имен
all_users = requests.get(URL_USERS).json() or {}

# --- СТРАНИЦА: ЛЕНТА ---
if page == "🌎 Лента":
    # Кнопка создания поста
    with st.expander("➕ Создать публикацию"):
        post_img = st.text_input("Ссылка на фото (URL)")
        post_txt = st.text_area("Описание поста")
        if st.button("Опубликовать"):
            new_post = {
                "author": st.session_state.username,
                "img": post_img,
                "text": post_txt,
                "time": datetime.now().strftime("%H:%M")
            }
            requests.post(URL_POSTS, json=new_post)
            st.rerun()

    # Отображение ленты
    posts = requests.get(URL_POSTS).json()
    if posts:
        for p_id in reversed(list(posts.keys())):
            p = posts[p_id]
            author_info = all_users.get(p['author'], {})
            
            with st.container():
                st.markdown(f"**@{p['author']}**")
                if p.get('img'):
                    st.image(p['img'], use_container_width=True)
                st.write(f"**{p['author']}**: {p['text']}")
                st.caption(f"🕒 {p['time']}")
                col1, col2 = st.columns([1, 8])
                col1.button("❤️", key=f"like_{p_id}")
                st.write("---")

# --- СТРАНИЦА: ПРОФИЛЬ ---
elif page == "👤 Мой Профиль":
    my_data = all_users.get(st.session_state.username, {})
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        st.image(my_data.get('avatar'), width=150)
        new_ava = st.text_input("Ссылка на новый аватар")
        if st.button("Обновить фото"):
            requests.patch(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{st.session_state.username}.json", json={"avatar": new_ava})
            st.rerun()

    with col_p2:
        st.header(st.session_state.username)
        st.write(f"ℹ️ {my_data.get('bio')}")
        new_bio = st.text_input("Изменить статус")
        if st.button("Сохранить био"):
            requests.patch(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{st.session_state.username}.json", json={"bio": new_bio})
            st.rerun()

    st.subheader("🖼️ Моя галерея")
    album_link = st.text_input("Добавить фото в альбом (URL)")
    if st.button("Добавить"):
        album = my_data.get('album', [])
        if isinstance(album, dict): album = list(album.values())
        album.append(album_link)
        requests.patch(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{st.session_state.username}.json", json={"album": album})
        st.rerun()
    
    current_album = my_data.get('album', [])
    if current_album:
        cols = st.columns(3)
        for i, img in enumerate(current_album):
            cols[i % 3].image(img, use_container_width=True)

# --- СТРАНИЦА: ДИРЕКТ ---
elif page == "✉️ Директ":
    st.subheader("Личные сообщения")
    recipient = st.selectbox("Кому пишем?", [u for u in all_users.keys() if u != st.session_state.username])
    
    msg_input = st.text_input("Напишите сообщение...")
    if st.button("Отправить"):
        requests.post(URL_MESSAGES, json={
            "from": st.session_state.username,
            "to": recipient,
            "text": msg_input,
            "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()

    st.write("---")
    msgs = requests.get(URL_MESSAGES).json()
    if msgs:
        for m in reversed(list(msgs.values())):
            if m['to'] == st.session_state.username or m['from'] == st.session_state.username:
                side = "📩" if m['to'] == st.session_state.username else "📤"
                st.write(f"{side} **{m['from']}**: {m['text']} ({m['time']})")

# --- СТРАНИЦА: ЛЮДИ ---
elif page == "👥 Люди":
    st.subheader("Пользователи сети")
    for name, data in all_users.items():
        with st.container(border=True):
            c_u1, c_u2 = st.columns([1, 5])
            c_u1.image(data.get('avatar'), width=50)
            c_u2.write(f"**{name}**")
            c_u2.caption(data.get('bio'))
