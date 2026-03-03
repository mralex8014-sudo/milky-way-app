import streamlit as st
import requests
from datetime import datetime
import hashlib

# Настройка страницы
st.set_page_config(page_title="Млечный Путь: Соцсеть", page_icon="🚀")

# Ссылки на базу (разделяем посты и пользователей)
URL_POSTS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"
URL_USERS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/users.json"

# Функция для шифрования пароля (чтобы не хранить их открыто)
def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

st.title("🌌 Млечный Путь: Соцсеть")

# --- СИСТЕМА ВХОДА ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    menu = ["Вход", "Регистрация"]
    choice = st.sidebar.selectbox("Меню", menu)
    
    username = st.sidebar.text_input("Имя пользователя")
    password = st.sidebar.password_input("Пароль")
    
    if choice == "Регистрация":
        if st.sidebar.button("Создать аккаунт"):
            # Проверяем, существует ли пользователь
            res = requests.get(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{username}.json")
            if res.json():
                st.error("Это имя уже занято!")
            else:
                user_data = {"password": hash_pass(password)}
                requests.put(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{username}.json", json=user_data)
                st.success("Аккаунт создан! Теперь войдите.")
                
    else: # Вход
        if st.sidebar.button("Войти"):
            res = requests.get(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{username}.json")
            user_data = res.json()
            if user_data and user_data['password'] == hash_pass(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Неверное имя или пароль")
    st.info("Пожалуйста, войдите, чтобы читать ленту и писать сообщения.")
    st.stop() # Останавливаем код, пока человек не войдет

# --- ИНТЕРФЕЙС ДЛЯ АВТОРИЗОВАННЫХ ---
st.sidebar.success(f"Вы вошли как: {st.session_state.username}")
if st.sidebar.button("Выйти"):
    st.session_state.logged_in = False
    st.rerun()

# Вкладки: Лента и Личные сообщения
tab1, tab2 = st.tabs(["🌎 Общая лента", "✉️ Личные сообщения"])

with tab1:
    with st.form("post_form", clear_on_submit=True):
        text = st.text_area("Что нового?")
        if st.form_submit_button("Опубликовать"):
            if text:
                new_post = {"time": datetime.now().strftime("%H:%M"), "author": st.session_state.username, "text": text}
                requests.post(URL_POSTS, json=new_post)
                st.rerun()

    # Показ постов
    res = requests.get(URL_POSTS).json()
    if res:
        for p_id in reversed(list(res.keys())):
            p = res[p_id]
            st.markdown(f"**{p['author']}** ({p['time']})")
            st.write(p['text'])
            st.divider()

with tab2:
    st.subheader("Ваши переписки")
    # Здесь мы позже добавим выбор друга и чат
    st.write("Раздел в разработке... Скоро здесь можно будет выбрать друга!")
