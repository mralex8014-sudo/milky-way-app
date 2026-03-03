import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка
st.set_page_config(page_title="Млечный Путь: Профили", page_icon="🌌", layout="wide")

URL_POSTS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"
URL_USERS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/users.json"
URL_MESSAGES = "https://milky-way-8ea60-default-rtdb.firebaseio.com/messages.json"

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- АВТОРИЗАЦИЯ (справа сверху) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

head_col, auth_col = st.columns([3, 1])
with head_col:
    st.title("🌌 Млечный Путь")

with auth_col:
    if not st.session_state.logged_in:
        with st.expander("🔐 Вход"):
            mode = st.radio("Действие", ["Вход", "Регистрация"])
            u = st.text_input("Ник")
            p = st.text_input("Пароль", type="password")
            if st.button("ОК"):
                user_url = f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{u}.json"
                if mode == "Регистрация":
                    requests.put(user_url, json={"password": hash_pass(p), "avatar": "https://cdn-icons-png.flaticon.com/512/149/149071.png", "bio": "Новичок в космосе", "album": []})
                    st.success("Создано!")
                else:
                    data = requests.get(user_url).json()
                    if data and data['password'] == hash_pass(p):
                        st.session_state.logged_in, st.session_state.username = True, u
                        st.rerun()
    else:
        st.write(f"Привет, **{st.session_state.username}**")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

if not st.session_state.logged_in:
    st.info("Пожалуйста, войдите в систему.")
    st.stop()

# --- ГЛАВНОЕ МЕНЮ (справа) ---
main_col, menu_col = st.columns([3, 1])

with menu_col:
    st.subheader("Навигация")
    page = st.radio("Куда идем?", ["🌎 Лента", "👤 Мой Профиль", "✉️ Сообщения", "👥 Люди"])

with main_col:
    # --- СТРАНИЦА ПРОФИЛЯ ---
    if page == "👤 Мой Профиль":
        user_url = f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{st.session_state.username}.json"
        user_data = requests.get(user_url).json()

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(user_data.get('avatar', 'https://via.placeholder.com/150'), width=150)
            if st.button("Изменить аватар"):
                new_ava = st.text_input("Ссылка на новое фото:")
                if new_ava:
                    requests.patch(user_url, json={"avatar": new_ava})
                    st.rerun()
        
        with col2:
            st.header(st.session_state.username)
            st.write(f"**О себе:** {user_data.get('bio', '...')}")
            new_bio = st.text_input("Обновить статус:")
            if st.button("Сохранить статус"):
                requests.patch(user_url, json={"bio": new_bio})
                st.rerun()

        st.divider()
        
        # Альбом
        st.subheader("🖼️ Мой Фотоальбом")
        album_col1, album_col2 = st.columns(2)
        with album_col1:
            img_url = st.text_input("Добавить фото в альбом (ссылка):")
            if st.button("Добавить в альбом"):
                album = user_data.get('album', [])
                if isinstance(album, dict): album = list(album.values()) # Костыль для Firebase
                album.append(img_url)
                requests.patch(user_url, json={"album": album})
                st.rerun()
        
        # Показ альбома
        album = user_data.get('album', [])
        if album:
            cols = st.columns(3)
            for idx, img in enumerate(album):
                cols[idx % 3].image(img, use_container_width=True)
        else:
            st.write("Альбом пока пуст.")

    # --- ЛЕНТА (Общая) ---
    elif page == "🌎 Лента":
        st.header("Мировая лента")
        with st.form("post"):
            txt = st.text_area("Ваша мысль:")
            if st.form_submit_button("Опубликовать"):
                requests.post(URL_POSTS, json={"author": st.session_state.username, "text": txt, "time": datetime.now().strftime("%H:%M")})
                st.rerun()
        
        posts = requests.get(URL_POSTS).json()
        if posts:
            for p in reversed(list(posts.values())):
                st.chat_message("user").write(f"**{p['author']}**: {p['text']} ({p['time']})")

    # --- ОСТАЛЬНЫЕ РАЗДЕЛЫ (Сообщения и Люди остаются из прошлого кода) ---
    elif page == "✉️ Сообщения":
        st.write("Тут ваши чаты (логика из прошлого шага)")
    
    elif page == "👥 Люди":
        st.header("Жители сети")
        all_users = requests.get(URL_USERS).json()
        for name, data in all_users.items():
            col_u1, col_u2 = st.columns([1, 4])
            col_u1.image(data.get('avatar', 'https://via.placeholder.com/50'), width=50)
            col_u2.write(f"**{name}** — {data.get('bio', '')}")
