import streamlit as st
import google.generativeai as genai

# --- Настройки ---
st.set_page_config(page_title="AI Code Assistant", page_icon="🧑‍💻", layout="wide")
st.title("🧑‍💻 AI Code Assistant")
st.caption("Модель: **Gemini 3.8 Flash**")

SYSTEM = "Ты опытный senior разработчик. Отвечай кратко, с примерами кода в markdown."

PROMPTS = {
    "Объяснить код": "Объясни этот код:\n{code}",
    "Исправить ошибку": "Исправь ошибку в коде.\nКод:\n{code}\nОшибка:\n{error}",
    "Сгенерировать тесты": "Напиши тесты ({framework}) для кода:\n{code}"
}

if "history" not in st.session_state:
    st.session_state.history = []

# --- Боковая панель ---
with st.sidebar:
    mode = st.selectbox("Режим", list(PROMPTS.keys()))
    lang = st.text_input("Язык кода", value="python")
    framework = st.text_input("Фреймворк для тестов", value="pytest")
    if st.button("🗑 Очистить историю"):
        st.session_state.history = []
        st.rerun()

# --- Поля ввода ---
code = st.text_area("Код", height=220, placeholder="Вставь код сюда...")

error = ""
if mode == "Исправить ошибку":
    error = st.text_area("Текст ошибки", height=120, placeholder="Вставь traceback...")

# --- Кнопка отправки ---
if st.button("🚀 Отправить", type="primary"):
    if not code.strip():
        st.warning("Вставь код.")
    else:
        prompt = PROMPTS[mode].format(code=code, error=error, framework=framework)
        st.session_state.history.append({"role": "user", "content": prompt})

        st.markdown("### Ответ")
        placeholder = st.empty()
        
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # Используем модель 3.8
            model = genai.GenerativeModel('gemini-3.8-flash')
            
            full_prompt = SYSTEM + "\n\n" + "\n".join([m["content"] for m in st.session_state.history])
            
            # Выводим индикатор загрузки
            with st.spinner("Думаю..."):
                response = model.generate_content(full_prompt)
                placeholder.markdown(response.text)
                st.session_state.history.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            # Если ошибка - выводим её красным
            st.error(f"Ошибка: {e}")

# --- История ---
if st.session_state.history:
    st.divider()
    st.markdown("### История")
    for i, msg in enumerate(st.session_state.history):
        role = "🧑 Ты" if msg["role"] == "user" else "🤖 Ассистент"
        with st.expander(f"{role} · {msg['content'][:60]}..."):
            st.markdown(msg["content"])
