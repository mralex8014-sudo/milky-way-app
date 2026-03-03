import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Конфигурация страницы
st.set_page_config(page_title="MilkyGram", page_icon="📸", layout="centered")

# --- КАСТОМНЫЙ CSS (DARK STYLE) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    [data-testid="stHeader"] { background-color: #000000; border-bottom: 1px solid #262626; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #FFFFFF !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #121212 !important; color: #FFFFFF !important; border: 1px solid #363636 !important;
    }
    .stButton>button {
        background-color: #0095f6 !important; color: white !important; border-radius: 8px !important; border: none !important; width: 100%;
    }
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
        background-color: #000000 !important; border: 1px solid #262626 !important; border-radius: 10px; padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Ссылки на Firebase
DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
URL_POSTS = f"{DB_URL}posts.json"
URL_USERS = f"{DB_URL}users.json"
URL_MESSAGES = f"{DB_URL}messages.json"
URL_NOTIFS = f"{DB_URL}notifications.json"

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_notification(to_user, text, type="info"):
    """Функция для создания уведомления в базе"""
    notif_data = {
        "from": st.session_state.username,
        "text": text,
        "type": type,
        "time": datetime.now().strftime("%H:%M"),
        "read": False
    }
    requests.post(f"{DB_URL}notifications/{to_user}.json", json=notif_data)

# --- СИСТЕМА ВХОДА ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

col_head, col_log = st.columns([2, 1])
with col_head: st.header("📸 MilkyGram")

with col_log:
    if not st.session_state.logged_in:
        with st.expander("🔑 Вход"):
            mode = st.radio("Действие", ["Вход", "Регистрация"], label_visibility="collapsed")
            u_in = st.text_input("Никнейм")
            p_in = st.text_input("Пароль", type="password")
            if st.button("ОК"):
                user_url = f"{DB_URL}users/{u_in}.json"
                if mode == "Регистрация":
                    requests.put(user_url, json={"password": hash_pass(p_in), "avatar": "https://cdn-icons-png.flaticon.com/512/149/149071.png", "bio": "Сталкер звезд"})
                    st.success("Успех!")
                else:
                    data = requests.get(user_url).json()
                    if data and data['password'] == hash_pass(p_in):
                        st.session_state.logged_in, st.session_state.username = True, u_in
                        st.rerun()
    else:
        st.write(f"@{st.session_state.username}")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

if not st.session_state.logged_in: st.stop()

# --- ПОЛУЧЕНИЕ УВЕДОМЛЕНИЙ ДЛЯ СЧЕТЧИКА ---
my_notifs = requests.get(f"{DB_URL}notifications/{st.session_state.username}.json").json() or {}
unread_count = len([n for n in my_notifs.values() if not n.get('read')])
notif_label = f"🔔 Уведомления ({unread_count})" if unread_count > 0 else "🔔 Уведомления"

# --- НАВИГАЦИЯ ---
st.write("---")
page = st.selectbox("Меню", ["🌎 Лента", "🔍 Поиск", "✉️ Директ", notif_label, "👤 Профиль"], label_visibility="collapsed")
st.write("---")

all_users = requests.get(URL_USERS).json() or {}

# --- РАЗДЕЛ: УВЕДОМЛЕНИЯ ---
if "Уведомления" in page:
    st.subheader("Ваши уведомления")
    if my_notifs:
        for n_id, n in reversed(list(my_notifs.items())):
            with st.container(border=True):
                col_n1, col_n2 = st.columns([4, 1])
                status = "🔵" if not n.get('read') else ""
                col_n1.write(f"{status} **{n['from']}**: {n['text']}")
                col_n1.caption(f"🕒 {n['time']}")
                if not n.get('read'):
                    if col_n2.button("Ок", key=f"read_{n_id}"):
                        requests.patch(f"{DB_URL}notifications/{st.session_state.username}/{n_id}.json", json={"read": True})
                        st.rerun()
        if st.button("Очистить всё"):
            requests.delete(f"{DB_URL}notifications/{st.session_state.username}.json")
            st.rerun()
    else:
        st.write("Пока новостей нет.")

# --- РАЗДЕЛ: ПОИСК (с запросом в друзья) ---
elif page == "🔍 Поиск":
    q = st.text_input("Найти кого-нибудь...")
    if q:
        filtered = {n: d for n, d in all_users.items() if q.lower() in n.lower()}
        for n, d in filtered.items():
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 2])
                c1.image(d.get('avatar'), width=50)
                c2.write(f"**{n}**")
                if c3.button("В друзья", key=f"f_{n}"):
                    add_notification(n, "хочет добавить вас в друзья! 🤝", "friend_request")
                    st.success("Запрос отправлен!")

# --- РАЗДЕЛ: ДИРЕКТ (с уведомлением о сообщении) ---
elif page == "✉️ Директ":
    target = st.selectbox("Собеседник", [u for u in all_users.keys() if u != st.session_state.username])
    m_txt = st.text_input("Сообщение...")
    if st.button("Отправить"):
        requests.post(URL_MESSAGES, json={"from": st.session_state.username, "to": target, "text": m_txt, "time": datetime.now().strftime("%H:%M")})
        add_notification(target, f"прислал вам новое сообщение: '{m_txt[:20]}...'", "message")
        st.rerun()
    
    # Отображение переписки (упрощенно)
    msgs = requests.get(URL_MESSAGES).json() or {}
    for m in reversed(list(msgs.values())):
        if (m['from'] == st.session_state.username and m['to'] == target) or (m['to'] == st.session_state.username and m['from'] == target):
            st.write(f"**{m['from']}**: {m['text']}")

# --- ОСТАЛЬНЫЕ РАЗДЕЛЫ (Лента и Профиль остаются прежними) ---
elif page == "🌎 Лента":
    st.write("Тут лента постов...") # (Добавь сюда код из прошлой версии)
elif page == "👤 Профиль":
    st.write("Тут настройки профиля...") # (Добавь сюда код из прошлой версии)
