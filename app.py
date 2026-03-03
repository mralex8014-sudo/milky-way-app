import streamlit as st
import requests
from datetime import datetime
import hashlib

# 1. Настройка Вселенной
st.set_page_config(page_title="MilkyGram Pro", page_icon="🌌", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ ---
defaults = {
    'logged_in': False, 'username': "", 'page': "my_profile", 
    'viewing_profile': None, 'theme': "Dark"
}
for key, val in defaults.items():
    if key not in st.session_state: st.session_state[key] = val

DB_URL = "https://milky-way-8ea60-default-rtdb.firebaseio.com/"
DEFAULT_AVA = "https://cdn-icons-png.flaticon.com/512/2592/2592188.png"

# --- ЦВЕТОВАЯ СХЕМА ---
if st.session_state.theme == "Dark":
    bg, txt, brd, inp, accent = "#0A0A0C", "#E0E0E0", "#22222E", "#11111B", "#3D3D6B"
else:
    bg, txt, brd, inp, accent = "#EDEEF0", "#222222", "#DCE1E6", "#FFFFFF", "#4A76A8"

st.markdown(f"<style>html, body, [class*='css'] {{ font-size: 13px !important; color: {txt}; }} .stApp {{ background-color: {bg}; }} div[data-testid='stVerticalBlock'] > div[style*='border: 1px solid'] {{ background-color: {inp} !important; border: 1px solid {brd} !important; border-radius: 8px; }}</style>", unsafe_allow_html=True)

# --- ЛОГИКА ОБНОВЛЕНИЯ ONLINE ---
if st.session_state.logged_in:
    requests.patch(f"{DB_URL}users/{st.session_state.username}.json", 
                   json={"last_seen": datetime.now().strftime("%d.%m %H:%M")})

# --- ЗАГРУЗКА ДАННЫХ ---
all_users = requests.get(f"{DB_URL}users.json").json() or {}
my_data = all_users.get(st.session_state.username, {})
my_following = my_data.get('following', []) or []
my_followers = my_data.get('followers', []) or []

# --- ФУНКЦИИ ВЗАИМОДЕЙСТВИЯ ---
def get_friends(user_name):
    u = all_users.get(user_name, {})
    ing = u.get('following', []) or []
    ers = u.get('followers', []) or []
    return [name for name in ing if name in ers]

def get_only_followers(user_name):
    u = all_users.get(user_name, {})
    ing = u.get('following', []) or []
    ers = u.get('followers', []) or []
    return [name for name in ers if name not in ing]

# --- САЙДБАР (ВК-СТАЙЛ) ---
with st.sidebar:
    st.title("MilkyGram")
    if st.button("🏠 Моя страница"): st.session_state.page, st.session_state.viewing_profile = "my_profile", None; st.rerun()
    if st.button("📡 Лента новостей"): st.session_state.page = "feed"; st.rerun()
    if st.button("📟 Сообщения"): st.session_state.page = "dm"; st.rerun()
    if st.button("⚙️ Анкета / Настройки"): st.session_state.page = "settings"; st.rerun()
    st.write("---")
    if st.button("🚪 Выйти"): st.session_state.logged_in = False; st.rerun()

# --- СТРАНИЦА ПРОФИЛЯ ---
if st.session_state.page == "my_profile" or st.session_state.viewing_profile:
    target = st.session_state.viewing_profile or st.session_state.username
    u = all_users.get(target, {})
    info = u.get('info', {})
    
    # Шапка профиля
    with st.container(border=True):
        c1, c2 = st.columns([1, 3])
        with c1:
            st.image(u.get('avatar', DEFAULT_AVA), width='stretch')
            if target != st.session_state.username:
                if st.button("✉️ Сообщение"): 
                    st.session_state.page = "dm"; st.session_state.chat_with = target; st.rerun()
        with c2:
            # Статус Online
            last_seen = u.get('last_seen', 'Давно')
            st.markdown(f"### {info.get('f_name', target)} {info.get('l_name', '')} <span style='font-size:10px; color:green;'>● online</span>" if last_seen == datetime.now().strftime("%d.%m %H:%M") else f"### {target} <span style='font-size:10px; color:gray;'>был {last_seen}</span>", unsafe_allow_html=True)
            st.caption(f"📢 {u.get('status', 'Статус не установлен')}")
            
            # Анкета
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"🎂 **ДР:** {info.get('bday', 'Не указано')}")
                st.write(f"📍 **Город:** {info.get('city', 'Не указано')}")
            with col_b:
                st.write(f"💍 **СП:** {info.get('status_rel', 'Не указано')}")
                st.write(f"📧 **E-mail:** {info.get('email', 'Скрыто')}")
            st.write(f"🧩 **Интересы:** {info.get('interests', 'Космос, звезды...')}")

    # Списки Друзей и Подписчиков
    t1, t2, t3 = st.tabs(["👥 Друзья", "📥 Подписчики", "🖼 Галерея"])
    with t1:
        friends = get_friends(target)
        for f in friends: st.button(f"👤 {f}", key=f"fr_{f}", on_click=lambda x=f: setattr(st.session_state, 'viewing_profile', x))
    with t2:
        subs = get_only_followers(target)
        for s in subs: st.button(f"📥 {s}", key=f"sub_{s}")
    with t3:
        st.write("Снимки из последних экспедиций:")
        # Логика галереи: берем картинки из постов пользователя
        posts = requests.get(f"{DB_URL}posts.json").json() or {}
        imgs = [p['img'] for p in posts.values() if p.get('author') == target and p.get('img')]
        if imgs: st.image(imgs[:4], width=150)
        else: st.caption("Галерея пуста")

    # Стена
    st.write("---")
    st.subheader("📝 Стена")
    # Поле публикации
    with st.container(border=True):
        t_wall = st.text_area("Оставить запись...", height=70, label_visibility="collapsed")
        if st.button("Опубликовать"):
            requests.post(f"{DB_URL}posts.json", json={
                "author": target, "creator": st.session_state.username, 
                "text": t_wall, "time": datetime.now().strftime("%H:%M"), "likes": 0
            })
            st.rerun()

    # Вывод постов и комментариев
    posts = requests.get(f"{DB_URL}posts.json").json() or {}
    for pid, p in reversed(list(posts.items())):
        if p.get('author') == target:
            with st.container(border=True):
                st.write(f"**{p['creator']}** <small>{p['time']}</small>", unsafe_allow_html=True)
                st.write(p['text'])
                # Мини-комментарии
                with st.expander("💬 Комментарии"):
                    coms = p.get('comments', {})
                    for c in coms.values():
                        st.markdown(f"**{c['user']}**: {c['txt']}")
                    new_c = st.text_input("Написать ответ...", key=f"c_{pid}")
                    if st.button("Отправить", key=f"b_{pid}"):
                        requests.post(f"{DB_URL}posts/{pid}/comments.json", json={"user": st.session_state.username, "txt": new_c})
                        st.rerun()

# --- СТРАНИЦА НАСТРОЕК (АНКЕТА) ---
elif st.session_state.page == "settings":
    st.title("🛰️ Редактирование анкеты")
    with st.container(border=True):
        st.subheader("Личные данные")
        fn = st.text_input("Имя", value=my_data.get('info', {}).get('f_name', ''))
        ln = st.text_input("Фамилия", value=my_data.get('info', {}).get('l_name', ''))
        bd = st.text_input("Дата рождения (ДД.ММ.ГГГГ)", value=my_data.get('info', {}).get('bday', ''))
        city = st.text_input("Город", value=my_data.get('info', {}).get('city', ''))
        rel = st.selectbox("Семейное положение", ["Не указано", "В активном поиске", "Свободен(а)", "В отношениях", "Влюблен(а)"])
        mail = st.text_input("Эл. почта", value=my_data.get('info', {}).get('email', ''))
        ints = st.text_area("Интересы", value=my_data.get('info', {}).get('interests', ''))
        
        st.subheader("Профиль")
        stat = st.text_input("Статус (краткая фраза)", value=my_data.get('status', ''))
        ava = st.text_input("Ссылка на аватар", value=my_data.get('avatar', DEFAULT_AVA))
        
        if st.button("🚀 Сохранить анкету"):
            info_payload = {
                "f_name": fn, "l_name": ln, "bday": bd, 
                "city": city, "status_rel": rel, "email": mail, "interests": ints
            }
            requests.patch(f"{DB_URL}users/{st.session_state.username}.json", 
                           json={"info": info_payload, "status": stat, "avatar": ava})
            st.success("Данные успешно синхронизированы с базой!")
