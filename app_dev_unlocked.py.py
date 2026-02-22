import streamlit as st
import google.generativeai as genai
import time
import urllib.parse
import random
import re

# ------------------------------------------------------------------
# 1. Page Config & 철벽 테마 방어
# ------------------------------------------------------------------
# [이름 변경] 브라우저 탭 타이틀 변경
st.set_page_config(page_title="Validatix MVP", page_icon="🔥", layout="centered")

# [🔥 실전 배포를 위한 개발자 모드 OFF (결제창 철벽 가동) 🔥]
dev_mode = False 

KAKAO_LINK = "https://bit.ly/3MavCUX"
BMC_LINK = "https://bit.ly/4rpRfQw"

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Pretendard:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0E1117 !important;
        color: #E0E0E0 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    /* 텍스트 쪼개짐 방지 및 기본 색상 */
    p, li, div, th, td, span {
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
        color: #E0E0E0 !important;
    }

    h1, h1 * { font-family: 'JetBrains Mono', monospace !important; color: #00FFD1 !important; }
    
    h2 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 40px !important; }
    h2, h2 * { color: #FFFFFF !important; }
    
    h3 { margin-top: 30px !important; margin-bottom: 15px !important; font-size: 22px !important; font-weight: 800 !important; line-height: 1.4 !important; } 
    h3, h3 * { color: #00FFD1 !important; } 

    h4 { margin-top: 25px !important; margin-bottom: 12px !important; font-size: 20px !important; font-weight: 800 !important; line-height: 1.4 !important; } 
    h4, h4 * { color: #00FFD1 !important; }

    /* 본문 줄 간격을 1.45로 줄여서 쫀쫀하게 수정 */
    p, li { line-height: 1.45 !important; font-size: 16px; margin-bottom: 15px; }
    
    /* 표 가로 폭 100% 꽉 채우기 */
    table { width: 100% !important; border-collapse: collapse !important; margin-bottom: 20px !important; }
    th { background-color: #21262D !important; color: #00FFD1 !important; font-size: 16px !important; text-align: left !important; padding: 12px !important; border-bottom: 2px solid #444 !important; }
    td { font-size: 15px !important; padding: 15px 12px !important; border-bottom: 1px solid #333 !important; vertical-align: top !important; line-height: 1.6 !important; }

    /* 버튼 및 텍스트 박스 보호색 방어 */
    div.stButton > button { width: 100%; border-radius: 8px; height: 55px; font-weight: 800; font-size: 18px; border: none; transition: all 0.3s ease; font-family: 'JetBrains Mono', monospace; }
    div.stButton > button:active { transform: scale(0.98); }
    .primary-btn button { background: linear-gradient(90deg, #FF4B4B 0%, #FF9068 100%); color: white !important; }
    .secondary-btn button { background-color: #21262D; color: #00FFD1 !important; border: 1px solid #30363D; }

    /* 점수 전용 클래스를 만들어 글로벌 CSS 강제 덮어쓰기 */
    .score-red { color: #FF4B4B !important; }
    .score-green { color: #00FFD1 !important; }

    .score-card { text-align: center; padding: 30px; border-radius: 20px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 30px; }

    .final-gatekeeper-box { width: 100%; text-align: center; padding: 40px 20px; background: linear-gradient(180deg, rgba(20,20,20,1) 0%, rgba(10,10,10,1) 100%); border: 2px solid #F04452; border-radius: 16px; box-shadow: 0 10px 30px rgba(240, 68, 82, 0.15); margin-top: 20px; margin-bottom: 30px; position: relative; z-index: 100; }
    .final-blur-content { filter: blur(8px); opacity: 0.2; pointer-events: none; user-select: none; }
    </style>
""", unsafe_allow_html=True)

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("🚨 API Key Error. secrets.toml 파일을 확인하세요.")
    st.stop()

# ------------------------------------------------------------------
# 2. Data Decks
# ------------------------------------------------------------------
KR_IDEAS = [
    "헤어진 연인 사진 속 얼굴만 자연스럽게 지워주는 AI", "층간소음 발생 시 윗집 스피커 해킹하는 복수 앱", "주식 폭락할 때마다 욕해주는 위로 AI", "직장 상사 잔소리를 클래식 음악으로 변환하는 이어폰", "헬스장 안 가면 등록비가 자동으로 기부되는 시계",
    "내 장례식 플레이리스트 미리 짜주는 서비스", "소개팅 망했을 때 탈출용 가짜 전화 걸어주는 앱", "다이어트 실패하면 배달앱 자동 차단하는 공유기", "반려견 짖는 소리 번역해서 카톡으로 보내주는 목걸이", "매일 아침 팩트 폭력으로 깨워주는 알람 시계",
    "술 마시고 전 애인에게 연락하면 자동 결제되는 벌금 앱", "조별과제 무임승차자 자동 박제 시스템", "헬스장 거울 셀카 점수 매겨주는 AI", "내 코골이 소리로 작곡해주는 수면 앱", "중고거래 사기꾼 잡으면 현상금 주는 플랫폼",
    "비건을 위한 고기 맛 나는 채소 프린터", "넷플릭스 증후군 치료 (볼 거 고르다 잠드는 사람 추천)", "코인 떡락하면 자동으로 한강 수온 알려주는 앱", "MBTI 궁합 안 맞으면 매칭 아예 안 해주는 소개팅 앱", "자소서 복붙하면 합격 확률 알려주는 취업 AI",
    "상사 몰래 딴짓할 때 화면 자동으로 엑셀로 바꿔주는 센서", "내가 싼 똥 사진 찍으면 건강 상태 분석해주는 변기", "결혼식 축의금 얼마 낼지 계산해주는 눈치 계산기", "노래방에서 삑사리 나면 자동으로 오토튠 걸어주는 마이크", "라면 물 조절 실패하면 욕해주는 스마트 냄비",
    "지하철 빈자리 찾아서 내비게이션 해주는 AR 안경", "싫어하는 사람 인형 만들어주는 부두술 쇼핑몰", "내 목소리 100% 똑같이 흉내내서 전화 받아주는 AI 비서", "탈모 진행률 예측해서 가발 미리 추천해주는 앱", "밤새 넷플릭스 보면 다음날 연차 사유서 써주는 AI",
    "고양이 털 모아서 니트 짜주는 재활용 서비스", "PC방 알바생 대신 라면 끓여주는 로봇 팔", "화장 지우기 귀찮을 때 얼굴 핥아서 씻겨주는 로봇 강아지", "헤어진 연인 선물 중고가 견적 내주는 카메라", "코딩하다 에러 나면 대신 키보드 샷건 쳐주는 기계",
    "내 얼굴 합성해서 헐리우드 영화 주인공 만들어주는 딥페이크 OTT", "맛집 웨이팅 대신 서주는 알바 매칭 플랫폼", "집 나간 멘탈 찾아주는 명상 VR", "로또 번호 꿈에서 본 거 해석해주는 해몽 AI", "친구들이랑 여행 가서 정산 안 하는 놈 자동 고발 앱",
    "내가 쓴 악플 다 지워주는 디지털 세탁소", "보이스피싱범이랑 AI가 대신 싸워주는 통화 앱", "공포영화 볼 때 무서운 장면 1초 전에 가려주는 안경", "내 통장 잔고 보면 한숨 쉬어주는 가계부", "미용실에서 말 걸면 경고음 울리는 의자",
    "소개팅 상대방 인스타 분석해서 '거를 타선' 알려주는 AI", "밤길 무서울 때 드론이 따라오면서 경호해주는 서비스", "중고차 허위매물인지 딜러 눈동자 흔들림으로 감지하는 앱", "배달 음식 늦게 오면 배달비 따블로 환불받는 보험", "게임 트롤러 만나면 현피 주선해주는 매칭 시스템",
    "짝사랑 성공 확률 계산해주는 시뮬레이션 게임", "내 묘비명 미리 공모전 여는 플랫폼", "월요일 아침마다 '회사 망해라' 기도해주는 챗봇", "길거리 붕어빵 트럭 위치 실시간 추적 지도", "노트북 발열로 계란 후라이 해먹는 키트",
    "내 전생 체험시켜주는 최면 VR", "반려 식물 죽으면 장례 치러주는 화분", "안 씻고 출근해도 씻은 척 냄새 덮어주는 향수", "회의 시간에 멍 때려도 고개 끄덕여주는 로봇 목", "퇴사하고 싶을 때마다 사직서 찢는 ASMR 들려주는 앱",
    "비트코인 차트 보면서 롤러코스터 타는 VR 게임", "내 성대모사 퀄리티 평가해주는 오디션 앱", "길 가다 마주친 강아지 품종 알려주는 안경", "자취생 엄마 잔소리 구독 서비스", "엘리베이터 버튼 발로 누르게 해주는 페달",
    "지하철 옆사람 어깨에 기대면 전기 충격 주는 패드", "화장실 휴지 떨어지면 드론으로 배달해주는 서비스", "노래 못 부르면 예약 취소되는 코인노래방", "내 유언장 블록체인에 영구 박제하는 서비스", "못생긴 사진만 골라서 지워주는 갤러리 정리 AI",
    "친구한테 돈 빌려주고 안 갚으면 카톡 프사 자동으로 바꾸는 앱", "헬스장 기구 사용법 모르면 홀로그램으로 알려주는 AR", "편의점 알바생 진상 손님 퇴치용 사이렌", "내 얼굴로 이모티콘 1초 만에 만드는 생성기", "소개팅 앱 사진이랑 실물 다르면 환불해주는 보험",
    "나랑 똑같이 생긴 도플갱어 찾아주는 전 세계 검색 엔진", "맛없는 식당 가면 '맛없음' 깃발 꽂는 지도", "내 흑역사 자동으로 발굴해서 이불킥 하게 만드는 알람", "공부 안 하고 폰 만지면 전기 오르는 스마트폰 케이스", "내 반려동물이랑 대화 가능한 뇌파 번역기",
    "잠수 이별 당하면 상대방 회사에 화환 보내주는 서비스", "SNS 허세 사진 감별해주는 팩트체크 AI", "혼밥할 때 앞에 앉아서 같이 먹어주는 홀로그램 아이돌", "비 오는 날 우산 없이 뛰는 사람들 등수 매기는 스포츠", "지각 핑계 100가지 만들어주는 AI 생성기",
    "내 기분에 맞춰서 칵테일 제조해주는 텀블러", "월급날 1초 만에 스쳐 지나가는 돈 시각화해주는 AR", "상사 뒷담화하면 자동으로 익명 게시판에 올려주는 앱", "코인 노래방 점수 내기로 밥값 계산하는 결제 시스템", "내 묘비에 QR코드 박아서 인스타 링크 거는 서비스",
    "책 읽다 잠들면 자동으로 불 꺼주고 책갈피 꽂아주는 로봇", "운전 중 욱하면 차 안에서 클래식 틀어주는 내비게이션", "냉장고 유통기한 임박한 재료로 요리 대결하는 앱", "내 발 냄새 수치 측정해서 양말 교체 알림 주는 신발", "회의 중 딴짓하다 질문 받으면 답변 대신 해주는 AI",
    "지하철 쩍벌남 감지하면 다리 오므리게 하는 진동 의자", "내 목소리로 부모님께 안부 전화 대신 걸어주는 효도 AI", "옷장에 안 입는 옷 자동으로 중고장터에 올리는 로봇", "내 인생을 3줄 요약해서 자소서 써주는 생성기", "라면 국물 옷에 튀면 3초 안에 지워주는 휴대용 세탁기",
    "지하철 환승 최단 거리 바닥에 레이저로 쏴주는 신발", "화장실 변기 물 내리는 소리 데시벨 조절해주는 앱", "내가 코 골면 배우자 귀마개 자동으로 씌워주는 기계", "술자리에서 꼰대 발언 감지하면 마이크 꺼지는 기능", "내 통장 잔고에 맞춰서 점심 메뉴 골라주는 룰렛",
    "버스 기사님이랑 스몰토크 대신 해주는 챗봇", "비 오는 날 젖은 우산 10초 만에 말려주는 휴대용 드라이어", "엘리베이터 거울 보며 춤추면 영상 찍어서 틱톡에 올리는 CCTV", "내 기분에 따라 조명 색깔 바꿔주는 스마트 홈", "반려견 산책 대신 시켜주는 드론 리드줄"
]

EN_IDEAS = [
    "AI eraser that removes ex-lovers from photos naturally", "Revenge speaker that hacks noisy neighbors' wifi", "Stock market therapist that swears with you when red", "Earbuds that turn boss's nagging into classical music", "Smartwatch that donates money to charity if you skip gym",
    "Service to curate your own funeral playlist in advance", "Fake call app to escape bad dates immediately", "Router that blocks Uber Eats if you fail your diet", "Collar that texts you what your dog is actually saying", "Alarm clock that wakes you up with brutal personal insults",
    "App that automatically fines you for texting ex while drunk", "Platform to publicly shame lazy group project members", "AI that rates your gym mirror selfies brutally", "Sleep app that composes jazz music from your snoring", "Bounty hunter platform for tracking down online scammers",
    "3D printer that makes vegetables taste exactly like bacon", "Cure for Netflix Syndrome (spending hours choosing what to watch)", "App that checks local bridge water temp when crypto crashes", "Dating app that blocks incompatible MBTI types instantly", "AI that predicts job offer probability from your resume",
    "Sensor that switches screen to Excel when boss walks by", "Smart toilet that analyzes health from your poop photos", "Calculator for exactly how much cash to give at weddings", "Microphone that auto-tunes you only when you sing off-key", "Smart pot that curses at you if you ruin the Ramen water ratio",
    "AR glasses that navigate you to empty seats on the subway", "Voodoo doll shop that makes dolls of people you hate", "AI assistant that mimics your voice perfectly to answer calls", "App that predicts baldness and recommends wigs in advance", "AI that writes sick leave emails if you binged Netflix all night",
    "Recycling service that knits sweaters from cat hair", "Robot arm that cooks ramen for tired PC cafe workers", "Robot dog that licks your face clean if you're too lazy to wash", "Camera that estimates resale value of gifts from exes", "Machine that smashes keyboard for you when coding errors occur",
    "Deepfake OTT that puts your face in Hollywood movies", "Platform to hire people to wait in line for famous restaurants", "Meditation VR to find your lost mental stability", "Dream interpretation AI for lottery numbers seen in sleep", "App that auto-reports friends who don't pay their share of trips",
    "Digital laundry service that deletes all your hateful comments", "App where AI fights back against voice phishing scammers", "Glasses that black out 1 second before scary movie scenes", "Budget app that sighs audibly when you check your balance", "Barber chair that sounds an alarm if the barber talks to you",
    "AI that analyzes date's Instagram to flag 'red flags'", "Drone security service that follows you on dark streets", "App that detects lying used car dealers by eye movement", "Insurance that refunds double if food delivery is late", "Matchmaking system for real-life fights with game trollers",
    "Simulation game calculating success rate of unrequited love", "Platform to host a contest for your own tombstone epitaph", "Chatbot that prays for your company's bankruptcy every Monday", "Real-time map tracking street food trucks", "Kit to fry eggs using laptop heat",
    "Hypnosis VR to experience your past life", "Funeral service for house plants when they die", "Perfume that makes you smell clean even if you didn't shower", "Robot neck that nods for you during boring meetings", "App that plays ASMR of tearing resignation letters",
    "VR game riding a rollercoaster based on Bitcoin charts", "Audition app rating your impersonation quality", "Glasses that identify dog breeds on the street", "Subscription service for mom's nagging for people living alone", "Pedal to press elevator buttons with your foot",
    "Shoulder pad that shocks strangers if they lean on you on subway", "Drone delivery for toilet paper when you run out", "Karaoke that cancels song if you sing terribly", "Service to permanently record your will on blockchain", "AI gallery cleaner that deletes only ugly photos",
    "App that changes friend's profile pic if they don't pay back money", "AR that shows how to use gym machines if you look confused", "Siren for convenience store clerks to chase away rude customers", "Generator creating emojis from your face in 1 second", "Insurance giving refund if dating app date looks different IRL",
    "Search engine to find your doppelganger worldwide", "Map where you plant 'Not Tasty' flags on bad restaurants", "Alarm that reminds you of embarrassing past moments", "Phone case that shocks you if you touch it instead of studying", "Brainwave translator to talk with your pet",
    "Service sending wreaths to ex's workplace after ghosting", "Fact-check AI for showing off photos on SNS", "Hologram idol that eats with you when dining alone", "Sport ranking people running without umbrellas in rain", "AI generator for 100 excuses for being late",
    "Tumbler that mixes cocktails based on your mood", "AR visualizing salary vanishing in 1 second on payday", "App posting anonymous complaints about boss automatically", "Payment system where karaoke score decides who pays dinner", "Service engraving QR code on tombstone linking to Instagram",
    "Robot that turns off lights and bookmarks page if you fall asleep reading", "Navigation that plays classical music if you get road rage", "App for cooking battles using expiring fridge ingredients", "Shoes that notify you to change socks based on odor level", "AI that answers questions for you if you zone out in meetings",
    "Vibrating chair that forces 'manspreaders' on subway to close legs", "AI calling parents in your voice to say youre fine", "Robot selling unworn clothes from closet automatically", "Generator summarizing your life into 3 lines for resume", "Portable washer removing ramen stains in 3 seconds",
    "Shoes projecting laser path for fastest subway transfer", "App adjusting toilet flush volume to hide sounds", "Machine putting earplugs on spouse if you snore", "Microphone that cuts off if you make 'boomer' comments while drinking", "Roulette choosing lunch menu based on bank balance",
    "Chatbot doing small talk with bus drivers for you", "Portable dryer drying wet umbrella in 10 seconds", "CCTV posting TikToks if you dance in elevator", "Smart home changing lights based on your mood", "Drone leash walking your dog for you"
]

# ------------------------------------------------------------------
# 3. Initialization
# ------------------------------------------------------------------
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'result_data' not in st.session_state:
    st.session_state.result_data = {}
if 'input_area_key' not in st.session_state:
    st.session_state.input_area_key = "" 

def pick_random_idea(lang):
    target_deck = KR_IDEAS if lang == 'ko' else EN_IDEAS
    st.session_state.input_area_key = random.choice(target_deck)

def get_ui_text(lang_code):
    text_pack = {
        "ko": {
            "main_title": "Validatix MVP 🔥", # [이름 변경] 
            "sub_title": "AI가 당신의 사업 아이디어를 팩트로 폭행합니다.",
            "input_label": "아이디어 입력",
            "input_placeholder": "예: 직장인 점심 메뉴 추천 서비스",
            "analyze_btn": "🔥 팩트 폭력 당하기 (분석)",
            "random_btn": "🎲 예시 아이디어 넣기", 
            "warning": "아이디어를 입력하세요.",
            "connecting": "🧠 Validatix Brain 접속 중...", # [이름 변경] 
            "analyzing": "🔍 아이디어 해부 중...",
            "calculating": "💰 수익 모델 계산 중...",
            "score_title": "생존 확률",
            "tab_free": "🔥 팩트 폭력 (무료)",
            "tab_paid": "📊 심층 리포트 (Premium)",
            "roast_title": "💀 왜 망하는가?",
            "share_btn": "🐦 트위터 공유",
            "share_msg": "내 사업 점수: {score}점 ㅋㅋㅋ AI가 '{one_liner}'라고 함.",
            "info_msg": "💡 이 탭은 당신이 '살아남을 방법'을 알려줍니다.",
            "swot_title": "1. SWOT 심층 분석",
            "money_title": "2. 💰 구체적 수익화 모델 (Top 3)",
            "survival_title": "3. 🛡️ 유일한 생존 전략 및 타임라인",
            "lock_title": "🔒 Premium 리포트 열람하기",
            "lock_desc": "당신의 아이디어를 살릴 <b>구체적인 생존 전략</b>과 <b>수익 모델</b>이 숨겨져 있습니다.",
            "price": "단돈 4,900원 (커피 한 잔 값)",
            "unlock_btn": "👉 카톡으로 문의하기",
        },
        "en": {
            "main_title": "Validatix MVP 🔥", # [이름 변경] 
            "sub_title": "AI roasts your business idea with brutal facts.",
            "input_label": "Enter Idea",
            "input_placeholder": "e.g., AI dating coach",
            "analyze_btn": "🔥 Roast My Idea",
            "random_btn": "🎲 Random Idea",
            "warning": "Please enter an idea.",
            "connecting": "🧠 Connecting...",
            "analyzing": "🔍 Analyzing...",
            "calculating": "💰 Calculating...",
            "score_title": "Success Rate",
            "tab_free": "🔥 Roast (Free)",
            "tab_paid": "📊 Deep Report (Premium)",
            "roast_title": "💀 Brutal Feedback",
            "share_btn": "🐦 Share on X",
            "share_msg": "My Score: {score}/100 💀 AI said: '{one_liner}'",
            "info_msg": "💡 This tab reveals how to survive.",
            "swot_title": "1. Deep SWOT Analysis",
            "money_title": "2. 💰 Monetization Strategy",
            "survival_title": "3. 🛡️ Survival Strategy & Timeline",
            "lock_title": "🔓 Unlock Full Report",
            "lock_desc": "Get the <b>Survival Strategy</b> & <b>Revenue Model</b>.",
            "price": "Only $4.90",
            "unlock_btn": "👉 Unlock Now",
        }
    }
    return text_pack[lang_code]

# ------------------------------------------------------------------
# 4. Main UI
# ------------------------------------------------------------------
col_lang1, col_lang2, col_lang3 = st.columns([1, 2, 1])
with col_lang2:
    lang_choice = st.radio("언어 / Language", ["🇰🇷 한국어", "🇺🇸 English"], horizontal=True, label_visibility="collapsed")

current_lang = "ko" if "한국어" in lang_choice else "en"
ui = get_ui_text(current_lang)

st.markdown(f'<h1 style="text-align: center;">{ui["main_title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center; color: #8B949E; margin-bottom: 30px;">{ui["sub_title"]}</div>', unsafe_allow_html=True)

user_text = st.text_area(ui["input_label"], height=100, placeholder=ui["input_placeholder"], key="input_area_key")

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    analyze_btn = st.button(ui["analyze_btn"])
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    st.button(ui["random_btn"], on_click=pick_random_idea, args=(current_lang,))
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# 5. Logic
# ------------------------------------------------------------------
if analyze_btn:
    if not user_text:
        st.warning(ui["warning"])
    else:
        status_box = st.status(ui["connecting"], expanded=True)
        progress_bar = status_box.progress(0)
        
        try:
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"temperature": 0.4})
            progress_bar.progress(30)
            status_box.write(ui["analyzing"])
            
            if current_lang == "ko":
                prompt = f"""
                당신은 실리콘밸리의 가장 냉혹하고 파괴적인 비즈니스 컨설턴트(Validatix)입니다. 
                사용자 아이디어: "{user_text}"
                
                [절대 규칙]
                1. 모든 출력 결과물은 반드시 **한국어(Korean)**로만 작성할 것.
                2. 해결책 노출 금지: FEEDBACK과 SWOT에서는 대안을 주지 말고 철저하게 짓밟을 것.
                
                IMPORTANT: Use the exact tags below.
                
                [[[SCORE]]] 
                (0~100 사이의 숫자 하나만 출력. 형편없는 아이디어는 10~30점 부여)
                
                [[[ONE_LINER]]] 
                (유저의 기선을 제압하는 건방지고 도발적인 한 줄 평)
                
                [[[FEEDBACK]]] 
                아이디어가 망할 수밖에 없는 3가지 이유를 작성. 
                ### [뼈 때리는 소제목]
                (소제목은 20자 이내 한 줄로. 그 아래 4~5문장의 독설을 상세하게 작성)
                
                [[[SWOT]]] 
                (FORCE FORMAT: You MUST render a Markdown Table.
                Header: | 구분 | 냉혹한 심층 평가 |
                Separator: |---|---|
                Rows: 구분 열에는 `**Strengths**<br>(강점)`, `**Weaknesses**<br>(약점)`, `**Opportunities**<br>(기회)`, `**Threats**<br>(위협)` 형식 사용.
                내용 열: 각 항목당 최소 4~5문장 이상으로 구체적 리스크를 포함하여 길게 작성.
                CRITICAL FORMATTING RULE: 테이블 직후 반드시 아래 인용구 출력:
                > **"하지만 절망하기엔 이릅니다. 이 형편없는 아이디어의 타겟과 수익 모델을 비틀어, 월 매출 1,000만 원짜리 비즈니스로 탈바꿈시킬 '단 하나의 치명적인 피벗(Pivot) 전략'이 아래에 숨겨져 있습니다."**
                )
                
                [[[MONETIZATION]]] 
                (수익 모델 3가지를 구체적으로 작성. 각 모델마다 아래 하위 구조를 반드시 포함:
                ### 1. [수익 모델 이름]
                * **핵심 가치:** (왜 돈을 내는지 3문장 이상)
                * **타겟 고객:** (정확한 페르소나)
                * **적정 가격(Price):** (구체적 금액)
                * **세일즈 채널:** (구체적 영업 채널)
                )
                
                [[[SURVIVAL]]] 
                (피벗 전략과 액션 플랜 3가지. 각 전략마다 아래 구조 포함:
                ### 1. [생존 전략 이름]
                * **전략의 본질:** (왜 유일한 돌파구인지 3문장 이상)
                * **Day 1 Action:** (내일 당장 실행할 구체적 업무)
                * **Day 30 Action:** (한 달 내 달성할 마일스톤)
                )
                """
            else:
                prompt = f"""
                You are Validatix, the most ruthless and destructive business consultant in Silicon Valley.
                User Idea: "{user_text}"
                
                [CRITICAL RULE]
                1. You MUST write your ENTIRE response ONLY in **ENGLISH**. No other languages allowed.
                2. No Solutions Early: In FEEDBACK and SWOT, only destroy the idea. Do not offer solutions.
                
                IMPORTANT: Use the exact tags below.
                
                [[[SCORE]]] 
                (Output a single number between 0 and 100. Give 10-30 for bad ideas. Be harsh.)
                
                [[[ONE_LINER]]] 
                (A savage, arrogant one-liner roasting the user's idea)
                
                [[[FEEDBACK]]] 
                Write 3 reasons why this idea will inevitably fail.
                ### [Brutal Subheading]
                (Keep the subheading under 50 characters, on a single line. Below it, write 4-5 sentences of brutal, detailed critique.)
                
                [[[SWOT]]] 
                (FORCE FORMAT: You MUST render a Markdown Table.
                Header: | Category | Brutal Deep Analysis |
                Separator: |---|---|
                Rows: Use `**Strengths**`, `**Weaknesses**`, `**Opportunities**`, `**Threats**` for the Category column.
                Content: Write at least 4-5 sentences per item. Be highly analytical and detailed.
                CRITICAL FORMATTING RULE: Immediately after the table, you MUST output this exact quote:
                > **"But do not despair just yet. By twisting the target and monetization model of this terrible idea, the 'one fatal pivot strategy' to transform it into a $10K/month business is hidden below."**
                )
                
                [[[MONETIZATION]]] 
                (Write 3 highly specific monetization models. Include these sub-bullets for each:
                ### 1. [Monetization Model Name]
                * **Core Value:** (Explain why customers will pay in 3+ sentences)
                * **Target Customer:** (Highly specific persona)
                * **Appropriate Price:** (Specific pricing strategy)
                * **Sales Channel:** (Specific acquisition channels)
                )
                
                [[[SURVIVAL]]] 
                (Write 3 specific pivot strategies and action plans. Include this timeline structure for each:
                ### 1. [Survival Strategy Name]
                * **Essence of Strategy:** (Why this pivot is the only way out in 3+ sentences)
                * **Day 1 Action:** (One immediate, zero-cost action item for tomorrow)
                * **Day 30 Action:** (A concrete milestone to achieve within a month)
                )
                """
            
            response = model.generate_content(prompt, safety_settings=safety_settings)
            progress_bar.progress(80)
            status_box.write(ui["calculating"])
            
            content = response.text
            
            def extract_tag(tag, text, default=""):
                pattern = fr"\[\[\[{tag}\]\]\](.*?)(?=\[\[\[|$)"
                match = re.search(pattern, text, re.DOTALL)
                return match.group(1).strip() if match else default

            score_text = extract_tag("SCORE", content, "0")
            st.session_state.score = int(re.search(r'\d+', score_text).group()) if re.search(r'\d+', score_text) else 0
            
            default_one_liner = "AI가 할 말을 잃었습니다." if current_lang == "ko" else "AI is speechless."
            default_feedback = "분석 실패." if current_lang == "ko" else "Analysis failed."
            default_data = "데이터 없음." if current_lang == "ko" else "No data."

            st.session_state.result_data = {
                "one_liner": extract_tag("ONE_LINER", content, default_one_liner),
                "feedback": extract_tag("FEEDBACK", content, default_feedback),
                "swot": extract_tag("SWOT", content, default_data),
                "money": extract_tag("MONETIZATION", content, default_data),
                "survival": extract_tag("SURVIVAL", content, default_data)
            }
            
            st.session_state.analyzed = True
            progress_bar.progress(100)
            status_box.update(label="Complete!", state="complete", expanded=False)
            
            if current_lang == "ko":
                st.toast("🔥 팩트 폭력 완료! 멘탈 꽉 잡으세요.", icon="💀")
            else:
                st.toast("🔥 Roast Complete! Brace yourself.", icon="💀")

        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.analyzed:
    data = st.session_state.result_data
    score = st.session_state.score
    
    st.divider()
    
    score_class = "score-red" if score < 50 else "score-green"
    
    st.markdown(f"""
    <div class="score-card">
        <h2 style='margin:0; color:#8B949E !important; border:none;'>{ui['score_title']}</h2>
        <div class='{score_class}' style='font-family:"JetBrains Mono", monospace; font-size:72px; font-weight:bold; margin:10px 0;'>{score}%</div>
        <p style='font-size:20px; font-weight:bold; color:#FFFFFF; word-break: keep-all !important;'>"{data['one_liner']}"</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([ui['tab_free'], ui['tab_paid']])
    
    with tab1:
        st.subheader(ui['roast_title'])
        st.markdown(data['feedback'], unsafe_allow_html=True)
        
        share_text = urllib.parse.quote(ui['share_msg'].format(score=score, one_liner=data['one_liner']))
        st.markdown(f"""
        <br>
        <a href="https://twitter.com/intent/tweet?text={share_text}&url=https://genesis-mvp.streamlit.app" target="_blank" style="text-decoration:none;">
            <button style='background:#1DA1F2; color:white; border:none; padding:12px 24px; border-radius:30px; font-weight:bold; cursor:pointer; width:100%;'>
                {ui['share_btn']}
            </button>
        </a>
        """, unsafe_allow_html=True)

    with tab2:
        st.info(ui['info_msg'])
        
        st.markdown(f"## {ui['swot_title']}")
        st.markdown(data['swot'], unsafe_allow_html=True)
        st.markdown("---")
        
        money_html = data['money'].replace("###", "<h3>").replace("**", "").replace("-", "•").replace("\n", "<br>")
        survival_html = data['survival'].replace("###", "<h3>").replace("**", "").replace("-", "•").replace("\n", "<br>")

        if dev_mode:
            st.markdown(f"## {ui['money_title']}")
            st.markdown(data['money'], unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"## {ui['survival_title']}")
            st.markdown(data['survival'], unsafe_allow_html=True)
        else:
            payment_link = KAKAO_LINK if current_lang == "ko" else BMC_LINK
            button_text = ui['unlock_btn']
            button_color = "#FEE500" if current_lang == "ko" else "#FFDD00" 
            text_color = "#191919" if current_lang == "ko" else "#000000"

            st.markdown(f"""
            <div class="final-gatekeeper-box">
                <h2 style='color:#FFF !important; border:none; margin:0 !important;'>{ui['lock_title']}</h2>
                <p style='color:#DDD; margin-top:15px;'>{ui['lock_desc']}</p>
                <p style='color:#F04452; font-weight:bold; font-size:24px; margin: 25px 0;'>{ui['price']}</p>
                <a href="{payment_link}" target="_blank" style="text-decoration: none;">
                    <button style='background:{button_color}; color:{text_color}; border:none; padding:15px 30px; border-radius:10px; font-size:18px; font-weight:bold; cursor:pointer; width:100%; display:block; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                        {button_text}
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="final-blur-content">
                <h2>{ui['money_title']}</h2>
                {money_html}
                <br><br>
                <h2>{ui['survival_title']}</h2>
                {survival_html}
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px; padding-bottom: 50px;">
        <p>Copyright © 2026 Validatix MVP. All rights reserved.</p>
        <p>Contact: <a href="mailto:seotony77@gmail.com" style="color: #888;">seotony77@gmail.com</a></p>
    </div>
""", unsafe_allow_html=True)