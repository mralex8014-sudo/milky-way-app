import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка страницы
st.set_page_config(page_title="Млечный Путь", page_icon="🌌", layout="wide")

# База данных
URL_POSTS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"
URL_USERS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/users.json"
URL_MESSAGES = "https://milky-way-8ea60-default-rtdb.firebaseio.com/messages.json"

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- ВЕРХНЯЯ ПАНЕЛЬ И ЛОГИКА ВХОДА ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Создаем две колонки: Заголовок и Кнопка входа
head_col, auth_col = st.columns([3, 1])

with head_col:
    st.title("🌌 Млечный Путь")

with auth_col:
    if not st.session_state.logged_in:
        with st.expander("🔐 Вход / Регистрация"):
            mode = st.radio("Действие", ["Вход", "Регистрация"], label_visibility="collapsed")
            user_in = st.text_input("Никнейм", key="u_in")
            pass_in = st.text_input("Пароль", type="password", key="p_in")
            
            if st.button("Подтвердить"):
                if mode == "Регистрация":
                    res = requests.get(f"{URL_USERS.replace('.json', f'/{user_in}.json')}")
                    if res.json(): st.error("Занято!")
                    else:
                        requests.put(f"{URL_USERS.replace('.json', f'/{user_in}.json')}", json={"password": hash_pass(pass_in)})
                        st.success("Создано! Войдите.")
                else:
                    res = requests.get(f"{URL_USERS.replace('.json', f'/{user_in}.json')}")
                    data = res.json()
                    if data and data['password'] == hash_pass(pass_in):
                        st.session_state.logged_in, st.session_state.username = True, user_in
                        st.rerun()
                    else: st.error("Ошибка")
    else:
        st.write(f"👤 **{st.session_state.username}**")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

st.divider()

# --- ОСНОВНОЙ КОНТЕНТ И МЕНЮ СПРАВА ---
if not st.session_state.logged_in:
    st.info("Войдите через панель справа сверху, чтобы увидеть ленту.")
    st.stop()

# Делим экран на Контент (слева) и Меню (справа)
main_col, menu_col = st.columns([3, 1])

with menu_col:
    st.subheader("Меню 🧭")
    page = st.radio("Перейти:", ["🌎 Лента", "✉️ Сообщения", "👥 Люди"], label_visibility="collapsed")
    
    st.divider()
    st.caption("Статистика сети")
    st.write("Онлайн: 🟢 Много")

with main_col:
    if page == "🌎 Лента":
        st.header("Мировая лента")
        with st.form("new_post"):
            txt = st.text_area("Что нового?")
            if st.form_submit_button("Опубликовать"):
                requests.post(URL_POSTS, json={"author": st.session_state.username, "text": txt, "time": datetime.now().strftime("%H:%M")})
                st.rerun()
        
        posts = requests.get(URL_POSTS).json()
        if posts:
            for p in reversed(list(posts.values())):
                with st.chat_message("user"):
                    st.write(f"**{p['author']}** — {p['time']}")
                    st.write(p['text'])

    elif page == "✉️ Сообщения":
        st.header("Ваши чаты")
        all_u = requests.get(URL_USERS).json()
        recipient = st.selectbox("Собеседник", [u for u in all_u.keys() if u != st.session_state.username])
        
        with st.container(border=True):
            msg_text = st.text_input("Написать...")
            if st.button("Отправить"):
                requests.post(URL_MESSAGES, json={"from": st.session_state.username, "to": recipient, "text": msg_text, "time": datetime.now().strftime("%H:%M")})
                st.rerun()
        
        msgs = requests.get(URL_MESSAGES).json()
        if msgs:
            for m in reversed(list(msgs.values())):
                if m['to'] == st.session_state.username or m['from'] == st.session_state.username:
                    align = "←" if m['to'] == st.session_state.username else "→"
                    st.write(f"{align} **{m['from']}**: {m['text']} *({m['time']})*")

    elif page == "👥 Люди":
        st.header("Пользователи")
        users = requests.get(URL_USERS).json()
        for u in users.keys():
            st.write(f"🌟 {u}")
