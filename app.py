import streamlit as st
import requests
from datetime import datetime

# 1. Настройка страницы (вкладка в браузере)
st.set_page_config(page_title="Млечный Путь: Online", page_icon="🌌")

# Ссылка на твою базу данных Firebase
URL_BASE = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"

# Главный заголовок
st.title("🌌 Млечный Путь: Online")

# 2. Боковая панель
st.sidebar.header("Настройки профиля")
user_name = st.sidebar.text_input("Ваше имя или никнейм", value="Странник")

# 3. Форма создания поста
with st.form("post_form", clear_on_submit=True):
    st.subheader("Опубликовать мысль")
    text = st.text_area("Что у вас нового?", placeholder="Напишите что-нибудь интересное...")
    submit = st.form_submit_button("Опубликовать")

    if submit and text:
        try:
            time_now = datetime.now().strftime("%H:%M")
            new_post = {"time": time_now, "author": user_name, "text": text}
            requests.post(URL_BASE, json=new_post)
            st.success("Ваше сообщение отправлено в ленту!")
            st.rerun()
        except Exception as e:
            st.error(f"Не удалось отправить: {e}")

st.divider()

# 4. Лента сообщений
st.header("🔭 Лента событий")

try:
    response = requests.get(URL_BASE)
    all_posts = response.json()

    if all_posts:
        # Показываем сообщения от новых к старым
        for p_id in reversed(list(all_posts.keys())):
            p = all_posts[p_id]
            # Создаем красивый блок сообщения
            with st.container():
                st.markdown(f"**{p.get('author', 'Аноним')}** — *{p.get('time', '00:00')}*")
                st.write(p.get('text', ''))
                st.divider()
    else:
        st.info("В ленте пока нет сообщений. Станьте первым!")
except Exception as e:
    st.error(f"Ошибка при загрузке ленты: {e}")
