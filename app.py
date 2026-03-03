import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка страницы
st.set_page_config(page_title="MilkyGram", page_icon="🌌", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ ---
for key, val in {
    'logged_in': False, 'username': "", 'page': "feed", 
    'viewing_profile': None, 'theme': "Dark", 'viewing_nebula': None
}.items():
    if key not in st.session_state: st.session_state[key] = val

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ЦВЕТОВАЯ СХЕМА (ВК-стайл) ---
if st.session_state.theme == "Dark":
    bg, txt, brd, inp, accent = "#0A0A0A", "#E1E1E1", "#222222", "#161616", "#2D2D4D"
else:
    bg, txt, brd, inp, accent = "#EDEEF0", "#000000", "#DCE1E6", "#FFFFFF", "#E1E9F1"

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-size: 13px !important; color: {txt} !important; }}
    .stApp {{ background-color: {bg}; color: {txt}; }}
    
    /* Контейнеры (Белые блоки как в ВК) */
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {{
        background-color: {inp} !important; border: 1px solid {brd} !important; 
        border-radius: 8px; padding: 15px !important; margin-bottom: 10px;
    }}
    
    /* Сайдбар */
    [data-testid="stSidebar"] {{ background-color: {bg}; border-right: none; }}
    .stButton>button {{ 
        border-radius: 6px; padding: 4px; font-size: 13px !important; 
        background-color: {accent}; color: {txt} !important; border: none; text-align: left;
    }}
    
    /* Посты */
    .post-header {{ font-weight: bold; color: #4A76A8; cursor: pointer; }}
    .comment-box {{ background: {bg}; padding: 8px; border-radius: 4px; margin-top: 5px; border: 1px solid {brd}; }}
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
            p = st.text_input("Код", type="password")
            if st.button("Войти в систему"):
                res = requests.get(f"{DB_URL}users/{u}.json").json()
                if res and res.get('password') == hash_pass(p):
                    st.session_state.logged_in, st.session_state.username = True, u
                    st.rerun()
    st.stop()

# --- ЗАГРУЗКА ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
nebulas = requests.get(f"{DB_URL}nebulas.json").json() or {}
my_data = all_users.get(st.session_state.username, {})

# --- МЕНЮ (СЛЕВА КАК В ВК) ---
with st.sidebar:
    st.markdown(f"### @{st.session_state.username}")
    if st.button("🏠 Моя страница"): st.session_state.page, st.session_state.viewing_profile = "my_profile", None; st.rerun()
    if st.button("📡 Горизонт (Лента)"): st.session_state.page = "feed"; st.rerun()
    if st.button("📟 Радио (Мессенджер)"): st.session_state.page = "dm"; st.rerun()
    if st.button("🔍 Поиск пилотов"): st.session_state.page = "search"; st.rerun()
    if st.button("☁️ Туманности (Группы)"): st.session_state.page = "nebulas"; st.rerun()
    st.write("---")
    if st.toggle("🌙 Тема", value=(st.session_state.theme == "Dark")): st.session_state.theme = "Dark"
    else: st.session_state.theme = "Light"
    if st.button("🚪 Выход"): st.session_state.logged_in = False; st.rerun()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def render_post(pid, p, is_nebula=False):
    with st.container(border=True):
        author_name = p.get('author')
        col_a, col_t = st.columns([4, 1])
        if col_a.button(f"👤 {author_name}", key=f"p_btn_{pid}"):
            if is_nebula: st.session_state.viewing_nebula = author_name
            else: st.session_state.viewing_profile = author_name
            st.rerun()
        col_t.caption(p.get('time'))
        if p.get('img'): st.image(p['img'], use_container_width=True)
        st.write(p.get('text', ''))
        
        l1, l2 = st.columns([1, 5])
        if l1.button(f"✨ {p.get('likes', 0)}", key=f"l_{pid}"):
            path = "nebulas" if is_nebula else "posts"
            requests.patch(f"{DB_URL}{path}/{pid}.json", json={"likes": p.get('likes', 0) + 1}); st.rerun()

# --- СТРАНИЦЫ ---

# 1. ЛЕНТА
if st.session_state.page == "feed":
    st.title("Новости")
    all_posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(all_posts.items())):
        render_post(pid, p)

# 2. ПРОФИЛЬ (МОЙ ИЛИ ЧУЖОЙ)
elif st.session_state.page in ["my_profile", "view_profile"] or st.session_state.viewing_profile:
    target = st.session_state.viewing_profile or st.session_state.username
    user = all_users.get(target, {})
    
    st.title(f"@{target}")
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        c1.image(user.get('avatar', DEFAULT_AVA), width=150)
        with c2:
            st.subheader(target)
            st.write(f"ℹ️ {user.get('bio', 'Нет описания')}")
            if target != st.session_state.username:
                if st.button("📟 Написать сообщение"): 
                    st.session_state.page = "dm"; st.session_state.chat_with = target; st.rerun()
            else:
                if st.button("⚙️ Редактировать"): st.session_state.page = "settings"; st.rerun()

    st.write("### 📝 Стена")
    if target == st.session_state.username:
        with st.expander("Что нового?"):
            img = st.text_input("URL фото")
            txt_p = st.text_area("Текст")
            if st.button("Опубликовать"):
                requests.post(f"{DB_URL}posts.json", json={"author": target, "img": img, "text": txt_p, "time": datetime.now().strftime("%H:%M"), "likes": 0})
                st.rerun()
    
    # Фильтруем посты только этого пользователя
    all_posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(all_posts.items())):
        if p.get('author') == target:
            render_post(pid, p)

# 3. ТУМАННОСТИ (СООБЩЕСТВА)
elif st.session_state.page == "nebulas":
    st.title("☁️ Туманности")
    with st.expander("✨ Создать Туманность"):
        n_name = st.text_input("Название")
        n_bio = st.text_input("Описание")
        if st.button("Создать"):
            requests.put(f"{DB_URL}nebulas/{n_name}.json", json={"creator": st.session_state.username, "bio": n_bio, "avatar": DEFAULT_AVA})
            st.rerun()
    
    for name, data in nebulas.items():
        with st.container(border=True):
            st.write(f"### {name}")
            st.caption(data.get('bio'))
            if st.button(f"Войти в {name}", key=f"neb_{name}"):
                st.session_state.page = "nebula_view"; st.session_state.viewing_nebula = name; st.rerun()

elif st.session_state.page == "nebula_view":
    neb_name = st.session_state.viewing_nebula
    neb_data = nebulas.get(neb_name, {})
    st.title(f"☁️ {neb_name}")
    st.caption(neb_data.get('bio'))
    
    if neb_data.get('creator') == st.session_state.username:
        with st.expander("📢 Опубликовать от имени группы"):
            txt_n = st.text_area("Текст поста")
            if st.button("Послать в Туманность"):
                requests.post(f"{DB_URL}posts.json", json={"author": f"{neb_name} (Группа)", "text": txt_n, "time": datetime.now().strftime("%H:%M"), "likes": 0})
                st.rerun()
    
    # Посты группы
    all_posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(all_posts.items())):
        if neb_name in p.get('author', ''):
            render_post(pid, p, is_nebula=True)

# 4. РАДИО (МЕССЕНДЖЕР)
elif st.session_state.page == "dm":
    st.title("📟 Радиоэфир")
    target = st.selectbox("Выберите контакт", [u for u in all_users.keys() if u != st.session_state.username])
    chat_id = "".join(sorted([st.session_state.username, target]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    
    with st.container(border=True):
        for m in msgs.values():
            st.write(f"**{m['from']}**: {m['text']}")
    
    m_in = st.text_input("Ваш сигнал...")
    if st.button("Отправить"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={"from": st.session_state.username, "text": m_in, "time": datetime.now().strftime("%H:%M")})
        st.rerun()

# 5. НАСТРОЙКИ
elif st.session_state.page == "settings":
    st.title("⚙️ Настройки")
    with st.container(border=True):
        new_ava = st.text_input("URL аватара", value=my_data.get('avatar', DEFAULT_AVA))
        new_bio = st.text_area("О себе", value=my_data.get('bio', ''))
        if st.button("Сохранить изменения"):
            requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={"avatar": new_ava, "bio": new_bio})
            st.success("Обновлено!")
