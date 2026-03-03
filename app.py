import streamlit as st
import requests
from datetime import datetime

# 1. Настройка страницы
st.set_page_config(page_title="MilkyGram | Моя Страница", layout="wide")

# --- Инициализация ---
for key, val in {
    'username': "Pilot_Alpha", 'page': "profile", 'logged_in': True, 'viewing_profile': None
}.items():
    if key not in st.session_state: st.session_state[key] = val

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ВК-СТИЛЬ 2026 ---
st.markdown("""
<style>
    .stApp { background-color: #0A0A12; }
    
    /* Контейнеры-блоки */
    .vk-card {
        background-color: #19191B;
        border: 1px solid #2D2D2E;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    
    /* Заголовки */
    .vk-name { color: #E1E3E6; font-size: 22px; font-weight: 500; margin-bottom: 2px; }
    .vk-status { color: #828282; font-size: 14px; margin-bottom: 15px; border-bottom: 1px solid #2D2D2E; padding-bottom: 10px; }
    
    /* Таблица инфо */
    .vk-info-table { width: 100%; font-size: 14px; border-collapse: collapse; }
    .vk-info-label { color: #828282; width: 160px; padding: 4px 0; }
    .vk-info-value { color: #71AAEB; padding: 4px 0; }

    /* Кнопки меню */
    .sidebar-link {
        padding: 8px 12px;
        color: #E1E3E6;
        text-decoration: none;
        display: block;
        border-radius: 6px;
        margin: 2px 0;
    }
    .sidebar-link:hover { background-color: #222224; }
    
    /* Кнопка "Редактировать" под фото */
    .stButton>button {
        background-color: #2D2D2E !important;
        color: #E1E3E6 !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
u_data = all_users.get(st.session_state.username, {})
info = u_data.get('info', {})

# --- ВЕРХНЯЯ ПАНЕЛЬ (Header) ---
header_col1, header_col2 = st.columns([2, 8])
with header_col1:
    st.markdown("<h3 style='color:white; margin:0;'>🌌 MilkyGram</h3>", unsafe_allow_html=True)

st.write("---")

# --- ОСНОВНОЙ ПАТТЕРН ВК (3 колонки) ---
col_nav, col_side, col_main = st.columns([1.5, 2.5, 6])

# 1. НАВИГАЦИЯ (Слева)
with col_nav:
    if st.button("🏠 Моя страница", key="nav_me"): st.session_state.page = "profile"; st.rerun()
    if st.button("📡 Новости", key="nav_news"): st.session_state.page = "feed"; st.rerun()
    if st.button("📟 Сообщения", key="nav_msg"): st.session_state.page = "dm"; st.rerun()
    if st.button("👥 Друзья", key="nav_fr"): st.session_state.page = "friends"; st.rerun()
    if st.button("⚙️ Настройки", key="nav_set"): st.session_state.page = "settings"; st.rerun()

# 2. ЛЕВАЯ КОЛОНКА (Фото и краткие списки)
with col_side:
    with st.container():
        st.markdown('<div class="vk-card">', unsafe_allow_html=True)
        # ФИКС: width='stretch' вместо None
        ava_url = u_data.get('avatar', DEFAULT_AVA)
        st.image(ava_url if (ava_url and len(ava_url)>5) else DEFAULT_AVA, width='stretch')
        st.write("")
        st.button("Редактировать профиль")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="vk-card">', unsafe_allow_html=True)
        st.markdown("<b style='color:#E1E3E6;'>Друзья</b> <span style='color:#828282;'>64</span>", unsafe_allow_html=True)
        # Здесь можно вывести сетку аватарок друзей 3х3
        st.markdown('</div>', unsafe_allow_html=True)

# 3. ЦЕНТРАЛЬНАЯ КОЛОНКА (Инфо и Стена)
with col_main:
    # Блок Профиля
    with st.container():
        st.markdown('<div class="vk-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="vk-name">{info.get("f_name", st.session_state.username)} {info.get("l_name", "")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="vk-status">{u_data.get("status", "установить статус")}</div>', unsafe_allow_html=True)
        
        # Данные анкеты
        rows = [
            ("День рождения:", info.get("bday", "не указан")),
            ("Город:", info.get("city", "не указан")),
            ("Семейное положение:", info.get("status_rel", "не указано")),
            ("Интересы:", info.get("interests", "не указаны"))
        ]
        
        html_table = "<table class='vk-info-table'>"
        for label, val in rows:
            html_table += f"<tr><td class='vk-info-label'>{label}</td><td class='vk-info-value'>{val}</td></tr>"
        html_table += "</table>"
        st.markdown(html_table, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Блок статистики (счетчики)
    with st.container():
        st.markdown('<div class="vk-card" style="padding: 10px 0;">', unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        s1.metric(label="друзей", value="142")
        s2.metric(label="подписчиков", value="85")
        s3.metric(label="фото", value="12")
        s4.metric(label="постов", value="4")
        st.markdown('</div>', unsafe_allow_html=True)

    # Стена
    st.markdown("<b style='color:#E1E3E6;'>Все записи</b>", unsafe_allow_html=True)
    
    # Создание поста
    with st.container():
        st.markdown('<div class="vk-card">', unsafe_allow_html=True)
        t_post = st.text_input("", placeholder="Что нового?", key="wall_input")
        if st.button("Опубликовать", key="wall_btn"):
            requests.post(f"{DB_URL}posts.json", json={
                "author": st.session_state.username,
                "text": t_post,
                "time": datetime.now().strftime("%H:%M"),
                "likes": 0
            })
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Вывод постов
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        if p.get('author') == st.session_state.username:
            with st.container():
                st.markdown('<div class="vk-card">', unsafe_allow_html=True)
                st.markdown(f"<b style='color:#71AAEB;'>{p['author']}</b> <span style='color:#828282; font-size:12px;'>сегодня в {p.get('time')}</span>", unsafe_allow_html=True)
                st.write(p.get('text', ''))
                st.markdown(f"<span style='color:#FF3347;'>❤ {p.get('likes', 0)}</span>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
