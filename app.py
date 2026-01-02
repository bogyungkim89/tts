import streamlit as st
from gtts import gTTS
import io

# 페이지 기본 설정
st.set_page_config(page_title="텍스트 음성 변환기", page_icon="🎙️")

st.title("🎙️ AI 텍스트-음성 변환기 (TTS)")
st.caption("Google Text-to-Speech를 활용하여 텍스트를 음성으로 변환합니다.")

# 1. 입력 영역
with st.form("tts_form"):
    text_input = st.text_area(
        "변환할 텍스트를 입력하세요:",
        height=150,
        placeholder="여기에 내용을 입력하면 음성으로 읽어줍니다."
    )
    
    # 옵션 설정 (사이드바 혹은 폼 내부)
    col1, col2 = st.columns(2)
    with col1:
        lang_option = st.selectbox("언어 선택", ["한국어 (ko)", "영어 (en)", "일본어 (ja)"])
        lang_code = lang_option.split("(")[1].replace(")", "") # ko, en, ja 추출
    
    with col2:
        # gTTS는 속도 조절이 제한적(slow=True/False)입니다.
        is_slow = st.checkbox("느리게 읽기")

    submit_button = st.form_submit_button("음성 변환하기")

# 2. 변환 로직
if submit_button:
    if text_input.strip() == "":
        st.warning("텍스트를 입력해주세요!")
    else:
        with st.spinner("음성을 생성하는 중입니다..."):
            try:
                # gTTS 객체 생성
                tts = gTTS(text=text_input, lang=lang_code, slow=is_slow)
                
                # 파일을 디스크에 저장하지 않고 메모리(BytesIO)에 저장 (클라우드 환경 최적화)
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0) # 파일 포인터를 처음으로 이동
                
                # 3. 오디오 출력
                st.success("변환 완료!")
                st.audio(mp3_fp, format='audio/mp3')
                
                # 다운로드 버튼 제공
                st.download_button(
                    label="MP3 다운로드",
                    data=mp3_fp,
                    file_name="tts_output.mp3",
                    mime="audio/mp3"
                )
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
