import streamlit as st
import edge_tts
import asyncio
import io

# 페이지 기본 설정
st.set_page_config(page_title="고속 AI 성우", page_icon="⚡")

st.title("⚡ 고속 AI 텍스트-음성 변환기")
st.markdown("""
<style>
    .stTextArea textarea { font-size: 16px; }
</style>
""", unsafe_allow_html=True)
st.caption("Microsoft Edge의 신경망 엔진을 사용하여 빠르고 자연스럽습니다.")

# --- 사이드바 설정 (음성 옵션) ---
with st.sidebar:
    st.header("🔊 음성 설정")
    
    # 성별/성우 선택
    voice_option = st.selectbox(
        "목소리 선택",
        options=["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"],
        format_func=lambda x: "여성 (선희)" if "SunHi" in x else "남성 (인준)"
    )
    
    # 속도 조절 (기본값 +30% = 1.3배속)
    speed_rate = st.slider(
        "말하기 속도", 
        min_value=0.5, 
        max_value=2.0, 
        value=1.3, 
        step=0.1,
        help="1.0이 기본 속도입니다. 1.3은 1.3배속입니다."
    )
    
    # edge-tts는 퍼센트 문자열로 속도를 받음 (예: +30%)
    rate_str = f"{int((speed_rate - 1.0) * 100):+d}%"

# --- 메인 기능 ---
with st.form("tts_form"):
    text_input = st.text_area(
        "텍스트 입력",
        height=150,
        placeholder="변환할 내용을 입력하세요."
    )
    submit_button = st.form_submit_button("즉시 변환 (Enter)")

# 비동기 함수: 음성 생성 로직
async def generate_audio(text, voice, rate):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    # 메모리 버퍼 생성
    audio_data = io.BytesIO()
    # 스트림으로 데이터를 받아 바로 메모리에 씀 (속도 최적화)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
    
    audio_data.seek(0)
    return audio_data

# 변환 실행
if submit_button:
    if not text_input.strip():
        st.warning("텍스트를 입력해주세요.")
    else:
        try:
            with st.spinner("⚡ 초고속 변환 중..."):
                # 비동기 함수 실행
                mp3_fp = asyncio.run(generate_audio(text_input, voice_option, rate_str))
                
                # 오디오 플레이어
                st.audio(mp3_fp, format='audio/mp3')
                
                # 다운로드 버튼
                st.download_button(
                    label="MP3 다운로드",
                    data=mp3_fp,
                    file_name="speed_tts_output.mp3",
                    mime="audio/mp3"
                )
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

