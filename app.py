from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import anthropic

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wisdom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

anthropic_api_key = os.environ.get('sk-ant-api03--Nx...zgAA')
client = anthropic.Client(api_key=anthropic_api_key)

class Reflection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wisdom_content = db.Column(db.String(500), nullable=False)
    wisdom_author = db.Column(db.String(100), nullable=False)
    reflection = db.Column(db.String(500), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/wisdom', methods=['GET'])
def get_wisdom():
  try:
    query = request.args.get('query', '')
    prompt = f"사용자의 질문: '{query}'\n\n이 질문에 관련된 3개의 명언이나 책 구절을 제시해주세요. 각 항목은 '내용'과 '출처'를 포함해야 합니다."
    response = client.completion(
        prompt=prompt,
        model="claude-2",
        max_tokens_to_sample=300,
        stop_sequences=["\n\n"]
    )
    wisdom_items = parse_anthropic_response(response.completion)
    return jsonify(wisdom_items)
   except Exception as e:
        print(f"Error in get_wisdom: {str(e)}")
        return jsonify({"error": str(e)}), 500

def parse_anthropic_response(response):
    lines = response.strip().split('\n')
    wisdom_items = []
    for line in lines:
        parts = line.split(' - ')
        if len(parts) == 2:
            wisdom_items.append({
                "content": parts[0].strip(),
                "author": parts[1].strip()
            })
    return wisdom_items

@app.route('/api/save-reflection', methods=['POST'])
def save_reflection():
    data = request.json
    new_reflection = Reflection(
        wisdom_content=data['wisdom']['content'],
        wisdom_author=data['wisdom']['author'],
        reflection=data['reflection']
    )
    db.session.add(new_reflection)
    db.session.commit()
    return jsonify({"success": True, "id": new_reflection.id})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

