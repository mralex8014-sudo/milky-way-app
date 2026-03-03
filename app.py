import streamlit as st
import requests
from datetime import datetime

# 1. Настройка страницы
st.set_page_config(page_title="MilkyGram | Профиль", layout="wide")

# --- Инициализация ---
if 'username' not in st.session_state: st.session_state.username = "Pilot_Alpha"
DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ВК-СТИЛЬ (CSS) ---
st.markdown("""
<style>
    /* Главный фон */
    .stApp { background-color: #0A0A12; }
    
    /* Контейнеры как блоки ВК */
    .vk-block {
        background-color: #19191B;
        border: 1px solid #2D2D2E;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Имена и заголовки */
    .user-name { color: #E1E3E6; font-size: 20px; font-weight: 500; margin-bottom: 5px; }
    .user-status { color: #828282; font-size: 13px; margin-bottom: 15px; }
    
    /* Информация в профиле */
    .info-row { display: flex; margin-bottom: 8px; font-size: 13px; }
    .info-label { color: #828282; width: 150px; }
    .info-value { color: #71AAEB; }

    /* Кнопки */
    .stButton>button {
        background-color: #2D2D2E !important;
        color: #E1E3E6 !important;
        border: none !important;
        width: 100%;
        border-radius: 8px !important;
        font-size: 14px !important;
    }
    .stButton>button:hover { background-color: #3D3D3E !important; }
</style>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА ДАННЫХ ---
users = requests.get(f"{DB_URL}users.json").json() or {}
u_data = users.get(st.session_state.username, {})
info = u_data.get('info', {})

# --- СТРУКТУРА СТРАНИЦЫ (3 Колонки как в ВК) ---
# 1 колонка - Меню, 2 - Фото, 3 - Контент
col_menu, col_left, col_main = st.columns([1, 2.5, 6])

# 1. ЛЕВОЕ МЕНЮ
with col_menu:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("🏠 Моя страница")
    st.caption("📡 Новости")
    st.caption("📟 Сообщения")
    st.caption("👥 Друзья")
    st.caption("☁️ Туманности")

# 2. ЛЕВАЯ ПАНЕЛЬ (Аватар)
with col_left:
    with st.container():
        st.markdown('<div class="vk-block">', unsafe_allow_html=True)
        ava_url = u_data.get('avatar', DEFAULT_AVA)
        st.image(ava_url if len(ava_url)>5 else DEFAULT_AVA, width=None)
        if st.button("Редактировать"): pass
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Блок друзей (мини)
    with st.container():
        st.markdown('<div class="vk-block">', unsafe_allow_html=True)
        st.markdown("<b style='color:#E1E3E6;'>Друзья</b>", unsafe_allow_html=True)
        st.caption("64 спутника")
        st.markdown('</div>', unsafe_allow_html=True)

# 3. ОСНОВНАЯ ПАНЕЛЬ (Информация и Стена)
with col_main:
    # Блок Информации
    with st.container():
        st.markdown(f'<div class="vk-block">', unsafe_allow_html=True)
        st.markdown(f'<div class="user-name">{info.get("f_name", "Пилот")} {info.get("l_name", "")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-status">{u_data.get("status", "В бесконечность и далее...")}</div>', unsafe_allow_html=True)
        st.markdown("<hr style='border: 0.5px solid #2D2D2E;'>", unsafe_allow_html=True)
        
        # Строки анкеты
        details = [
            ("День рождения:", info.get("bday", "Не указан")),
            ("Город:", info.get("city", "Туманность Андромеды")),
            ("Семейное положение:", info.get("status_rel", "В поиске экипажа")),
            ("Место работы:", "Звездный флот"),
        ]
        for label, val in details:
            st.markdown(f'<div class="info-row"><div class="info-label">{label}</div><div class="info-value">{val}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Блок статистики
    with st.container():
        st.markdown('<div class="vk-block" style="display:flex; justify-content: space-around; text-align:center;">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown("<span style='color:#E1E3E6; font-size:16px;'>142</span><br><span style='color:#828282; font-size:12px;'>друзей</span>", unsafe_allow_html=True)
        c2.markdown("<span style='color:#E1E3E6; font-size:16px;'>85</span><br><span style='color:#828282; font-size:12px;'>подписчиков</span>", unsafe_allow_html=True)
        c3.markdown("<span style='color:#E1E3E6; font-size:16px;'>12</span><br><span style='color:#828282; font-size:12px;'>фотографий</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ПОЛЕ ЗАПИСИ (Стена)
    with st.container():
        st.markdown('<div class="vk-block">', unsafe_allow_html=True)
        t_wall = st.text_input("", placeholder="Что нового, исследователь?")
        if st.button("Опубликовать"):
            requests.post(f"{DB_URL}posts.json", json={
                "author": st.session_state.username,
                "text": t_wall,
                "time": datetime.now().strftime("%H:%M")
            })
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ПОСТЫ НА СТЕНЕ
    all_posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(all_posts.items())):
        if p.get('author') == st.session_state.username:
            with st.container():
                st.markdown('<div class="vk-block">', unsafe_allow_html=True)
                st.markdown(f"<b style='color:#71AAEB;'>{p['author']}</b> <span style='color:#828282; font-size:11px;'>{p.get('time')}</span>", unsafe_allow_html=True)
                st.write(p['text'])
                st.markdown('</div>', unsafe_allow_html=True)
