import streamlit as st
import requests
from datetime import datetime

# 1. Настройка страницы — ВСЕГДА ПЕРВАЯ СТРОКА
st.set_page_config(page_title="Milky Way Online", page_icon="🌌")

# Ссылка на твою базу Firebase
URL_BASE = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"

st.title("🌌 Млечный Путь: Online")

# Боковая панель для имени
user_name = st.sidebar.text_input("Ваш никнейм", value="Странник")

# Форма для отправки поста
with st.form("post_form", clear_on_submit=True):
    text = st.text_area("О чем вы думаете?")
    submit = st.form_submit_button("Опубликовать")

    if submit and text:
        try:
            time_now = datetime.now().strftime("%H:%M")
            new_post = {"time": time_now, "author": user_name, "text": text}
            requests.post(URL_BASE, json=new_post)
            st.success("Пост улетел в космос!")
            st.rerun()
        except Exception as e:
            st.error(f"Ошибка связи с базой: {e}")

st.divider()
st.header("🔭 Мировая лента")

# Загрузка постов
try:
    response = requests.get(URL_BASE)
    all_posts = response.json()

    if all_posts:
        for p_id in reversed(list(all_posts.keys())):
            p = all_posts[p_id]
            st.subheader(f"{p.get('author', 'Аноним')} — {p.get('time', '00:00')}")
            st.write(p.get('text', ''))
            st.markdown("---")
    else:
        st.info("Лента пока пуста. Напишите что-нибудь первым!")
except Exception as e:
    st.error(f"Не удалось загрузить ленту: {e}")
