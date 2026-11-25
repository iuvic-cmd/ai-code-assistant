import streamlit as st
from llm import stream_chat, MODEL
from prompts import SYSTEM, PROMPTS

st.set_page_config(page_title="AI Code Assistant", page_icon="🧑‍💻", layout="wide")
st.title("🧑‍💻 AI Code Assistant")
st.caption(f"Модель: **{MODEL}**")

if "history" not in st.session_state:
    st.session_state.history = []
if "feedback" not in st.session_state:
    st.session_state.feedback = []

with st.sidebar:
    mode = st.selectbox("Режим", list(PROMPTS.keys()))
    lang = st.text_input("Язык кода", value="python")
    framework = st.text_input("Фреймворк для тестов", value="pytest")
    if st.button("🗑 Очистить историю"):
        st.session_state.history = []
        st.session_state.feedback = []
        st.rerun()

code = st.text_area("Код", height=220, placeholder="Вставь код сюда...")
error = ""
if mode == "Исправить ошибку":
    error = st.text_area("Текст ошибки", height=120, placeholder="Вставь traceback...")

if st.button("🚀 Отправить", type="primary"):
    if not code.strip():
        st.warning("Вставь код.")
    else:
        prompt = PROMPTS[mode].format(
            code=code, error=error, lang=lang, framework=framework
        )
        st.session_state.history.append({"role": "user", "content": prompt})

        st.markdown("### Ответ")
        placeholder = st.empty()
        full = ""
        try:
            for token in stream_chat(SYSTEM, st.session_state.history):
                full += token
                placeholder.markdown(full + "▌")
            placeholder.markdown(full)
            st.session_state.history.append({"role": "assistant", "content": full})
        except Exception as e:
            st.error(f"Ошибка запроса к модели: {e}")

if st.session_state.history:
    st.divider()
    st.markdown("### История")
    for i, msg in enumerate(st.session_state.history):
        role = "🧑 Ты" if msg["role"] == "user" else "🤖 Ассистент"
        with st.expander(f"{role} · {msg['content'][:60]}..."):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                c1, c2 = st.columns([1, 1])
                if c1.button("👍", key=f"up{i}"):
                    st.session_state.feedback.append({"msg_index": i, "vote": "up"})
                    st.toast("Спасибо! Сохранено как удачный пример.")
                if c2.button("👎", key=f"down{i}"):
                    st.session_state.feedback.append({"msg_index": i, "vote": "down"})
                    st.toast("Понял, учту.")
