import streamlit as st

st.title("버튼 누르면 스크립트 전체 다시 실행")

# if "clicks" not in st.session_state:  
clicks = 0

if st.button(' 클릭 '):
    clicks +=1
    st.balloons()

st.write(f"풍선 발사 {clicks}회")