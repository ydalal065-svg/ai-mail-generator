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
# Sidebar - About only
# ----------------------------
with st.sidebar:
    st.header("🎨 About")
    st.write(
        "Yeh app AI ki madad se professional aur attractive emails "
        "generate karta hai — sirf details bharo aur ek click me email tayyar!"
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
# Generation Logic (Groq only - hidden from user)
# ----------------------------
if generate_clicked:
    if not purpose or not key_points:
        st.warning("⚠️ Kripya Purpose aur Key Points zaroor bharein.")
    else:
        try:
            with st.spinner("AI aapke liye email likh raha hai... ✍️"):
                from groq import Groq
                client = Groq(api_key=st.secrets["api_keys"]["Groq"])
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=800,
                    messages=[{"role": "user", "content": build_prompt()}],
                )
                email_text = (response.choices[0].message.content or "").strip()

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
            st.error("❌ 'groq' package install nahi hai. Terminal me yeh chalayein:\n\npip install groq")
        except Exception as e:
            st.error(f"❌ Kuch error aayi: {e}")

st.divider()
st.caption("Built with Streamlit")
