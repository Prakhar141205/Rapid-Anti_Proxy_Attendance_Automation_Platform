import streamlit as st


def footer_home():

    logo_url = "https://i.ibb.co/4r5X1FY/apnacollege.png"
    
    st.markdown(f"""
        <div style="
            margin-top: 2rem;
            display: flex;
            gap: 6px;
            justify-content: center;
            align-items: center;
        ">
            <p style="font-weight: bold; color: white; margin: 0;">
                Created with &#10084;&#65039;
            </p>
            <img src="{logo_url}" style="height: 25px;">
        </div>
                    """, unsafe_allow_html=True)
    

def footer_dashboard():

    logo_url = "https://i.ibb.co/4r5X1FY/apnacollege.png"
    
    st.markdown(f"""
        <div style="
            margin-top: 2rem;
            display: flex;
            gap: 6px;
            justify-content: center;
            align-items: center;
        ">
            <p style="font-weight: bold; color: black; margin: 0;">
                Created with &#10084;&#65039;
            </p>
            <img src="{logo_url}" style="height: 25px;">
        </div>
                    """, unsafe_allow_html=True)