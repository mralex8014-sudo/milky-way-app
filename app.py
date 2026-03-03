import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Инициализация Вселенной
st.set_page_config(page_title="MilkyGram", page_icon="🌌", layout="wide")

# --- ГЛОБАЛЬНЫЕ КОНСТАНТЫ ---
DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ИНИЦИАЛИЗАЦИЯ SESSION STATE (Лечим KeyError) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'page' not in st.session_state: st.session_state.page = "feed"
if 'viewing_profile' not in st.session_state: st.session_state.viewing_profile = None
if 'theme' not in st.session_state: st.session_state.theme = "Dark"

# --- СТИЛИЗАЦИЯ (с защитой от AttributeError) ---
bg, txt, brd, inp = ("#050505", "#E0E0E0", "#1B1B3A", "#0F0F1B") if st.session_state.theme == "Dark" else ("#FFFFFF", "#000000", "#DBDBDB", "#FAFAFA")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {inp}; border-right: 1px solid {brd}; }}
    h1, h2, h3, h4, p, span, label {{ color: {txt} !important; }}
    .stButton>button {{ border-radius: 20px; background-color: #3D3D6B; color: white; border: none; width: 100%; }}
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {inp} !important; border: 1px solid {brd} !important; border-radius: 15px; padding: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ЛОГИКА ВХОДА ---
if not st.session_state.logged_in:
    st.title("👨‍🚀 MilkyGram: Вход в систему")
    u = st.text_input("Позывной")
    p = st.text_input("Код доступа", type="password")
    if st.button("Запуск"):
        res = requests.get(f"{DB_URL}users/{u}.json").json()
        if res and res.get('password') == hash_pass(p):
            st.session_state.logged_in, st.session_state.username = True, u
            st.rerun()
        else: st.error("Неверный позывной или код")
    st.stop()

# --- ПОЛУЧЕНИЕ ДАННЫХ (После входа!) ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})
my_satellites = my_data.get('satellites', [])
if not isinstance(my_satellites, list): my_satellites = []

# --- ФУНКЦИИ (После получения данных) ---
def send_signal(to_u, text):
    requests.post(f"{DB_URL}notifications/{to_u}.json", json={
        "from": st.session_state.username, "text": text,
        "time": datetime.now().strftime("%H:%M"), "read": False
    })

def show_user_profile(target_name):
    user = all_users.get(target_name)
    if not user: 
        st.error("Объект не найден в нашей галактике")
        return
    st.title(f"👨‍🚀 Звездная карта @{target_name}")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(user.get('avatar', DEFAULT_AVA), width=150)
    with col2:
        st.write(f"**Статус:** {user.get('bio', 'Исследователь космоса')}")
        
        is_friend = target_name in my_satellites
        if is_friend:
            if st.button("💥 Разорвать гравитационную связь"):
                my_satellites.remove(target_name)
                requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites})
                st.rerun()
        else:
            if st.button("🔗 Установить гравитационную связь"):
                my_satellites.append(target_name)
                requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites})
                send_signal(target_name, "теперь ваш Спутник!")
                st.rerun()
        
        if st.button("📟 Начать радиосеанс"):
            st.session_state.page = "dm"
            st.session_state.chat_with = target_name
            st.session_state.viewing_profile = None
            st.rerun()

# --- ЦУП (БОКОВОЕ МЕНЮ) ---
with st.sidebar:
    st.title("🛸 MilkyGram")
    st.write(f"Пилот: **@{st.session_state.username}**")
    
    # Смена темы
    theme_on = st.toggle("🌙 Темный режим", value=(st.session_state.theme == "Dark"))
    if theme_on != (st.session_state.theme == "Dark"):
        st.session_state.theme = "Dark" if theme_on else "Light"
        st.rerun()

    st.write("---")
    if st.button("📡 Горизонт событий"): 
        st.session_state.page, st.session_state.viewing_profile = "feed", None
        st.rerun()
    if st.button("🔍 Сектор поиска"): 
        st.session_state.page, st.session_state.viewing_profile = "search", None
        st.rerun()
    if st.button("📟 Радиоэфир"): 
        st.session_state.page, st.session_state.viewing_profile = "dm", None
        st.rerun()
    if st.button("🌌 Моя Галактика"): 
        st.session_state.page, st.session_state.viewing_profile = "galaxy", None
        st.rerun()
    if st.button("👨‍🚀 Мой отсек"): 
        st.session_state.page, st.session_state.viewing_profile = "my_profile", None
        st.rerun()
    
    st.write("---")
    if st.button("🚪 Выход"):
        st.session_state.logged_in = False
        st.rerun()

# --- ОСНОВНОЙ КОНТЕНТ ---
if st.session_state.viewing_profile:
    show_user_profile(st.session_state.viewing_profile)
    if st.button("⬅️ Назад в систему"): 
        st.session_state.viewing_profile = None
        st.rerun()

elif st.session_state.page == "feed":
    st.header("🛰️ Лента: Горизонт событий")
    with st.expander("➕ Создать пост"):
        img_url = st.text_input("URL снимка")
        text = st.text_area("Текст передачи")
        if st.button("Транслировать"):
            requests.post(f"{DB_URL}posts.json", json={
                "author": st.session_state.username, "img": img_url, "text": text, "time": datetime.now().strftime("%H:%M")
            })
            st.rerun()
    
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        with st.container(border=True):
            author = p.get('author', 'unknown')
            if st.button(f"👤 @{author}", key=f"feed_{pid}"):
                st.session_state.viewing_profile = author
                st.rerun()
            if p.get('img'): st.image(p['img'], use_container_width=True)
            st.write(p.get('text', ''))

elif st.session_state.page == "search":
    st.header("🔍 Поиск пилотов")
    q = st.text_input("Ввод позывного")
    if q:
        for name, data in all_users.items():
            if q.lower() in name.lower() and name != st.session_state.username:
                with st.container(border=True):
                    c1, c2 = st.columns([1, 5])
                    c1.image(data.get('avatar', DEFAULT_AVA), width=50)
                    if c2.button(f"Открыть карту @{name}", key=f"search_{name}"):
                        st.session_state.viewing_profile = name
                        st.rerun()

elif st.session_state.page == "galaxy":
    st.header("🌌 Моя Галактика")
    st.subheader("Ваши Спутники")
    if my_satellites:
        for sat in my_satellites:
            with st.container(border=True):
                col1, col2 = st.columns([1, 5])
                sat_data = all_users.get(sat, {})
                col1.image(sat_data.get('avatar', DEFAULT_AVA), width=50)
                if col2.button(f"Связаться с @{sat}", key=f"gal_{sat}"):
                    st.session_state.viewing_profile = sat
                    st.rerun()
    else: st.write("Вы пока одинокий странник. Найдите друзей в поиске!")

elif st.session_state.page == "my_profile":
    st.header("👨‍🚀 Личный отсек")
    new_ava = st.text_input("Ссылка на аватар", value=my_data.get('avatar', DEFAULT_AVA))
    new_bio = st.text_area("О себе", value=my_data.get('bio', ''))
    if st.button("Обновить данные"):
        requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"avatar": new_ava, "bio": new_bio})
        st.success("Данные обновлены!")
        st.rerun()

elif st.session_state.page == "dm":
    st.header("📟 Радиоэфир")
    target = st.session_state.get('chat_with')
    if not target:
        target = st.selectbox("Выберите частоту (пилота)", [u for u in all_users.keys() if u != st.session_state.username])
    
    st.write(f"Связь с: **@{target}**")
    chat_id = "".join(sorted([st.session_state.username, target]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    
    for m in msgs.values():
        st.write(f"**{m['from']}**: {m['text']}")
    
    msg_input = st.text_input("Введите сообщение")
    if st.button("Послать сигнал"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={"from": st.session_state.username, "text": msg_input})
        st.rerun()
