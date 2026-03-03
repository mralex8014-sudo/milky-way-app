import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Конфигурация в стиле соцсети
st.set_page_config(page_title="MilkyGram", page_icon="📸", layout="centered")

# Кастомный CSS для "инстаграмного" вида
st.markdown("""
    <style>
    .stApp { background-color: white; }
    [data-testid="stHeader"] { background-color: white; border-bottom: 1px solid #dbdbdb; }
    .stButton>button { width: 100%; border-radius: 8px; }
    img { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

URL_POSTS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"
URL_USERS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/users.json"

# --- ШАПКА (Header) ---
col_logo, col_search, col_nav = st.columns([1, 1, 1])
with col_logo:
    st.subheader("MilkyGram")

# --- ЛОГИКА ВХОДА ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.warning("Пожалуйста, войдите в свой аккаунт")
    with st.expander("🔑 Авторизация", expanded=True):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Войти"):
            res = requests.get(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{u}.json").json()
            if res and res['password'] == hashlib.sha256(str.encode(p)).hexdigest():
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
    st.stop()

# --- STORIES (Ряд аватарок) ---
users_data = requests.get(URL_USERS).json() or {}
st.write("---")
story_cols = st.columns(7)
for i, (name, data) in enumerate(list(users_data.items())[:7]):
    with story_cols[i]:
        st.image(data.get('avatar', 'https://via.placeholder.com/150'), width=60)
        st.caption(name[:7])
st.write("---")

# --- ОСНОВНАЯ ЛЕНТА ---
# Кнопка создания поста (как "+" в инстаграме)
with st.expander("➕ Создать новый пост"):
    img_url = st.text_input("Ссылка на фото")
    caption = st.text_area("Описание")
    if st.button("Опубликовать"):
        new_p = {"author": st.session_state.username, "img": img_url, "text": caption, "time": datetime.now().strftime("%d.%m %H:%M")}
        requests.post(URL_POSTS, json=new_p)
        st.rerun()

# Отображение постов
posts = requests.get(URL_POSTS).json()
if posts:
    for p_id in reversed(list(posts.keys())):
        p = posts[p_id]
        with st.container(border=True):
            # Шапка поста
            c1, c2 = st.columns([1, 6])
            author_data = users_data.get(p['author'], {})
            c1.image(author_data.get('avatar', 'https://via.placeholder.com/50'), width=40)
            c2.markdown(f"**{p['author']}**")
            
            # Контент
            if p.get('img'):
                st.image(p['img'], use_container_width=True)
            
            st.write(f"**{p['author']}** {p['text']}")
            st.caption(f"Опубликовано: {p['time']}")
            
            # Интерактивы
            like_col, comm_col = st.columns([1, 5])
            like_col.button("❤️", key=f"like_{p_id}")
            comm_col.button("💬", key=f"comm_{p_id}")
