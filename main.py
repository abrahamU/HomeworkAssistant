import streamlit as st
import json
import openai
from datetime import datetime
from openai import OpenAI
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import homeworkwriter

st.set_page_config(page_title="Home Work Writer", layout="wide", initial_sidebar_state="auto")

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login('Login', 'main')

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main', key='unique_key')
    st.title(f'欢迎 *{st.session_state["name"]}*，如果是第一次使用，请修改您的初始密码😀')
    try:
        if authenticator.reset_password(st.session_state["username"], 'Change password'):
            st.success('Password modified successfully')
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)
    
    #=====================================================================Running code here===================
    homeworkwriter.run()
    #=========================================================================================================
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')

