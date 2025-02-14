from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

GOOGLE_API_KEY = "your-api-key"

app = Flask(__name__)

# API 키로 설정 구성
genai.configure(api_key=GOOGLE_API_KEY)

def generate_summary(text):
    """
    Google Gemini API를 사용하여 프롬프트 기반의 AI 응답을 생성하는 함수.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(text)
        return response.text.strip()
    except Exception as e:
        return str(e)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    privacy_text = data.get("privacyText", "")

    if not privacy_text:
        return jsonify({"error": "No privacyText provided"}), 400

    # AI 요약 실행
    summary = generate_summary(privacy_text)
    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
