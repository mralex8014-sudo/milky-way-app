import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Инициализация Вселенной
st.set_page_config(page_title="MilkyGram", page_icon="🌌", layout="wide")

# --- ГЛОБАЛЬНЫЕ КОНСТАНТЫ ---
DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ИНИЦИАЛИЗАЦИЯ SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'page' not in st.session_state: st.session_state.page = "feed"
if 'viewing_profile' not in st.session_state: st.session_state.viewing_profile = None
if 'theme' not in st.session_state: st.session_state.theme = "Dark"

# --- СТИЛИЗАЦИЯ ---
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
    .comment-box {{ background: {bg}; padding: 10px; border-radius: 10px; margin-top: 5px; border-left: 3px solid #3D3D6B; }}
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
    st.stop()

# --- ПОЛУЧЕНИЕ ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})
my_satellites = my_data.get('satellites', [])
if not isinstance(my_satellites, list): my_satellites = []

# --- ФУНКЦИИ ---
def send_signal(to_u, text):
    requests.post(f"{DB_URL}notifications/{to_u}.json", json={
        "from": st.session_state.username, "text": text,
        "time": datetime.now().strftime("%H:%M"), "read": False
    })

def show_user_profile(target_name):
    user = all_users.get(target_name)
    if not user: return
    st.title(f"👨‍🚀 Звездная карта @{target_name}")
    col1, col2 = st.columns([1, 3])
    with col1: st.image(user.get('avatar', DEFAULT_AVA), width=150)
    with col2:
        st.write(f"**Статус:** {user.get('bio', 'Исследователь')}")
        if target_name != st.session_state.username:
            if target_name in my_satellites:
                if st.button("💥 Разорвать связь"):
                    my_satellites.remove(target_name); requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites}); st.rerun()
            else:
                if st.button("🔗 Установить связь"):
                    my_satellites.append(target_name); requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites}); st.rerun()
            if st.button("📟 Радиосеанс"): st.session_state.page = "dm"; st.session_state.chat_with = target_name; st.session_state.viewing_profile = None; st.rerun()

# --- ЦУП (МЕНЮ) ---
with st.sidebar:
    st.title("🛸 MilkyGram")
    st.write(f"Пилот: **@{st.session_state.username}**")
    theme_on = st.toggle("🌙 Темный режим", value=(st.session_state.theme == "Dark"))
    if theme_on != (st.session_state.theme == "Dark"):
        st.session_state.theme = "Dark" if theme_on else "Light"; st.rerun()
    st.write("---")
    if st.button("📡 Лента"): st.session_state.page, st.session_state.viewing_profile = "feed", None; st.rerun()
    if st.button("🔍 Поиск"): st.session_state.page, st.session_state.viewing_profile = "search", None; st.rerun()
    if st.button("📟 Радиоэфир"): st.session_state.page, st.session_state.viewing_profile = "dm", None; st.rerun()
    if st.button("🌌 Галактика"): st.session_state.page, st.session_state.viewing_profile = "galaxy", None; st.rerun()
    if st.button("👨‍🚀 Мой отсек"): st.session_state.page, st.session_state.viewing_profile = "my_profile", None; st.rerun()
    if st.button("🚪 Выйти"): st.session_state.logged_in = False; st.rerun()

# --- КОНТЕНТ ---
if st.session_state.viewing_profile:
    show_user_profile(st.session_state.viewing_profile)
    if st.button("⬅️ Назад"): st.session_state.viewing_profile = None; st.rerun()

elif st.session_state.page == "feed":
    st.header("🛰️ Горизонт событий")
    with st.expander("➕ Создать пост"):
        img_url = st.text_input("URL снимка")
        text = st.text_area("Текст передачи")
        if st.button("Транслировать"):
            requests.post(f"{DB_URL}posts.json", json={
                "author": st.session_state.username, "img": img_url, "text": text, "time": datetime.now().strftime("%d.%m %H:%M"), "likes": 0
            })
            st.rerun()
    
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        with st.container(border=True):
            col_h1, col_h2 = st.columns([4, 1])
            if col_h1.button(f"👤 @{p.get('author')}", key=f"feed_u_{pid}"):
                st.session_state.viewing_profile = p.get('author'); st.rerun()
            col_h2.caption(f"🕒 {p.get('time')}")
            
            if p.get('img'): st.image(p['img'], use_container_width=True)
            st.write(p.get('text', ''))
            
            # Лайки и Комменты
            c1, c2 = st.columns([1, 4])
            likes = p.get('likes', 0)
            if c1.button(f"✨ {likes}", key=f"like_{pid}"):
                requests.patch(f"{DB_URL}posts/{pid}.json", json={"likes": likes + 1}); st.rerun()
            
            with st.expander("💬 Обсуждение"):
                coms = p.get('comments', {})
                for cid, c in coms.items():
                    st.markdown(f"<div class='comment-box'><b>@{c['user']}</b>: {c['txt']}</div>", unsafe_allow_html=True)
                new_com = st.text_input("Ваш сигнал...", key=f"in_{pid}")
                if st.button("Отправить", key=f"send_{pid}"):
                    requests.post(f"{DB_URL}posts/{pid}/comments.json", json={"user": st.session_state.username, "txt": new_com})
                    st.rerun()

elif st.session_state.page == "dm":
    st.header("📟 Радиоэфир")
    target = st.session_state.get('chat_with') or st.selectbox("Частота", [u for u in all_users.keys() if u != st.session_state.username])
    
    chat_id = "".join(sorted([st.session_state.username, target]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    
    for m in msgs.values():
        align = "right" if m['from'] == st.session_state.username else "left"
        st.markdown(f"<div style='text-align: {align};'><b>{m['from']}</b> <small>{m.get('time', '')}</small><br>{m['text']}</div>", unsafe_allow_html=True)
    
    msg_in = st.text_input("Введите сообщение")
    if st.button("Послать"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={
            "from": st.session_state.username, "text": msg_in, "time": datetime.now().strftime("%H:%M")
        }); st.rerun()

elif st.session_state.page == "search":
    st.header("🔍 Поиск")
    q = st.text_input("Никнейм...")
    for name, data in all_users.items():
        if q.lower() in name.lower() and name != st.session_state.username:
            if st.button(f"👤 @{name}", key=f"s_{name}"):
                st.session_state.viewing_profile = name; st.rerun()

elif st.session_state.page == "galaxy":
    st.header("🌌 Моя Галактика")
    for sat in my_satellites:
        if st.button(f"🛰️ @{sat}", key=f"gal_{sat}"):
            st.session_state.viewing_profile = sat; st.rerun()

elif st.session_state.page == "my_profile":
    st.header("👨‍🚀 Мой отсек")
    new_a = st.text_input("Аватар URL", value=my_data.get('avatar', DEFAULT_AVA))
    new_b = st.text_area("Био", value=my_data.get('bio', ''))
    if st.button("Сохранить"):
        requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"avatar": new_a, "bio": new_b}); st.rerun()
