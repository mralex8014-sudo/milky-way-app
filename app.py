import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка и Константы
st.set_page_config(page_title="Млечный Путь: Соцсеть", page_icon="🌌")
URL_POSTS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"
URL_USERS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/users.json"
URL_MESSAGES = "https://milky-way-8ea60-default-rtdb.firebaseio.com/messages.json"

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

st.title("🌌 Млечный Путь: Online")

# --- ЛОГИКА ВХОДА ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    menu = ["Вход", "Регистрация"]
    choice = st.sidebar.selectbox("Меню", menu)
    username = st.sidebar.text_input("Имя пользователя")
    password = st.sidebar.text_input("Пароль", type="password")
    
    if choice == "Регистрация":
        if st.sidebar.button("Создать аккаунт"):
            if username and password:
                res = requests.get(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{username}.json")
                if res.json(): st.error("Имя занято!")
                else:
                    requests.put(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{username}.json", json={"password": hash_pass(password)})
                    st.success("Готово! Войдите.")
    else:
        if st.sidebar.button("Войти"):
            res = requests.get(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{username}.json")
            user_data = res.json()
            if user_data and user_data['password'] == hash_pass(password):
                st.session_state.logged_in, st.session_state.username = True, username
                st.rerun()
            else: st.error("Ошибка входа")
    st.stop()

# --- ПАНЕЛЬ УПРАВЛЕНИЯ ---
st.sidebar.write(f"Привет, **{st.session_state.username}**!")
if st.sidebar.button("Выйти"):
    st.session_state.logged_in = False
    st.rerun()

# Вкладки
tab1, tab2, tab3 = st.tabs(["🌎 Лента", "✉️ Сообщения", "👥 Люди"])

# Вкладка 1: Общая лента
with tab1:
    with st.form("post"):
        txt = st.text_area("Ваша новость:")
        if st.form_submit_button("Поделиться"):
            requests.post(URL_POSTS, json={"author": st.session_state.username, "text": txt, "time": datetime.now().strftime("%H:%M")})
            st.rerun()
    
    posts = requests.get(URL_POSTS).json()
    if posts:
        for p in reversed(list(posts.values())):
            st.info(f"**{p['author']}** ({p['time']})\n\n{p['text']}")

# Вкладка 3: Список людей (сначала сделаем её для выбора собеседника)
with tab3:
    st.subheader("Жители Млечного Пути")
    all_users_res = requests.get(URL_USERS).json()
    if all_users_res:
        users_list = list(all_users_res.keys())
        for user in users_list:
            st.write(f"👤 {user}")
    else:
        st.write("Тут пока только ты...")

# Вкладка 2: Личные сообщения
with tab2:
    if all_users_res:
        recipient = st.selectbox("Кому отправить сообщение?", [u for u in users_list if u != st.session_state.username])
        msg_text = st.text_input("Ваше сообщение", key="msg_input")
        if st.button("Отправить ЛС"):
            if msg_text:
                new_msg = {
                    "from": st.session_state.username,
                    "to": recipient,
                    "text": msg_text,
                    "time": datetime.now().strftime("%H:%M")
                }
                requests.post(URL_MESSAGES, json=new_msg)
                st.success("Отправлено!")
        
        st.divider()
        st.subheader("Ваша переписка")
        msgs = requests.get(URL_MESSAGES).json()
        if msgs:
            for m in reversed(list(msgs.values())):
                # Показываем только если я отправитель или я получатель
                if m['to'] == st.session_state.username or m['from'] == st.session_state.username:
                    color = "blue" if m['from'] == st.session_state.username else "green"
                    st.markdown(f"**{m['from']}** ➔ **{m['to']}** ({m['time']})")
                    st.write(m['text'])
                    st.markdown("---")
