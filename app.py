import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import requests

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

# -----------------------------
# IMAGE GENERATOR (WORKING)
# -----------------------------
def generate_image(prompt):
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}"
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        return image
    except:
        return None

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="AI Comic Generator", layout="wide")
st.title("🎨 AI Comic Generator (With Images)")
st.caption("Generate comic stories with visuals")

# -----------------------------
# INPUTS
# -----------------------------
idea = st.text_area("💡 Enter your comic idea", height=120)

genre = st.selectbox("🎭 Genre", [
    "Funny", "Motivational", "Romantic", "Dark", "Adventure"
])

characters = st.text_input("👥 Characters (comma separated)")
panels = st.slider("🖼️ Number of Panels", 3, 5, 3)

# -----------------------------
# GENERATE COMIC
# -----------------------------
if st.button("🚀 Generate Comic"):

    if not idea.strip():
        st.warning("⚠️ Please enter a story idea")
        st.stop()

    with st.spinner("🧠 Generating comic story..."):

        # STEP 1: Generate comic script
        prompt = f"""
        Create a {panels}-panel comic.

        Idea: {idea}
        Genre: {genre}
        Characters: {characters}

        Format STRICTLY like:

        Panel 1:
        Scene: ...
        Dialogue: ...

        Panel 2:
        Scene: ...
        Dialogue: ...
        """

        response = model.generate_content(prompt)
        comic_script = response.text

        st.subheader("📖 Comic Story")
        st.write(comic_script)

        # STEP 2: Extract scenes
        scenes = []
        dialogues = []

        for line in comic_script.split("\n"):
            if line.strip().startswith("Scene:"):
                scenes.append(line.replace("Scene:", "").strip())
            if line.strip().startswith("Dialogue:"):
                dialogues.append(line.replace("Dialogue:", "").strip())

        # -----------------------------
        # GENERATE IMAGES
        # -----------------------------
        st.subheader("🖼️ Comic Panels")

        for i in range(len(scenes)):
            st.markdown(f"### Panel {i+1}")

            col1, col2 = st.columns([2, 1])

            with col1:
                image_prompt = f"comic style illustration, {scenes[i]}, {genre}, colorful, expressive characters"
                image = generate_image(image_prompt)

                if image:
                    st.image(image, use_column_width=True)
                else:
                    st.warning("⚠️ Image generation failed")

            with col2:
                st.write(f"📝 **Scene:** {scenes[i]}")
                if i < len(dialogues):
                    st.success(f"💬 {dialogues[i]}")

        # -----------------------------
        # DOWNLOAD
        # -----------------------------
        st.download_button(
            "📥 Download Comic Script",
            data=comic_script,
            file_name="comic.txt"
        )