import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Системные настройки
st.set_page_config(page_title="MilkyGram Pro", page_icon="🌌", layout="wide")

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- Инициализация состояний (чтобы кнопки работали) ---
if 'page' not in st.session_state: st.session_state.page = "profile"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'viewing_profile' not in st.session_state: st.session_state.viewing_profile = None

# --- Стилизация (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #0A0A12; color: #E1E3E6; }
    .vk-card { background-color: #19191B; border: 1px solid #2D2D2E; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
    .vk-name { font-size: 20px; font-weight: 500; color: #FFFFFF; }
    .vk-status { color: #828282; font-size: 13px; padding-bottom: 10px; border-bottom: 1px solid #2D2D2E; }
    [data-testid="stMetricValue"] { color: #71AAEB !important; font-size: 18px !important; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #2D2D2E; color: white; border: none; }
    .stButton>button:hover { background-color: #3D3D3E; border: 1px solid #71AAEB; }
</style>
""", unsafe_allow_html=True)

# --- Вспомогательные функции ---
def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

def get_user_data(user):
    res = requests.get(f"{DB_URL}users/{user}.json").json()
    return res if res else {}

# --- ЛОГИКА АВТОРИЗАЦИИ ---
if not st.session_state.logged_in:
    st.title("🌌 MilkyGram: Вход в систему")
    col1, _ = st.columns([1, 2])
    with col1:
        with st.container(border=True):
            u = st.text_input("Позывной")
            p = st.text_input("Пароль", type="password")
            if st.button("Войти"):
                data = get_user_data(u)
                if data and data.get('password') == hash_pass(p):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
                else: st.error("Ошибка доступа")
    st.stop()

# --- ОСНОВНОЙ КОНТЕНТ ПОСЛЕ ВХОДА ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})

# Шапка сайта
h_left, h_right = st.columns([2, 8])
h_left.markdown("### 🌌 MilkyGram")
h_right.write(f"Вы вошли как: **@{st.session_state.username}**")
st.divider()

# Основная сетка: Навигация | Левая панель | Контент
col_nav, col_side, col_main = st.columns([1.5, 2.5, 6])

# --- 1. КНОПКИ НАВИГАЦИИ (Теперь работают!) ---
with col_nav:
    if st.button("🏠 Моя страница"): 
        st.session_state.page = "profile"
        st.session_state.viewing_profile = None
        st.rerun()
    if st.button("📡 Лента новостей"): 
        st.session_state.page = "feed"
        st.rerun()
    if st.button("📟 Сообщения"): 
        st.session_state.page = "messages"
        st.rerun()
    if st.button("📝 Редактировать"): 
        st.session_state.page = "settings"
        st.rerun()
    st.write("---")
    if st.button("🚪 Выйти"): 
        st.session_state.logged_in = False
        st.rerun()

# --- 2. ЛЕВАЯ ПАНЕЛЬ (Аватар) ---
target = st.session_state.viewing_profile or st.session_state.username
u_prof = all_users.get(target, {})

with col_side:
    st.markdown('<div class="vk-card">', unsafe_allow_html=True)
    ava = u_prof.get('avatar', DEFAULT_AVA)
    st.image(ava if len(str(ava)) > 5 else DEFAULT_AVA, use_container_width=True)
    if target != st.session_state.username:
        if st.button("✉️ Написать"):
            st.session_state.page = "messages"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. ЦЕНТРАЛЬНЫЙ БЛОК (Логика страниц) ---
with col_main:
    
    # --- СТРАНИЦА ПРОФИЛЯ ---
    if st.session_state.page == "profile":
        info = u_prof.get('info', {})
        st.markdown('<div class="vk-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="vk-name">{info.get("f_name", target)} {info.get("l_name", "")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="vk-status">{u_prof.get("status", "Исследователь космоса")}</div>', unsafe_allow_html=True)
        
        # Инфо-таблица
        details = {
            "Город": info.get("city", "Не указан"),
            "ДР": info.get("bday", "Не указан"),
            "Интересы": info.get("interests", "Пустота...")
        }
        for k, v in details.items():
            st.markdown(f"**{k}:** <span style='color:#71AAEB;'>{v}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Стена
        st.subheader("📝 Стена")
        with st.container(border=True):
            t_post = st.text_input("Что нового?", key="post_in", label_visibility="collapsed")
            if st.button("Опубликовать"):
                requests.post(f"{DB_URL}posts.json", json={
                    "author": target, "creator": st.session_state.username, 
                    "text": t_post, "time": datetime.now().strftime("%H:%M")
                })
                st.rerun()
        
        # Вывод постов
        posts = requests.get(f"{DB_URL}posts.json").json() or {}
        for pid, p in reversed(list(posts.items())):
            if p.get('author') == target:
                with st.container(border=True):
                    st.markdown(f"**{p.get('creator')}** <small>{p.get('time')}</small>", unsafe_allow_html=True)
                    st.write(p.get('text'))

    # --- СТРАНИЦА НОВОСТЕЙ ---
    elif st.session_state.page == "feed":
        st.subheader("📡 Последние сигналы из космоса")
        posts = requests.get(f"{DB_URL}posts.json").json() or {}
        for pid, p in reversed(list(posts.items())):
            with st.container(border=True):
                st.write(f"👤 **@{p.get('author')}**")
                st.write(p.get('text'))

    # --- СТРАНИЦА НАСТРОЕК ---
    elif st.session_state.page == "settings":
        st.subheader("⚙️ Редактирование Личного Дела")
        i = my_data.get('info', {})
        new_fn = st.text_input("Имя", i.get('f_name', ''))
        new_city = st.text_input("Город", i.get('city', ''))
        new_stat = st.text_input("Статус", my_data.get('status', ''))
        new_ava = st.text_input("URL аватара", my_data.get('avatar', ''))
        
        if st.button("Сохранить изменения"):
            requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={
                "info": {"f_name": new_fn, "city": new_city},
                "status": new_stat, "avatar": new_ava
            })
            st.success("Данные синхронизированы!")
            st.rerun()
