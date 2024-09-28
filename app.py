import sys
import json
import torch
import warnings
import numpy as np
import streamlit as st
from PIL import Image


from model import VLMModel
from helpers import read_config

config = read_config()
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Teknofest-Trendyol Hackathon",
    page_icon="🚀",
    layout= "wide",
    )


model = VLMModel(model_id = config["model"]["model_id"])

st.title("Teknofest-Trendyol Hackathon - Cogigators ✨")
# st.info(' Let me help generate segments for any of your images. 😉')

image_path = st.file_uploader("Upload Image 🚀", type=["png","jpg","bmp","jpeg"])
user_desc = st.text_input("Image Descrption","700 gram kuşburnu marmelat yüzde yüz dogal açtıktan sonra dolaba koyun")
prompt  = f"""Verilen cümle ve resimden önemli bilgileri çıkararak bir ürün başlığı ve açıklaması yaz. E-ticaret sitesinde paylş
Verilen cümle:  {user_desc}
1- Ürün adı, marka ve diğer önemli özellikleri yansıtan net ve öz bir ürün başlığı yazın.
2- Açıklama kısa olmalı ve temel ürün bilgilerini (boyut, renk, malzeme, ağırlık), kullanım talimatlarını, depolama bilgilerini ve varsa diğer bilgileri içermelidir.
Çıktıyı bu formatta yaz:
###Başlık:
###Açıklama:"""

if 'button_pressed' not in st.session_state:
        st.session_state.button_pressed = False
        
if st.button("Generate Description", disabled=st.session_state.button_pressed):        
    if image_path is not None:
        st.session_state.button_pressed = True
        with st.spinner("Working.. 💫"):
            image =Image.open(image_path)
            col1, col2 = st.columns(2)
            with col1: 
                st.image(image, caption="Uploaded Image", use_column_width=False)
            with col2:
                description = model.generate(prompt, image)
                st.image(image, caption="Enhanced Image", use_column_width=False)
                st.code(description, language="markdown")
             # Reset the button press state after processing
        st.session_state.button_pressed = False
else:
    st.warning('⚠ Please upload your Image!')

