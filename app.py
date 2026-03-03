import streamlit as st
import requests
from datetime import datetime

# 1. Настройка страницы (оставляем только базу)
st.set_page_config(
    page_title="Milky Way Online",
    page_icon="🌌",
    layout="centered"
)

# БЛОК С ТЕМНОЙ ТЕМОЙ (st.markdown) МЫ УДАЛИЛИ

# 2. Ссылка на базу
URL_BASE = "https://milky-way-8ea60-default-rtdb.firebaseio.com/posts.json"

st.title("🌌 Млечный Путь: Online")
# ... дальше весь остальной код без изменений