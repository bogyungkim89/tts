import streamlit as st
import edge_tts
import asyncio
import io

# 페이지 설정
st.set_page_config(page_title="무제한급 AI 성우", page_icon="🎙️")

st.title("🎙️ 고속 AI 성우 (대용량 안정화 버전)")
st.info("💡 아주 긴 글은 변환에 시간이 걸립니다. 완료될 때까지 브라우저를 닫지 마세요.")

# --- 사이드바 설정 ---
with st.sidebar:
    st.header("⚙️ 설정")
    voice_option = st.selectbox(
        "목소리 선택",
        options=["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"],
        format_func=lambda x: "여성 (선희)" if "SunHi" in x else "남성 (인준)"
    )
    
    speed_rate = st.slider(
        "말하기 속도", min_value=0.5, max_value=2.0, value=1.3, step=0.1
    )
    rate_str = f"{int((speed_rate - 1.0) * 100):+d}%"

# --- 메인 기능 ---
with st.form("tts_form"):
    text_input = st.text_area(
        "텍스트 입력",
        height=300,
        placeholder="소설, 논문 등 매우 긴 텍스트를 입력하세요. 자동으로 나누어 처리합니다."
    )
    submit_button = st.form_submit_button("대용량 변환 시작")

# 텍스트 분할 함수 (안정성을 위해 1000자 단위로 축소)
def split_text(text, max_length=1000):
    chunks = []
    current_chunk = ""
    sentences = text.split('.') # 문장 단위로 분리
    
    for sentence in sentences:
        if not sentence.strip():
            continue
        sentence = sentence + "."
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# 핵심: 재시도 로직이 포함된 음성 생성 함수
async def generate_audio_stream(text_chunks, voice, rate):
    combined_audio = io.BytesIO()
    total_chunks = len(text_chunks)
    
    # 진행률 표시바 및 상태 메시지
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, chunk in enumerate(text_chunks):
        status_text.text(f"진행 중: {i+1} / {total_chunks} 구간 변환 중...")
        
        retry_count = 0
        max_retries = 3
        success = False
        
        while not success and retry_count < max_retries:
            try:
                communicate = edge_tts.Communicate(chunk, voice, rate=rate)
                async for item in communicate.stream():
                    if item["type"] == "audio":
                        combined_audio.write(item["data"])
                success = True
                
            except Exception as e:
                retry_count += 1
                status_text.warning(f"구간 {i+1} 오류 발생. 2초 후 재시도합니다... ({retry_count}/{max_retries})")
                await asyncio.sleep(2) # 오류 시 2초 대기
        
        if not success:
            st.error(f"구간 {i+1} 변환에 실패했습니다. 너무 긴 문장이 있거나 서버 문제입니다.")
            return None

        # [중요] 서버 차단 방지를 위한 휴식 (0.5초)
        # 긴 글일수록 이 딜레이가 중요합니다.
        await asyncio.sleep(0.5)
        
        # 진행률 업데이트
        progress_bar.progress((i + 1) / total_chunks)
        
    combined_audio.seek(0)
    status_text.text("✅ 모든 변환이 완료되었습니다!")
    return combined_audio

# 실행 로직
if submit_button:
    if not text_input.strip():
        st.warning("내용을 입력해주세요.")
    else:
        # 비동기 실행을 위한 루프 생성
        try:
            chunks = split_text(text_input)
            st.write(f"총 {len(chunks)}개 구간으로 나누어 작업을 시작합니다. (예상 소요시간: {len(chunks)*2}초 내외)")
            
            mp3_fp = asyncio.run(generate_audio_stream(chunks, voice_option, rate_str))
            
            if mp3_fp:
                st.audio(mp3_fp, format='audio/mp3')
                st.download_button(
                    label="📂 전체 MP3 다운로드",
                    data=mp3_fp,
                    file_name="unlimited_tts.mp3",
                    mime="audio/mp3"
                )
        except Exception as e:
            st.error(f"예기치 못한 오류: {e}")
