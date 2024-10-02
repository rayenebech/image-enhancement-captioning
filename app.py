import sys
import json
import torch
import warnings
import numpy as np
import streamlit as st
from PIL import Image


from model import VLMModel
from helpers import read_config, parse_data

config = read_config()
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Teknofest-Trendyol Hackathon",
    page_icon="🚀",
    layout= "wide",
    )

def generate_image(prompt, image):
    return image

def reset():
    output_image_placeholder.empty()
    input_image_placeholder.empty()
    title_placeholder.empty()
    title_placeholder_text.empty()
    desc_placeholder.empty()
    desc_placeholder_text.empty()
    st.session_state["file_key"] += 1
    image_enhanced = None
    image_path = None

model = VLMModel(model_id = config["model"]["model_id"])

st.title("Teknofest-Trendyol Hackathon - Cogitators ✨")

if 'button_pressed' not in st.session_state:
        st.session_state.button_pressed = False
        
if 'image_generated' not in st.session_state:
        st.session_state.image_generated = False

if "file_key" not in st.session_state:
    st.session_state["file_key"] = 0
    
with st.container():  #container for the text 
    col1, col2 = st.columns(2)
    with col1: 
        user_desc = st.text_input("Lütfen, ürün açıklaması buraya yazın.", key= "input")
        prompt  = config["prompt"] + f"\n prompt: {user_desc}"
        image_path = st.file_uploader("Ürün foroğrafı buraya yükleyin", type=["png","jpg","bmp","jpeg"], key=st.session_state["file_key"])
        if image_path is not None:
            image =Image.open(image_path)
        col5, col6 = st.columns(2)
        with col5:
            button = st.button("Başla 🚀", disabled=st.session_state.button_pressed, use_container_width= True)
        with col6:
            clear =  st.button("Temizle 🗑️", use_container_width= True, on_click=reset)
                
    with col2:
        if button:  
            if image_path is not None:
                st.session_state.button_pressed = True
                with st.spinner("Lütfen bekleyin.. Şuan yapay zeka sizin için çalışıyor 💫"):
                    description = model.generate(prompt, image)
                    entity_name = description
                    data = parse_data(description)
                    if isinstance(data, dict):
                        entity_name = data.get("entity_name", "")
                        product_title = data.get("product_title", "")
                        product_description = data.get("product_description", description)
                        print("entity_name is ", entity_name)
                        title_placeholder = st.empty()
                        title_placeholder.subheader("Ürün Başlığı")
                        title_placeholder_text = st.empty()
                        title_placeholder_text.code(product_title, language="markdown")
                        desc_placeholder = st.empty()
                        desc_placeholder.subheader("Ürün Açıklaması")
                        desc_placeholder_text = st.empty()
                        desc_placeholder_text.code(product_description, language="markdown")
                    else:
                        desc_placeholder_text = st.empty()
                        desc_placeholder.subheader("Üretilen Veri")
                        desc_placeholder_text.code(description, language="markdown")
                    st.session_state.button_pressed = False
                    try:
                        image_enhanced = generate_image(entity_name, image) 
                        st.session_state.image_generated = True
                    except Exception as e:
                        print("An error happened when enhancing the image: ", e)
                    
        else:
            st.warning('⚠ Please upload your Image!')



with st.container(): #container for the images
    col3, col4 = st.columns(2)
    with col3:
        if image_path is not None:
            input_image_placeholder = st.empty()
            input_image = input_image_placeholder.image(image, caption="Uploaded Image", use_column_width=True)
    with col4: 
        try:
            if st.session_state.image_generated and image_enhanced:
                output_image_placeholder = st.empty()
                output_image = output_image_placeholder.image(image_enhanced, caption="Enhanced Image", use_column_width=True)
        except Exception as e:
            print(e)
    