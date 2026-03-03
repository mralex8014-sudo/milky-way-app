import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Инициализация Вселенной
st.set_page_config(page_title="MilkyGram", page_icon="🌌", layout="wide")

# Глобальные константы
DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# Стилизация
st.markdown(f"""
    <style>
    .stApp {{ background-color: #050505; color: #E0E0E0; }}
    [data-testid="stSidebar"] {{ background-color: #0A0A12; border-right: 1px solid #1B1B3A; }}
    .stButton>button {{ border-radius: 20px; background-color: #3D3D6B; color: white; border: none; }}
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: #0A0A12 !important; border: 1px solid #1B1B3A !important; border-radius: 15px; padding: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ФУНКЦИИ СВЯЗИ ---
def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

def send_signal(to_u, text):
    requests.post(f"{DB_URL}notifications/{to_u}.json", json={
        "from": st.session_state.username, "text": text,
        "time": datetime.now().strftime("%H:%M"), "read": False
    })

# --- ЛОГИКА ВХОДА ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'viewing_profile' not in st.session_state: st.session_state.viewing_profile = None

if not st.session_state.logged_in:
    st.title("👨‍🚀 MilkyGram: Вход в систему")
    u = st.text_input("Позывной")
    p = st.text_input("Код доступа", type="password")
    if st.button("Запуск"):
        res = requests.get(f"{DB_URL}users/{u}.json").json()
        if res and res.get('password') == hash_pass(p):
            st.session_state.logged_in, st.session_state.username = True, u
            st.rerun()
    st.stop()

# --- ЦУП (БОКОВОЕ МЕНЮ) ---
with st.sidebar:
    st.title("🛸 MilkyGram")
    st.write(f"Пилот: **@{st.session_state.username}**")
    st.write("---")
    if st.button("📡 Горизонт событий"): st.session_state.page, st.session_state.viewing_profile = "feed", None
    if st.button("🔍 Поиск"): st.session_state.page, st.session_state.viewing_profile = "search", None
    if st.button("📟 Радиоэфир"): st.session_state.page, st.session_state.viewing_profile = "dm", None
    if st.button("🌌 Моя Галактика"): st.session_state.page, st.session_state.viewing_profile = "galaxy", None
    if st.button("👨‍🚀 Мой отсек"): st.session_state.page, st.session_state.viewing_profile = "my_profile", None
    
    if st.button("🚪 Выйти"):
        st.session_state.logged_in = False
        st.rerun()

# --- ЗАГРУЗКА ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})
my_satellites = my_data.get('satellites', [])

# --- ЛОГИКА СТРАНИЦ ---

# Функция для отрисовки карточки профиля (чужого)
def show_user_profile(target_name):
    user = all_users.get(target_name)
    if not user: return
    st.title(f"👨‍🚀 Звездная карта @{target_name}")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(user.get('avatar', DEFAULT_AVA), width=150)
    with col2:
        st.write(f"**Статус:** {user.get('bio')}")
        
        is_friend = target_name in my_satellites
        if is_friend:
            if st.button("💥 Разорвать связь"):
                my_satellites.remove(target_name)
                requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites})
                st.rerun()
        else:
            if st.button("🔗 Установить связь"):
                if not isinstance(my_satellites, list): my_satellites = []
                my_satellites.append(target_name)
                requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites})
                send_signal(target_name, "установил с вами гравитационную связь!")
                st.rerun()
        
        if st.button("📟 Отправить сигнал (Чат)"):
            st.session_state.page = "dm"
            st.session_state.chat_with = target_name
            st.rerun()

if st.session_state.viewing_profile:
    show_user_profile(st.session_state.viewing_profile)
    if st.button("⬅️ Вернуться"): 
        st.session_state.viewing_profile = None
        st.rerun()

# --- 1. ЛЕНТА ---
elif st.session_state.page == "feed":
    st.title("🛰️ Горизонт событий")
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        with st.container(border=True):
            author = p.get('author')
            if st.button(f"👤 @{author}", key=f"btn_{pid}"):
                st.session_state.viewing_profile = author
                st.rerun()
            if p.get('img'): st.image(p['img'], use_container_width=True)
            st.write(p.get('text'))

# --- 2. МОЯ ГАЛАКТИКА (ДРУЗЬЯ) ---
elif st.session_state.page == "galaxy":
    st.title("🌌 Моя Галактика")
    st.subheader("Твои Спутники (Подписки)")
    if my_satellites:
        for sat in my_satellites:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 2])
                sat_info = all_users.get(sat, {})
                c1.image(sat_info.get('avatar', DEFAULT_AVA), width=50)
                c2.write(f"**@{sat}**")
                if c3.button("Открыть карту", key=f"view_{sat}"):
                    st.session_state.viewing_profile = sat
                    st.rerun()
    else:
        st.write("Твоя орбита пока пуста. Найди спутников в поиске!")

# --- 3. РАДИОЭФИР (ЧАТ) ---
elif st.session_state.page == "dm":
    st.title("📟 Радиоэфир")
    target = st.session_state.get('chat_with') or st.selectbox("Частота", [u for u in all_users.keys() if u != st.session_state.username])
    
    chat_id = "".join(sorted([st.session_state.username, target]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    
    for m in msgs.values():
        st.write(f"**{m['from']}**: {m['text']}")

    new_msg = st.text_input("Текст сигнала...")
    if st.button("Послать"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={"from": st.session_state.username, "text": new_msg})
        st.rerun()

# --- 4. ПОИСК ---
elif st.session_state.page == "search":
    st.title("🔍 Сканирование секторов")
    q = st.text_input("Введите позывной")
    for name in all_users:
        if q.lower() in name.lower() and name != st.session_state.username:
            if st.button(f"📡 Пилот @{name}", key=f"srch_{name}"):
                st.session_state.viewing_profile = name
                st.rerun()
