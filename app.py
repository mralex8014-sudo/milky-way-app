import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка Вселенной
st.set_page_config(page_title="MilkyGram Pro", page_icon="🌌", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ ---
defaults = {
    'logged_in': False, 'username': "", 'page': "feed", 
    'viewing_profile': None, 'theme': "Dark", 'viewing_nebula': None,
    'search_query': ""
}
for key, val in defaults.items():
    if key not in st.session_state: st.session_state[key] = val

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ДИЗАЙН ---
if st.session_state.theme == "Dark":
    bg, txt, brd, inp, accent = "#0A0A0C", "#E0E0E0", "#22222E", "#11111B", "#3D3D6B"
else:
    bg, txt, brd, inp, accent = "#EDEEF0", "#222222", "#DCE1E6", "#FFFFFF", "#4A76A8"

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-size: 13px !important; color: {txt}; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {bg}; border-right: 1px solid {brd}; }}
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {inp} !important; border: 1px solid {brd} !important; 
        border-radius: 8px; padding: 12px !important;
    }}
    .stButton>button {{ border-radius: 6px; background-color: {accent}; color: white !important; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ЛОГИКА ВХОДА ---
if not st.session_state.logged_in:
    st.title("🌌 MilkyGram")
    c1, _ = st.columns([1, 2])
    with c1:
        with st.container(border=True):
            u = st.text_input("Позывной")
            p = st.text_input("Пароль", type="password")
            if st.button("Войти"):
                res = requests.get(f"{DB_URL}users/{u}.json").json()
                if res and res.get('password') == hash_pass(p):
                    st.session_state.logged_in, st.session_state.username = True, u
                    st.rerun()
            if st.button("Регистрация"):
                requests.put(f"{DB_URL}users/{u}.json", json={"password": hash_pass(p), "avatar": DEFAULT_AVA, "bio": "Пилот", "following": []})
                st.success("Аккаунт создан!")
    st.stop()

# --- ДАННЫЕ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})
my_following = my_data.get('following', [])

# --- МЕНЮ ---
with st.sidebar:
    st.markdown(f"### @{st.session_state.username}")
    s_q = st.text_input("🔍 Поиск", placeholder="Ник или группа...")
    if s_q: 
        st.session_state.page = "search"
        st.session_state.search_query = s_q
    
    st.write("---")
    for lab, pg in {"🏠 Мой профиль": "my_profile", "📡 Новости": "feed", "📟 Сообщения": "dm"}.items():
        if st.button(lab): st.session_state.page, st.session_state.viewing_profile = pg, None; st.rerun()
    
    st.write("---")
    if st.toggle("🌙 Темная тема", value=(st.session_state.theme == "Dark")): st.session_state.theme = "Dark"
    else: st.session_state.theme = "Light"
    if st.button("🚪 Выйти"): st.session_state.logged_in = False; st.rerun()

# --- ФУНКЦИЯ ВЫВОДА ПОСТА ---
def draw_post(pid, p):
    with st.container(border=True):
        h1, h2 = st.columns([5, 1])
        if h1.button(f"👤 @{p.get('author')}", key=f"b_{pid}"):
            st.session_state.viewing_profile = p.get('author'); st.rerun()
        h2.caption(p.get('time', ''))
        
        # Безопасный вывод картинки (фикс Error opening '')
        img_url = p.get('img')
        if img_url and len(img_url) > 5: # Проверка, что ссылка не пустая
            try:
                st.image(img_url, width='stretch')
            except:
                st.caption("⚠️ Ошибка загрузки снимка")
        
        st.write(p.get('text', ''))
        likes = p.get('likes', 0)
        if st.button(f"✨ {likes}", key=f"l_{pid}"):
            requests.patch(f"{DB_URL}posts/{pid}.json", json={"likes": likes + 1}); st.rerun()

# --- СТРАНИЦЫ ---

# 1. НОВОСТИ
if st.session_state.page == "feed":
    st.title("Новости")
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        if p.get('author') in my_following or p.get('author') == st.session_state.username:
            draw_post(pid, p)

# 2. ПРОФИЛЬ
elif st.session_state.page == "my_profile" or st.session_state.viewing_profile:
    target = st.session_state.viewing_profile or st.session_state.username
    u_info = all_users.get(target, {})
    
    with st.container(border=True):
        c1, c2 = st.columns([1, 4])
        # Аватар тоже с проверкой
        ava = u_info.get('avatar', DEFAULT_AVA)
        c1.image(ava if ava else DEFAULT_AVA, width=120)
        with c2:
            st.subheader(target)
            st.write(f"*{u_info.get('bio', '')}*")
            if target != st.session_state.username:
                is_sub = target in my_following
                if st.button("Отписаться" if is_sub else "Подписаться"):
                    if is_sub: my_following.remove(target)
                    else: my_following.append(target)
                    requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"following": my_following})
                    st.rerun()
    
    st.write("---")
    st.subheader("📝 Стена")
    if target == st.session_state.username:
        with st.container(border=True):
            txt_p = st.text_area("Что нового?", height=70)
            img_p = st.text_input("URL картинки")
            if st.button("Опубликовать"):
                requests.post(f"{DB_URL}posts.json", json={
                    "author": target, "text": txt_p, "img": img_p, 
                    "time": datetime.now().strftime("%H:%M"), "likes": 0
                })
                st.rerun()
    
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        if p.get('author') == target:
            draw_post(pid, p)

# 3. ПОИСК
elif st.session_state.page == "search":
    st.title(f"Поиск: {st.session_state.search_query}")
    for name, data in all_users.items():
        if st.session_state.search_query.lower() in name.lower():
            with st.container(border=True):
                if st.button(f"👤 @{name}", key=f"s_{name}"):
                    st.session_state.viewing_profile = name; st.rerun()

# 4. МЕССЕНДЖЕР
elif st.session_state.page == "dm":
    st.title("Радиоэфир")
    target = st.selectbox("Диалог", [u for u in all_users if u != st.session_state.username])
    chat_id = "".join(sorted([st.session_state.username, target]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    for m in msgs.values():
        st.write(f"**{m['from']}**: {m['text']}")
    m_txt = st.text_input("Сигнал...")
    if st.button("Пуск"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={"from": st.session_state.username, "text": m_txt})
        st.rerun()
