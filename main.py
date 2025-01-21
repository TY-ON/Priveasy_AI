import google.generativeai as genai

# Gemini API Key 설정
<<<<<<< Updated upstream
GOOGLE_API_KEY = "your-api-key"
=======
GOOGLE_API_KEY = "발급받은 Gemini API Key 입력"
>>>>>>> Stashed changes

# API 키로 설정 구성
genai.configure(api_key=GOOGLE_API_KEY)

def generate_content_with_gemini(prompt):
    """
    Google Gemini API를 사용하여 콘텐츠를 생성하는 함수.
    """
    try:
        # Generative Model 초기화
        model = genai.GenerativeModel('gemini-pro')
        
        # 콘텐츠 생성 요청
        response = model.generate_content(prompt)
        
        # 응답 내용 반환
        return response.text

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Google Gemini 콘텐츠 생성 서비스")
    print("종료하려면 'exit'를 입력하세요.")
    
    while True:
        # 사용자 입력 받기
        prompt = input("\n질문 입력: ").strip()
        
        if prompt.lower() == 'exit':
            print("서비스를 종료합니다.")
            break
        
        # Gemini API로 콘텐츠 생성
        content = generate_content_with_gemini(prompt)
        
        if content:
            print(f"생성된 콘텐츠: {content}")
        else:
            print("콘텐츠 생성에 실패했습니다.")
