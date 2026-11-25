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
        full = ""
        
        try:
            # Берем ключ из настроек Streamlit
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # Используем актуальную модель
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Собираем историю диалога в один текст
            full_prompt = SYSTEM + "\n\n" + "\n".join([m["content"] for m in st.session_state.history])
            
            # Запрос к модели
            response = model.generate_content(full_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    full += chunk.text
                    placeholder.markdown(full + "▌")
            placeholder.markdown(full)
            
            # Сохраняем ответ в историю
            st.session_state.history.append({"role": "assistant", "content": full})
            
        except Exception as e:
            st.error(f"Ошибка запроса: {e}")

# --- История ---
if st.session_state.history:
    st.divider()
    st.markdown("### История")
    for i, msg in enumerate(st.session_state.history):
        role = "🧑 Ты" if msg["role"] == "user" else "🤖 Ассистент"
        with st.expander(f"{role} · {msg['content'][:60]}..."):
            st.markdown(msg["content"])
