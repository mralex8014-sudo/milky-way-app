import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка Вселенной
st.set_page_config(page_title="MilkyGram", page_icon="🌌", layout="wide")

# Базовые настройки стиля
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    [data-testid="stSidebar"] { background-color: #0A0A12; border-right: 1px solid #1B1B3A; }
    .stButton>button { border-radius: 20px; background-color: #3D3D6B; color: white; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #5D5D9D; transform: scale(1.02); }
    .stTextInput>div>div>input { background-color: #0F0F1B !important; color: white !important; border: 1px solid #1B1B3A !important; }
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
        background-color: #0A0A12 !important; border: 1px solid #1B1B3A !important; border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

def send_signal(to_u, text, type="info"):
    requests.post(f"{DB_URL}notifications/{to_u}.json", json={
        "from": st.session_state.username,
        "text": text,
        "time": datetime.now().strftime("%H:%M"),
        "read": False,
        "type": type
    })

# --- СИСТЕМА ИДЕНТИФИКАЦИИ (ВХОД / РЕГИСТРАЦИЯ) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("👨‍🚀 Добро пожаловать в MilkyGram")
    tab1, tab2 = st.tabs(["🚀 Вход в систему", "🪐 Регистрация нового пилота"])
    
    with tab1:
        u = st.text_input("Позывной (Никнейм)", key="l_u")
        p = st.text_input("Код доступа", type="password", key="l_p")
        if st.button("Начать запуск"):
            res = requests.get(f"{DB_URL}users/{u}.json").json()
            if res and res.get('password') == hash_pass(p):
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
            else: st.error("Ошибка доступа: данные не найдены в базе")

    with tab2:
        u_new = st.text_input("Уникальный позывной", key="r_u")
        p_new = st.text_input("Придумайте код доступа", type="password", key="r_p")
        if st.button("Зарегистрировать позывной"):
            # Проверка уникальности
            check = requests.get(f"{DB_URL}users/{u_new}.json").json()
            if check:
                st.error("Этот позывной уже занят другим пилотом!")
            elif u_new and p_new:
                requests.put(f"{DB_URL}users/{u_new}.json", json={
                    "password": hash_pass(p_new),
                    "avatar": "https://cdn-icons-png.flaticon.com/512/2592/2592188.png",
                    "bio": "На орбите MilkyGram",
                    "satellites": [] # Список друзей (Спутников)
                })
                st.success("Позывной успешно зарегистрирован! Перейдите на вкладку Вход.")
    st.stop()

# --- ЦУП (БОКОВОЕ МЕНЮ) ---
with st.sidebar:
    st.header("🛸 Центр Управления")
    st.write(f"Пилот: **@{st.session_state.username}**")
    st.write("---")
    
    if st.button("📡 Горизонт событий (Лента)"): st.session_state.page = "feed"
    if st.button("🔍 Поиск Спутников"): st.session_state.page = "search"
    if st.button("📟 Радиоэфир (Директ)"): st.session_state.page = "dm"
    
    # Уведомления
    notifs = requests.get(f"{DB_URL}notifications/{st.session_state.username}.json").json() or {}
    unread = len([n for n in notifs.values() if isinstance(n, dict) and not n.get('read')])
    if st.button(f"🔔 Сигналы ({unread})" if unread > 0 else "🔔 Сигналы"): st.session_state.page = "notifs"
    
    if st.button("👨‍🚀 Личный отсек (Профиль)"): st.session_state.page = "profile"
    
    st.write("---")
    if st.button("☄️ Выйти из системы"):
        st.session_state.logged_in = False
        st.rerun()

# --- ГЛОБАЛЬНЫЕ ДАННЫЕ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
if 'page' not in st.session_state: st.session_state.page = "feed"

# --- 1. ГОРИЗОНТ СОБЫТИЙ (ЛЕНТА) ---
if st.session_state.page == "feed":
    st.title("🛰️ Горизонт событий")
    with st.expander("📝 Передать данные в эфир"):
        img = st.text_input("Ссылка на визуальный файл (URL)")
        txt = st.text_area("Текстовое сообщение")
        if st.button("Транслировать"):
            requests.post(f"{DB_URL}posts.json", json={
                "author": st.session_state.username, "img": img, "text": txt, "time": datetime.now().strftime("%d.%m %H:%M")
            })
            st.rerun()

    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for p in reversed(list(posts.values())):
        with st.container(border=True):
            st.write(f"📡 **@{p.get('author')}**")
            if p.get('img'): st.image(p['img'], use_container_width=True)
            st.write(p.get('text'))
            st.caption(f"Время приема: {p.get('time')}")

# --- 2. ПОИСК СПУТНИКОВ ---
elif st.session_state.page == "search":
    st.title("🔍 Сканирование секторов")
    q = st.text_input("Введите позывной для поиска")
    for name, data in all_users.items():
        if q.lower() in name.lower() and name != st.session_state.username:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 2])
                c1.image(data.get('avatar'), width=60)
                c2.write(f"**@{name}**")
                c2.caption(data.get('bio'))
                if c3.button("Притянуть (В Спутники)", key=f"add_{name}"):
                    send_signal(name, "хочет установить гравитационную связь! 🤝", "friend")
                    st.success(f"Запрос отправлен @{name}")

# --- 3. РАДИОЭФИР (ДИРЕКТ) ---
elif st.session_state.page == "dm":
    st.title("📟 Радиоэфир")
    target = st.selectbox("Выбрать частоту (Собеседник)", [u for u in all_users.keys() if u != st.session_state.username])
    
    # Чат
    chat_id = "".join(sorted([st.session_state.username, target]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    
    with st.container(border=True):
        for m in msgs.values():
            align = "right" if m['from'] == st.session_state.username else "left"
            st.markdown(f"<div style='text-align: {align}; color: #A0A0FF;'><b>{m['from']}:</b> {m['text']}</div>", unsafe_allow_html=True)

    new_msg = st.text_input("Введите сообщение...")
    if st.button("Отправить сигнал"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={
            "from": st.session_state.username, "text": new_msg, "time": datetime.now().strftime("%H:%M")
        })
        send_signal(target, f"отправил вам сообщение в радиоэфире", "msg")
        st.rerun()

# --- 4. СИГНАЛЫ (УВЕДОМЛЕНИЯ) ---
elif st.session_state.page == "notifs":
    st.title("🔔 Входящие сигналы")
    if notifs:
        for nid, n in reversed(list(notifs.items())):
            with st.container(border=True):
                st.write(f"🚀 **{n.get('from')}** {n.get('text')}")
                if st.button("Принято", key=nid):
                    requests.patch(f"{DB_URL}notifications/{st.session_state.username}/{nid}.json", json={"read": True})
                    st.rerun()
    else: st.write("Космос молчит...")
