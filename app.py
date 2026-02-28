import streamlit as st
import requests
import os
import uuid

st.set_page_config(page_title="ИИ-Бот (GigaChat)", page_icon="🤖")
st.title("🤖 Школьный ИИ-Бот на GigaChat")

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

# === Получение access_token ===
def get_access_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Authorization": f"Basic {AUTH_KEY}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"scope": "GIGACHAT_API_PERS"}

    response = requests.post(url, headers=headers, data=data, verify=False)
    response.raise_for_status()
    return response.json()["access_token"]

# === Запрос к GigaChat ===
def ask_gigachat(messages, access_token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "GigaChat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500,
    }

    response = requests.post(url, headers=headers, json=payload, verify=False)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# === Интерфейс ===
with st.sidebar:
    st.header("Настройки")
    system_prompt = st.text_area(
        "Системная инструкция",
        "Ты полезный школьный помощник. Объясняй понятно и структурировано.",
    )

# 1) Обновлять system-сообщение при изменении поля
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
else:
    # гарантируем, что 0-й элемент — system и он актуален
    if st.session_state.messages and st.session_state.messages[0].get("role") == "system":
        st.session_state.messages[0]["content"] = system_prompt
    else:
        st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})

# ВСТАВИТЬ отладочный вывод (как просил)
st.sidebar.write("SYSTEM (реально в истории):", st.session_state.messages[0]["content"])

# 2) Кнопка “Очистить чат”
if st.sidebar.button("Очистить чат"):
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.rerun()

# Отображение истории (без system)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

prompt = st.chat_input("Напиши вопрос...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        token = get_access_token()
        reply = ask_gigachat(st.session_state.messages, token)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    except Exception as e:
        st.error(f"Ошибка: {e}")
