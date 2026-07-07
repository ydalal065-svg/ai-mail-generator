import streamlit as st

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="AI Mail Generator",
    page_icon="✉️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Provider / Model config
# ----------------------------
PROVIDER_MODELS = {
    "Claude (Anthropic)": ["claude-sonnet-5", "claude-opus-4-8", "claude-haiku-4-5-20251001"],
    "Gemini (Google)": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
    "Groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
}

# ----------------------------
# Sidebar - Provider, API Key & Settings
# ----------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    provider = st.selectbox(
        "AI Provider",
        list(PROVIDER_MODELS.keys()),
        help="Kaunsi AI service use karni hai",
    )

    model_choice = st.selectbox(
        "Model",
        PROVIDER_MODELS[provider],
        help="Provider ke andar kaunsa model use karna hai",
    )

    if provider == "Claude (Anthropic)":
        api_key = st.text_input(
            "Anthropic API Key", type="password",
            help="Apni Anthropic API key yahan daalein (console.anthropic.com se milegi)"
        )
    elif provider == "Gemini (Google)":
        api_key = st.text_input(
            "Google AI (Gemini) API Key", type="password",
            help="Apni Gemini API key yahan daalein (aistudio.google.com se milegi)"
        )
    else:  # Groq
        api_key = st.text_input(
            "Groq API Key", type="password",
            help="Apni Groq API key yahan daalein (console.groq.com se milegi)"
        )

    st.divider()
    st.subheader("🎨 About")
    st.write(
        "Yeh app AI ki madad se professional aur attractive emails "
        "generate karta hai — sirf details bharo aur ek click me email tayyar! "
        "Claude, Gemini aur Groq — teeno providers support karte hain."
    )
    st.divider()
    st.caption("Made with ❤️ using Streamlit")

# ----------------------------
# Header
# ----------------------------
st.title("✉️ AI Mail Generator")
st.caption("Seconds mein professional email likhwao — AI ke sath!")

# ----------------------------
# Input Form
# ----------------------------
col1, col2 = st.columns(2)
with col1:
    recipient = st.text_input("👤 Recipient Name", placeholder="e.g. Mr. Sharma")

with col2:
    tone = st.selectbox(
        "🗣️ Tone",
        ["Professional", "Formal", "Friendly", "Persuasive", "Apologetic", "Casual"],
    )

purpose = st.text_input(
    "📌 Email Purpose / Subject",
    placeholder="e.g. Leave application, Job follow-up, Meeting request",
)

key_points = st.text_area(
    "📝 Key Points (bullet ya sentence me likhein)",
    placeholder="e.g. 2 din ki chutti chahiye, wajah - family function, 15th se 16th tak",
    height=120,
)

col3, col4 = st.columns(2)
with col3:
    language = st.selectbox("🌐 Language", ["English", "Hindi", "Hinglish (Roman Hindi)"])
with col4:
    length = st.selectbox("📏 Length", ["Short", "Medium", "Detailed"])

st.write("")
generate_clicked = st.button("✨ Generate Email", use_container_width=True, type="primary")

# ----------------------------
# Prompt builder
# ----------------------------
def build_prompt():
    return f"""You are a professional email writing assistant.
Write a {tone.lower()} email in {language} with a {length.lower()} length.

Recipient: {recipient if recipient else "Concerned Person"}
Purpose / Subject: {purpose}
Key points to include: {key_points}

Rules:
- Include a proper subject line at the top (Subject: ...)
- Include a greeting, body, and a polite closing with a placeholder sender name like [Your Name]
- Keep formatting clean and ready to copy-paste
- Do not add any explanation, only output the email itself
"""

# ----------------------------
# Provider-specific call functions
# ----------------------------
def call_claude(key, model, prompt):
    from anthropic import Anthropic
    client = Anthropic(api_key=key)
    response = client.messages.create(
        model=model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    return "\n".join(parts).strip()


def call_gemini(key, model, prompt):
    import google.generativeai as genai
    genai.configure(api_key=key)
    gen_model = genai.GenerativeModel(model)
    response = gen_model.generate_content(prompt)
    return (response.text or "").strip()


def call_groq(key, model, prompt):
    from groq import Groq
    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return (response.choices[0].message.content or "").strip()


PROVIDER_DISPATCH = {
    "Claude (Anthropic)": call_claude,
    "Gemini (Google)": call_gemini,
    "Groq": call_groq,
}

PROVIDER_PACKAGE = {
    "Claude (Anthropic)": "anthropic",
    "Gemini (Google)": "google-generativeai",
    "Groq": "groq",
}

# ----------------------------
# Generation Logic
# ----------------------------
if generate_clicked:
    if not api_key:
        st.error(f"⚠️ Pehle sidebar me apni {provider} API key daalein.")
    elif not purpose or not key_points:
        st.warning("⚠️ Kripya Purpose aur Key Points zaroor bharein.")
    else:
        try:
            with st.spinner("AI aapke liye email likh raha hai... ✍️"):
                call_fn = PROVIDER_DISPATCH[provider]
                email_text = call_fn(api_key, model_choice, build_prompt())

            if not email_text:
                st.warning("⚠️ AI se khaali response mila. Dobara try karein.")
            else:
                st.subheader("📩 Generated Email")
                st.text_area("Output", value=email_text, height=320, label_visibility="collapsed")
                st.download_button(
                    "⬇️ Download as .txt",
                    data=email_text,
                    file_name="generated_email.txt",
                    mime="text/plain",
                )

        except ModuleNotFoundError:
            pkg = PROVIDER_PACKAGE[provider]
            st.error(
                f"❌ '{pkg}' package install nahi hai. Terminal me yeh chalayein:\n\n"
                f"pip install {pkg}"
            )
        except Exception as e:
            st.error(f"❌ Kuch error aayi ({provider}): {e}")

st.divider()
st.caption("Powered by Claude, Gemini & Groq • Built with Streamlit")