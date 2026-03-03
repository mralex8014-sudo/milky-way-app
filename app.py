import streamlit as st
import requests
from datetime import datetime

# 1. Настройка страницы
st.set_page_config(page_title="MilkyGram | Моя Страница", layout="wide")

# --- Инициализация состояния ---
for key, val in {
    'username': "Pilot_Alpha", 'page': "profile", 'logged_in': True, 'viewing_profile': None
}.items():
    if key not in st.session_state: st.session_state[key] = val

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ВК-СТИЛЬ 2026 (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #0A0A12; }
    .vk-card {
        background-color: #19191B;
        border: 1px solid #2D2D2E;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .vk-name { color: #E1E3E6; font-size: 22px; font-weight: 500; margin-bottom: 2px; }
    .vk-status { color: #828282; font-size: 14px; margin-bottom: 15px; border-bottom: 1px solid #2D2D2E; padding-bottom: 10px; }
    .vk-info-table { width: 100%; font-size: 14px; }
    .vk-info-label { color: #828282; width: 160px; padding: 4px 0; }
    .vk-info-value { color: #71AAEB; padding: 4px 0; }
    
    /* Убираем стандартные отступы Streamlit для кнопок в меню */
    div[data-testid="stVerticalBlock"] > div { border: none !important; }
</style>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
u_data = all_users.get(st.session_state.username, {})
info = u_data.get('info', {})

# --- ШАПКА ---
header_left, header_right = st.columns([2, 8])
header_left.markdown("<h3 style='color:white; margin:0;'>🌌 MilkyGram</h3>", unsafe_allow_html=True)
st.divider()

# --- ОСНОВНАЯ СЕТКА (3 КОЛОНКИ) ---
col_nav, col_side, col_main = st.columns([1.5, 2.5, 6])

# 1. ЛЕВОЕ МЕНЮ
with col_nav:
    menu_items = [
        ("🏠 Моя страница", "profile"),
        ("📡 Новости", "feed"),
        ("📟 Сообщения", "dm"),
        ("👥 Друзья", "friends"),
        ("⚙️ Настройки", "settings")
    ]
    for label, page in menu_items:
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page
            st.rerun()

# 2. БЛОК АВАТАРА (Слева)
with col_side:
    with st.container():
        st.markdown('<div class="vk-card">', unsafe_allow_html=True)
        ava_url = u_data.get('avatar', DEFAULT_AVA)
        # width='stretch' гарантирует заполнение контейнера
        st.image(ava_url if (ava_url and len(ava_url)>5) else DEFAULT_AVA, use_container_width=True)
        st.write("")
        st.button("Редактировать", key="edit_profile_btn")
        st.markdown('</div>', unsafe_allow_html=True)

# 3. ЦЕНТРАЛЬНЫЙ БЛОК (Инфо + Стена)
with col_main:
    # Инфо-карточка
    with st.container():
        st.markdown('<div class="vk-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="vk-name">{info.get("f_name", st.session_state.username)} {info.get("l_name", "")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="vk-status">{u_data.get("status", "установить статус")}</div>', unsafe_allow_html=True)
        
        rows = [
            ("День рождения:", info.get("bday", "не указан")),
            ("Город:", info.get("city", "Земля")),
            ("Семейное положение:", info.get("status_rel", "не указано")),
            ("Интересы:", info.get("interests", "не указаны"))
        ]
        
        for label, val in rows:
            st.markdown(f"""
            <div style="display: flex; font-size: 14px; padding: 3px 0;">
                <div style="color: #828282; width: 160px;">{label}</div>
                <div style="color: #71AAEB;">{val}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Статистика
    st.markdown('<div class="vk-card" style="padding: 5px 0;">', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("друзей", "142")
    s2.metric("подписчиков", "85")
    s3.metric("фото", "12")
    s4.metric("постов", "4")
    st.markdown('</div>', unsafe_allow_html=True)

    # СТЕНА
    st.markdown("<b style='color:#E1E3E6;'>Все записи</b>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="vk-card">', unsafe_allow_html=True)
        # ИСПРАВЛЕНИЕ: Добавлен label и label_visibility для чистоты логов
        t_post = st.text_input(
            label="Поле для создания поста", 
            placeholder="Что нового?", 
            key="wall_input", 
            label_visibility="collapsed"
        )
        if st.button("Опубликовать", key="wall_btn"):
            if t_post:
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
                st.markdown(f"<b style='color:#71AAEB;'>{p['author']}</b> <span style='color:#828282; font-size: 12px;'>в {p.get('time')}</span>", unsafe_allow_html=True)
                st.write(p.get('text', ''))
                st.markdown(f"<span style='color:#FF3347;'>❤ {p.get('likes', 0)}</span>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
