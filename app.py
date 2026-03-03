import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка страницы
st.set_page_config(page_title="MilkyGram", page_icon="🌌", layout="centered")

# --- ИНИЦИАЛИЗАЦИЯ SESSION STATE ---
for key, val in {
    'logged_in': False, 'username': "", 'page': "feed", 
    'viewing_profile': None, 'theme': "Dark"
}.items():
    if key not in st.session_state: st.session_state[key] = val

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- АДАПТИВНАЯ ЦВЕТОВАЯ СХЕМА ---
if st.session_state.theme == "Dark":
    bg, txt, brd, inp, accent = "#050505", "#E0E0E0", "#1B1B3A", "#0F0F1B", "#3D3D6B"
else:
    # Светлая тема: черный текст на белом фоне, серые границы
    bg, txt, brd, inp, accent = "#FFFFFF", "#1A1A1A", "#DBDBDB", "#F8F9FA", "#E0E0FF"

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-size: 14px !important; color: {txt} !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    
    /* Сайдбар */
    [data-testid="stSidebar"] {{ background-color: {inp}; border-right: 1px solid {brd}; }}
    [data-testid="stSidebar"] .stText, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h3 {{ color: {txt} !important; }}
    
    /* Заголовки и текст */
    h1, h2, h3, p, span, label, .stMarkdown {{ color: {txt} !important; }}
    
    /* Кнопки */
    .stButton>button {{ 
        border-radius: 10px; padding: 2px 10px; font-size: 12px !important; 
        background-color: {accent}; color: {txt if st.session_state.theme == 'Light' else 'white'} !important;
        border: 1px solid {brd};
    }}
    .stButton>button:hover {{ border-color: #6D6D9D; color: #6D6D9D !important; }}
    
    /* Карточки постов и блоков */
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {inp} !important; border: 1px solid {brd} !important; 
        border-radius: 12px; padding: 12px !important;
    }}
    
    /* Поля ввода */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {bg} !important; color: {txt} !important; border: 1px solid {brd} !important;
    }}
    
    /* Комментарии */
    .comment-box {{ 
        font-size: 12px; background: {bg}; padding: 6px; border-radius: 8px; 
        margin-top: 4px; border: 1px solid {brd}; color: {txt};
    }}
    
    /* Чат */
    .msg-cloud {{ padding: 6px 12px; border-radius: 12px; margin-bottom: 4px; display: inline-block; }}
    </style>
    """, unsafe_allow_html=True)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ЛОГИКА ВХОДА ---
if not st.session_state.logged_in:
    st.title("🌌 MilkyGram")
    with st.container(border=True):
        u = st.text_input("Позывной", key="log_u")
        p = st.text_input("Код", type="password", key="log_p")
        if st.button("Войти"):
            res = requests.get(f"{DB_URL}users/{u}.json").json()
            if res and res.get('password') == hash_pass(p):
                st.session_state.logged_in, st.session_state.username = True, u
                st.rerun()
            else: st.error("Ошибка доступа")
    st.stop()

# --- ЗАГРУЗКА ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})
my_satellites = my_data.get('satellites', []) or []

# --- ФУНКЦИИ ---
def show_user_profile(name):
    u = all_users.get(name)
    if not u: return
    st.subheader(f"Профиль @{name}")
    c1, c2 = st.columns([1, 3])
    c1.image(u.get('avatar', DEFAULT_AVA), width=80)
    with c2:
        st.write(f"*{u.get('bio', 'Исследователь')}*")
        if name != st.session_state.username:
            if name in my_satellites:
                if st.button("💥 Разорвать связь"):
                    my_satellites.remove(name); requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites}); st.rerun()
            else:
                if st.button("🔗 Установить связь"):
                    my_satellites.append(name); requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"satellites": my_satellites}); st.rerun()

# --- МЕНЮ ---
with st.sidebar:
    st.write(f"### @{st.session_state.username}")
    t_toggle = st.toggle("🌙 Темный режим", value=(st.session_state.theme == "Dark"))
    if t_toggle != (st.session_state.theme == "Dark"):
        st.session_state.theme = "Dark" if t_toggle else "Light"
        st.rerun()
    
    st.write("---")
    btns = {"📡 Лента": "feed", "🔍 Поиск": "search", "📟 Радио": "dm", "🌌 Связи": "galaxy", "👨‍🚀 Профиль": "my_profile"}
    for lab, pg in btns.items():
        if st.button(lab): st.session_state.page, st.session_state.viewing_profile = pg, None; st.rerun()
    if st.button("🚪 Выход"): st.session_state.logged_in = False; st.rerun()

# --- КОНТЕНТ ---
if st.session_state.viewing_profile:
    show_user_profile(st.session_state.viewing_profile)
    if st.button("← Назад"): st.session_state.viewing_profile = None; st.rerun()

elif st.session_state.page == "feed":
    st.title("Лента")
    with st.expander("📝 Создать пост"):
        img = st.text_input("URL фото")
        txt_p = st.text_area("Текст", height=70)
        if st.button("Отправить"):
            requests.post(f"{DB_URL}posts.json", json={"author": st.session_state.username, "img": img, "text": txt_p, "time": datetime.now().strftime("%H:%M"), "likes": 0})
            st.rerun()
    
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        with st.container(border=True):
            h1, h2 = st.columns([3, 1])
            if h1.button(f"@{p.get('author')}", key=f"u_{pid}"):
                st.session_state.viewing_profile = p.get('author'); st.rerun()
            h2.caption(p.get('time'))
            if p.get('img'): st.image(p['img'], width=350)
            st.write(p.get('text', ''))
            
            l1, l2 = st.columns([1, 5])
            if l1.button(f"✨ {p.get('likes', 0)}", key=f"l_{pid}"):
                requests.patch(f"{DB_URL}posts/{pid}.json", json={"likes": p.get('likes', 0) + 1}); st.rerun()
            
            with st.expander("💬 Обсуждение"):
                coms = p.get('comments', {})
                for c in coms.values():
                    st.markdown(f"<div class='comment-box'><b>{c['user']}</b>: {c['txt']}</div>", unsafe_allow_html=True)
                c_in = st.text_input("...", key=f"in_{pid}", label_visibility="collapsed")
                if st.button("OK", key=f"s_{pid}"):
                    requests.post(f"{DB_URL}posts/{pid}/comments.json", json={"user": st.session_state.username, "txt": c_in}); st.rerun()

elif st.session_state.page == "dm":
    st.title("Радиоэфир")
    target = st.selectbox("Собеседник", [u for u in all_users.keys() if u != st.session_state.username])
    chat_id = "".join(sorted([st.session_state.username, target]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    for m in msgs.values():
        align = "right" if m['from'] == st.session_state.username else "left"
        c_bg = "#3D3D6B" if align == "right" else brd
        c_tx = "white" if align == "right" else txt
        st.markdown(f"<div style='text-align:{align};'><div class='msg-cloud' style='background:{c_bg}; color:{c_tx};'>{m['text']}</div></div>", unsafe_allow_html=True)
    m_in = st.text_input("Сообщение...", key="m_in")
    if st.button("Послать"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={"from": st.session_state.username, "text": m_in, "time": datetime.now().strftime("%H:%M")}); st.rerun()

elif st.session_state.page == "my_profile":
    st.title("Настройки")
    with st.container(border=True):
        new_a = st.text_input("Аватар URL", value=my_data.get('avatar', DEFAULT_AVA))
        new_b = st.text_area("О себе", value=my_data.get('bio', ''))
        if st.button("Сохранить изменения"):
            requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"avatar": new_a, "bio": new_b}); st.rerun()

elif st.session_state.page == "search":
    st.title("Поиск")
    q = st.text_input("Никнейм...", label_visibility="collapsed")
    for name in all_users:
        if q.lower() in name.lower() and name != st.session_state.username:
            if st.button(f"👤 @{name}", key=f"sr_{name}"):
                st.session_state.viewing_profile = name; st.rerun()

elif st.session_state.page == "galaxy":
    st.title("Спутники")
    for s in my_satellites:
        if st.button(f"🛰️ @{s}", key=f"gal_{s}"): st.session_state.viewing_profile = s; st.rerun()
