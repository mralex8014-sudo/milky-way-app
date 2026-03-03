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

# --- ДИНАМИЧЕСКИЙ ДИЗАЙН ---
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
        border-radius: 4px; padding: 12px !important; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }}
    .stButton>button {{ 
        border-radius: 4px; background-color: {accent}; color: white !important; 
        border: none; width: 100%; transition: 0.2s;
    }}
    .stButton>button:hover {{ opacity: 0.8; transform: translateY(-1px); }}
    input {{ background-color: {bg} !important; color: {txt} !important; border: 1px solid {brd} !important; }}
    </style>
    """, unsafe_allow_html=True)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ЛОГИКА ВХОДА ---
if not st.session_state.logged_in:
    st.title("🌌 MilkyGram: Вход в сеть")
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
            st.caption("Нет аккаунта? Просто введи новый позывной и нажми регистрацию.")
            if st.button("Зарегистрироваться"):
                requests.put(f"{DB_URL}users/{u}.json", json={"password": hash_pass(p), "avatar": DEFAULT_AVA, "bio": "Новый пилот", "following": []})
                st.success("Готово! Теперь жми Войти.")
    st.stop()

# --- ЗАГРУЗКА ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
nebulas = requests.get(f"{DB_URL}nebulas.json").json() or {}
my_data = all_users.get(st.session_state.username, {})
my_following = my_data.get('following', [])

# --- ГЛОБАЛЬНЫЙ ПОИСК ---
with st.sidebar:
    st.markdown(f"### @{st.session_state.username}")
    s_q = st.text_input("🔍 Поиск", placeholder="Найти позывной или группу...")
    if s_q: 
        st.session_state.page = "search"
        st.session_state.search_query = s_q

    st.write("---")
    menu = {"🏠 Мой профиль": "my_profile", "📡 Новости": "feed", "📟 Сообщения": "dm", "☁️ Туманности": "nebulas"}
    for label, pg in menu.items():
        if st.button(label): st.session_state.page, st.session_state.viewing_profile = pg, None; st.rerun()
    
    st.write("---")
    if st.toggle("🌙 Темная тема", value=(st.session_state.theme == "Dark")): st.session_state.theme = "Dark"
    else: st.session_state.theme = "Light"
    if st.button("🚪 Выйти"): st.session_state.logged_in = False; st.rerun()

# --- РЕНДЕР ПОСТА ---
def draw_post(pid, p):
    with st.container(border=True):
        col_a, col_t = st.columns([5, 1])
        if col_a.button(f"👤 @{p.get('author')}", key=f"btn_{pid}"):
            st.session_state.viewing_profile = p.get('author'); st.rerun()
        col_t.caption(p.get('time', ''))
        if p.get('img'): st.image(p['img'], use_container_width=True)
        st.write(p.get('text', ''))
        
        c1, c2, c3 = st.columns([1, 1, 4])
        likes = p.get('likes', 0)
        if c1.button(f"✨ {likes}", key=f"lk_{pid}"):
            requests.patch(f"{DB_URL}posts/{pid}.json", json={"likes": likes + 1}); st.rerun()
        if c2.button("💬", key=f"cm_{pid}"): pass # Можно добавить разворот комментов

# --- СТРАНИЦЫ ---

# 1. ЛЕНТА НОВОСТЕЙ (Только подписки)
if st.session_state.page == "feed":
    st.title("Новости")
    all_posts = requests.get(f"{DB_URL}posts.json").json() or {}
    followed_anything = False
    for pid, p in reversed(list(all_posts.items())):
        if p.get('author') in my_following or p.get('author') == st.session_state.username:
            draw_post(pid, p)
            followed_anything = True
    if not followed_anything:
        st.info("Ваш горизонт пуст. Подпишитесь на пилотов или Туманности!")

# 2. ПРОФИЛЬ
elif st.session_state.page == "my_profile" or st.session_state.viewing_profile:
    target = st.session_state.viewing_profile or st.session_state.username
    u_info = all_users.get(target, {})
    
    c1, c2 = st.columns([1, 4])
    with c1:
        st.image(u_info.get('avatar', DEFAULT_AVA), use_container_width=True)
    with c2:
        st.title(target)
        st.write(f"*{u_info.get('bio', 'Исследователь космоса')}*")
        
        # Кнопки взаимодействия
        col1, col2 = st.columns(2)
        if target != st.session_state.username:
            is_sub = target in my_following
            if col1.button("Отписаться" if is_sub else "Подписаться"):
                if is_sub: my_following.remove(target)
                else: my_following.append(target)
                requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"following": my_following})
                st.rerun()
            if col2.button("Написать сообщение"):
                st.session_state.page = "dm"; st.session_state.chat_with = target; st.rerun()
        else:
            if col1.button("⚙️ Настройки"): st.session_state.page = "settings"; st.rerun()

    st.write("---")
    # Стена
    st.subheader("📝 Стена")
    with st.container(border=True):
        t_post = st.text_area("Написать на стене...", height=70, label_visibility="collapsed")
        i_post = st.text_input("Ссылка на изображение (опционально)")
        if st.button("Опубликовать"):
            requests.post(f"{DB_URL}posts.json", json={
                "author": target, "creator": st.session_state.username, 
                "text": t_post, "img": i_post, "time": datetime.now().strftime("%H:%M"), "likes": 0
            })
            st.rerun()
            
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        if p.get('author') == target:
            draw_post(pid, p)

# 3. МЕССЕНДЖЕР
elif st.session_state.page == "dm":
    st.title("Сообщения")
    chat_with = st.session_state.get('chat_with') or st.selectbox("Выберите диалог", [u for u in all_users if u != st.session_state.username])
    
    chat_id = "".join(sorted([st.session_state.username, chat_with]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    
    with st.container(border=True):
        for m in msgs.values():
            side = "flex-end" if m['from'] == st.session_state.username else "flex-start"
            clr = accent if m['from'] == st.session_state.username else brd
            st.markdown(f"""<div style="display: flex; justify-content: {side}; margin-bottom: 5px;">
                <div style="background: {clr}; padding: 8px; border-radius: 10px; max-width: 70%;">
                <b>{m['from']}</b>: {m['text']}</div></div>""", unsafe_allow_html=True)
    
    m_txt = st.text_input("Ваш сигнал...")
    if st.button("Отправить"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={"from": st.session_state.username, "text": m_txt})
        st.rerun()

# 4. ПОИСК
elif st.session_state.page == "search":
    st.title(f"Результаты поиска: {st.session_state.search_query}")
    for name, data in all_users.items():
        if st.session_state.search_query.lower() in name.lower():
            with st.container(border=True):
                c1, c2 = st.columns([1, 5])
                c1.image(data.get('avatar', DEFAULT_AVA), width=50)
                if c2.button(f"Перейти к @{name}", key=f"s_{name}"):
                    st.session_state.viewing_profile = name; st.session_state.page = "view_profile"; st.rerun()

# 5. НАСТРОЙКИ
elif st.session_state.page == "settings":
    st.title("Настройки профиля")
    new_bio = st.text_area("О себе", value=my_data.get('bio', ''))
    new_ava = st.text_input("Ссылка на аватар", value=my_data.get('avatar', DEFAULT_AVA))
    if st.button("Сохранить"):
        requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"bio": new_bio, "avatar": new_ava})
        st.success("Обновлено!")
