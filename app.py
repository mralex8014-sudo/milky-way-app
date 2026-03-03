import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка Вселенной
st.set_page_config(page_title="MilkyGram Pro", page_icon="🌌", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ SESSION STATE ---
for key, val in {
    'logged_in': False, 'username': "", 'page': "my_profile", 
    'viewing_profile': None, 'theme': "Dark", 'chat_with': None
}.items():
    if key not in st.session_state: st.session_state[key] = val

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- СТИЛИЗАЦИЯ ---
if st.session_state.theme == "Dark":
    bg, txt, brd, inp, accent = "#0A0A0C", "#E0E0E0", "#22222E", "#11111B", "#3D3D6B"
else:
    bg, txt, brd, inp, accent = "#EDEEF0", "#222222", "#DCE1E6", "#FFFFFF", "#4A76A8"

st.markdown(f"""<style>
    html, body, [class*='css'] {{ font-size: 13px !important; color: {txt}; }}
    .stApp {{ background-color: {bg}; }}
    div[data-testid='stVerticalBlock'] > div[style*='border: 1px solid'] {{ 
        background-color: {inp} !important; border: 1px solid {brd} !important; border-radius: 8px; 
    }}
    .stButton>button {{ border-radius: 6px; background-color: {accent}; color: white !important; width: 100%; }}
</style>""", unsafe_allow_html=True)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def safe_image(url, w=None):
    valid_url = url if (url and isinstance(url, str) and len(url) > 5) else DEFAULT_AVA
    try:
        if w == 'stretch': st.image(valid_url, width='stretch')
        else: st.image(valid_url, width=w if w else 150)
    except:
        st.image(DEFAULT_AVA, width=w if (w and w != 'stretch') else 150)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- ЛОГИКА ВХОДА ---
if not st.session_state.logged_in:
    st.title("🌌 MilkyGram Pro")
    c1, _ = st.columns([1, 2])
    with c1:
        with st.container(border=True):
            u_login = st.text_input("Позывной")
            p_login = st.text_input("Код", type="password")
            if st.button("Войти"):
                res = requests.get(f"{DB_URL}users/{u_login}.json").json()
                if res and res.get('password') == hash_pass(p_login):
                    st.session_state.logged_in, st.session_state.username = True, u_login
                    st.rerun()
                else: st.error("Неверный позывной или код")
    st.stop()

# --- ОБНОВЛЕНИЕ СТАТУСА ONLINE ---
requests.patch(f"{DB_URL}users/{st.session_state.username}.json", 
               json={"last_seen": datetime.now().strftime("%H:%M")})

# --- ЗАГРУЗКА ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})

# --- САЙДБАР ---
with st.sidebar:
    st.markdown(f"### @{st.session_state.username}")
    if st.button("🏠 Моя страница"): st.session_state.page, st.session_state.viewing_profile = "my_profile", None; st.rerun()
    if st.button("📡 Лента новостей"): st.session_state.page = "feed"; st.rerun()
    if st.button("📟 Сообщения"): st.session_state.page = "dm"; st.rerun()
    if st.button("📝 Анкета"): st.session_state.page = "settings"; st.rerun()
    st.write("---")
    if st.button("🚪 Выйти"): st.session_state.logged_in = False; st.rerun()

# --- СТРАНИЦА ПРОФИЛЯ ---
if st.session_state.page == "my_profile" or st.session_state.viewing_profile:
    target = st.session_state.viewing_profile or st.session_state.username
    u_prof = all_users.get(target, {})
    info = u_prof.get('info', {})
    
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        with c1: safe_image(u_prof.get('avatar'), w='stretch')
        with c2:
            now_time = datetime.now().strftime("%H:%M")
            is_online = u_prof.get('last_seen') == now_time
            online_html = f'<span style="color:green; font-size:10px;">● online</span>' if is_online else f'<span style="color:gray; font-size:10px;">был в {u_prof.get("last_seen", "---")}</span>'
            st.markdown(f"### {info.get('f_name', target)} {online_html}", unsafe_allow_html=True)
            st.caption(f"📢 {u_prof.get('status', 'Статус не задан')}")
            st.markdown(f"**Город:** {info.get('city', '---')} | **ДР:** {info.get('bday', '---')} | **СП:** {info.get('status_rel', '---')}")
            st.write(f"🧩 **Интересы:** {info.get('interests', '---')}")
            
            if target != st.session_state.username:
                if st.button("✉️ Написать сообщение"):
                    st.session_state.page = "dm"; st.session_state.chat_with = target; st.rerun()

    # Списки Друзей и Подписчиков (Логика подписок)
    my_ing = my_data.get('following', []) or []
    t_ing = u_prof.get('following', []) or []
    t_ers = u_prof.get('followers', []) or []
    friends = [name for name in t_ing if name in t_ers]
    only_subs = [name for name in t_ers if name not in t_ing]

    tab1, tab2, tab3 = st.tabs([f"👥 Друзья ({len(friends)})", f"📥 Подписчики ({len(only_subs)})", "🖼 Галерея"])
    
    with tab1:
        for f in friends:
            if st.button(f"👤 {f}", key=f"f_list_{f}"): st.session_state.viewing_profile = f; st.rerun()
    with tab2:
        for s in only_subs:
            if st.button(f"👽 {s}", key=f"s_list_{s}"): st.session_state.viewing_profile = s; st.rerun()
    with tab3:
        posts_all = requests.get(f"{DB_URL}posts.json").json() or {}
        imgs = [p['img'] for p in posts_all.values() if p.get('author') == target and p.get('img') and len(p['img']) > 5]
        if imgs:
            cols = st.columns(3)
            for idx, img_url in enumerate(imgs[:9]):
                cols[idx % 3].image(img_url, use_container_width=True)
        else: st.caption("Галерея пуста")

    st.markdown("---")
    st.subheader("📝 Стена")
    with st.container(border=True):
        t_wall = st.text_area("Оставить запись...", height=60, key="wall_in")
        if st.button("Опубликовать"):
            requests.post(f"{DB_URL}posts.json", json={
                "author": target, "creator": st.session_state.username, 
                "text": t_wall, "time": now_time, "likes": 0
            })
            st.rerun()

    posts_data = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts_data.items())):
        if p.get('author') == target:
            with st.container(border=True):
                # ФИКС KEYERROR 'creator': используем .get()
                creator_name = p.get('creator', p.get('author', 'Аноним'))
                st.write(f"**{creator_name}** <small>{p.get('time', '')}</small>", unsafe_allow_html=True)
                st.write(p.get('text', ''))
                with st.expander(f"💬 {len(p.get('comments', {}))}"):
                    for cid, c in p.get('comments', {}).items():
                        st.write(f"**{c.get('user', '???')}**: {c.get('txt', '')}")
                    c_in = st.text_input("Ответить...", key=f"in_{pid}")
                    if st.button("ОК", key=f"btn_{pid}"):
                        requests.post(f"{DB_URL}posts/{pid}/comments.json", json={"user": st.session_state.username, "txt": c_in})
                        st.rerun()

# --- МЕССЕНДЖЕР ---
elif st.session_state.page == "dm":
    st.title("📟 Радиоэфир")
    # Если мы пришли из профиля, контакт уже выбран
    contact_list = [u for u in all_users if u != st.session_state.username]
    selected_contact = st.session_state.get('chat_with')
    
    target_chat = st.selectbox("Собеседник", contact_list, index=contact_list.index(selected_contact) if selected_contact in contact_list else 0)
    
    chat_id = "".join(sorted([st.session_state.username, target_chat]))
    msgs = requests.get(f"{DB_URL}messages/{chat_id}.json").json() or {}
    
    with st.container(border=True):
        for mid, m in msgs.items():
            align = "right" if m.get('from') == st.session_state.username else "left"
            st.markdown(f"<div style='text-align:{align};'><b>{m.get('from')}</b>: {m.get('text')}</div>", unsafe_allow_html=True)
    
    m_in = st.text_input("Введите сообщение...", key="msg_input")
    if st.button("Отправить сигнал"):
        requests.post(f"{DB_URL}messages/{chat_id}.json", json={"from": st.session_state.username, "text": m_in, "time": datetime.now().strftime("%H:%M")})
        st.rerun()

# --- ЛЕНТА НОВОСТЕЙ ---
elif st.session_state.page == "feed":
    st.title("📡 Новости Федерации")
    posts_data = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts_data.items())):
        # Показываем посты друзей и свои
        if p.get('author') in my_data.get('following', []) or p.get('author') == st.session_state.username:
            with st.container(border=True):
                st.write(f"👤 **{p.get('author')}**")
                if p.get('img'): st.image(p['img'], use_container_width=True)
                st.write(p.get('text', ''))
                if st.button(f"✨ {p.get('likes', 0)}", key=f"lk_feed_{pid}"):
                    requests.patch(f"{DB_URL}posts/{pid}.json", json={"likes": p.get('likes', 0) + 1})
                    st.rerun()

# --- АНКЕТА ---
elif st.session_state.page == "settings":
    st.title("🛰️ Ваше Личное Дело")
    with st.container(border=True):
        i = my_data.get('info', {})
        new_fn = st.text_input("Имя", value=i.get('f_name', ''))
        new_ln = st.text_input("Фамилия", value=i.get('l_name', ''))
        new_bd = st.text_input("Дата рождения", value=i.get('bday', ''))
        new_ct = st.text_input("Город", value=i.get('city', ''))
        new_rl = st.selectbox("Семейное положение", ["Свободен", "В отношениях", "Сложно"], index=0)
        new_em = st.text_input("Почта", value=i.get('email', ''))
        new_it = st.text_area("Интересы", value=i.get('interests', ''))
        st.write("---")
        new_stat = st.text_input("Статус", value=my_data.get('status', ''))
        new_ava = st.text_input("URL аватара", value=my_data.get('avatar', ''))
        
        if st.button("Синхронизировать данные"):
            requests.patch(f"{DB_URL}users/{st.session_state.username}.json", json={
                "info": {"f_name": new_fn, "l_name": new_ln, "bday": new_bd, "city": new_ct, "status_rel": new_rl, "email": new_em, "interests": new_it},
                "status": new_stat, "avatar": new_ava
            })
            st.success("Данные успешно отправлены на орбиту!")
