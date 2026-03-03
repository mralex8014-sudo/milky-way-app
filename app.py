import streamlit as st
import requests
from datetime import datetime
import hashlib

# Настройка страницы
st.set_page_config(page_title="Млечный Путь: Соцсеть", page_icon="🚀")

# Ссылки на базу
URL_POSTS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"
URL_USERS = "https://milky-way-8ea60-default-rtdb.firebaseio.com/users.json"

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

st.title("🌌 Млечный Путь: Соцсеть")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    menu = ["Вход", "Регистрация"]
    choice = st.sidebar.selectbox("Меню", menu)
    
    username = st.sidebar.text_input("Имя пользователя")
    # ВОТ ТУТ ИСПРАВЛЕНО:
    password = st.sidebar.text_input("Пароль", type="password")
    
    if choice == "Регистрация":
        if st.sidebar.button("Создать аккаунт"):
            if username and password:
                res = requests.get(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{username}.json")
                if res.json():
                    st.error("Это имя уже занято!")
                else:
                    user_data = {"password": hash_pass(password)}
                    requests.put(f"https://milky-way-8ea60-default-rtdb.firebaseio.com/users/{username}.json", json=user_data)
                    st.success("Аккаунт создан! Теперь войдите.")
            else:
                st.warning("Заполните все поля")
                
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
    st.info("Пожалуйста, войдите, чтобы пользоваться соцсетью.")
    st.stop()

# Интерфейс после входа
st.sidebar.success(f"Вы вошли как: {st.session_state.username}")
if st.sidebar.button("Выйти"):
    st.session_state.logged_in = False
    st.rerun()

tab1, tab2 = st.tabs(["🌎 Общая лента", "✉️ Личные сообщения"])

with tab1:
    with st.form("post_form", clear_on_submit=True):
        text = st.text_area("Что нового?")
        if st.form_submit_button("Опубликовать"):
            if text:
                new_post = {"time": datetime.now().strftime("%H:%M"), "author": st.session_state.username, "text": text}
                requests.post(URL_POSTS, json=new_post)
                st.rerun()

    res = requests.get(URL_POSTS).json()
    if res:
        for p_id in reversed(list(res.keys())):
            p = res[p_id]
            st.markdown(f"**{p['author']}** ({p['time']})")
            st.write(p['text'])
            st.divider()

with tab2:
    st.subheader("Личные сообщения")
    st.write("Раздел в разработке... Наладим регистрацию и сразу запустим чаты!")
