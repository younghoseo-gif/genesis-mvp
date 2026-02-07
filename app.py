import streamlit as st
import google.generativeai as genai
import plotly.graph_objects as go
import time
import random

# ------------------------------------------------------------------
# 1. Page Config
# ------------------------------------------------------------------
st.set_page_config(page_title="Genesis: VC Roast", page_icon="🔥", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; color: #191F28; }
    .stButton>button { width: 100%; background-color: #F04452; color: white; border-radius: 12px; height: 50px; font-weight: 800; font-size: 18px; border: none; }
    .stButton>button:hover { background-color: #D32F2F; }
    .big-title { font-size: 40px; font-weight: 800; color: #191F28; margin-bottom: 0px; }
    .subtitle { font-size: 18px; color: #8B95A1; margin-top: 5px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 2. API Key Setup
# ------------------------------------------------------------------
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("🚨 API Key Error. Please check .streamlit/secrets.toml")
    st.stop()

# ------------------------------------------------------------------
# 3. UI Structure
# ------------------------------------------------------------------
st.markdown('<div class="big-title">Genesis: VC Roast 🔥</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Validate your startup idea with brutal honesty.</div>', unsafe_allow_html=True)

user_input = st.text_area("Pitch your idea", height=150, placeholder="Write in any language...\ne.g., Airbnb for camping spots.")
analyze_btn = st.button("Analyze (Start) 🚀")

# ------------------------------------------------------------------
# 4. Engine Logic (Smart Model Selector)
# ------------------------------------------------------------------
if analyze_btn:
    if not user_input:
        st.warning("Please enter your idea first.")
    else:
        # 로딩 효과
        status_box = st.status("Searching for active AI Brain...", expanded=True)
        progress_bar = status_box.progress(0)
        time.sleep(0.5)

        # [핵심 수정] 사용 가능한 모델 자동 찾기
        try:
            active_model_name = None
            try:
                # 구글 서버에 현재 사용 가능한 모델 목록을 달라고 요청
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # 1.5-flash나 pro가 있으면 그걸 우선 선택
                        if 'flash' in m.name:
                            active_model_name = m.name
                            break
                        elif 'pro' in m.name and active_model_name is None:
                            active_model_name = m.name
                
                if not active_model_name:
                    active_model_name = "models/gemini-pro" # 못 찾으면 기본값 강제 할당
                
                status_box.write(f"🧠 Brain Connected: {active_model_name}")
                progress_bar.progress(30)
                
            except Exception as e:
                # 목록 조회 실패 시 그냥 강제 연결 시도
                active_model_name = "gemini-pro"
                status_box.write("⚠️ Direct Connection Mode")

            # 모델 연결
            model = genai.GenerativeModel(active_model_name)
            
            # 프롬프트 실행
            prompt = f"""
            You are a legendary VC. Name: 'Genesis'.
            [User Input]: "{user_input}"
            [Instructions]:
            1. Language: Reply in the SAME LANGUAGE as Input.
            2. Score: 0-100.
            3. Verdict: Short title.
            4. Analysis: 3 paragraphs brutal feedback.
            5. Format: SCORE|VERDICT|ANALYSIS_TEXT
            """
            
            progress_bar.progress(60)
            status_box.write("🔥 Roasting in progress...")
            
            response = model.generate_content(prompt)
            
            # 결과 처리
            try:
                parts = response.text.split("|")
                if len(parts) >= 3:
                    score = int(parts[0].strip())
                    verdict = parts[1].strip()
                    analysis = parts[2].strip()
                else:
                    score = 50
                    verdict = "Format Error"
                    analysis = response.text
            except:
                score = 0
                verdict = "System Fail"
                analysis = "AI returned an unexpected format."

            progress_bar.progress(100)
            status_box.update(label="Complete!", state="complete", expanded=False)

            # 결과 화면 출력
            st.divider()
            stamp_color = "#F04452" if score < 80 else "#28a745"
            stamp_text = "REJECTED 🔴" if score < 80 else "OFFER 🟢"
            
            st.markdown(f"<h1 style='text-align: center; color: {stamp_color}; border: 3px solid {stamp_color}; display: inline-block; padding: 10px 20px; border-radius: 10px; transform: rotate(-5deg); margin-left: 30%;'>{stamp_text}</h1>", unsafe_allow_html=True)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = score,
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': stamp_color}}
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f"### 📝 {verdict}")
            st.info(analysis)
            
            # 팁 박스
            st.divider()
            st.caption("Treat the AI a coffee to cool down the GPU.")
            st.markdown("""<a href="https://www.buymeacoffee.com" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" style="height: 40px;"></a>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"System Error: {e}")
            st.error("💡 Tip: If 404 error persists, check your API Key in secrets.toml again.")