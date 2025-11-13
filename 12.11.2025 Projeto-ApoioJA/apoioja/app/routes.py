from flask import render_template, request, jsonify
from app import app, db
from app.models import Report
from app.chatbot import get_gemini_response, get_fallback_response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/denuncia')
def denuncia():
    return render_template('denuncia.html')

@app.route('/api/reports', methods=['POST'])
def create_report():
    data = request.get_json()
    new_report = Report(
        category=data.get('category'),
        description=data.get('description'),
        location=data.get('location')
    )
    db.session.add(new_report)
    db.session.commit()
    return jsonify({"message": "Denúncia registrada com sucesso!"}), 201


@app.route('/api/chat', methods=['GET', 'POST'])
def api_chat():
    if request.method == 'GET':
        return jsonify({
            "info": "Use POST com JSON {'message':'texto'} para conversar."
        })

    data = request.get_json() or {}
    msg = (data.get('message') or '').strip()
    context = data.get('context')

    if not msg:
        return jsonify({"error": "Mensagem vazia."}), 400

    reply = get_gemini_response(msg, context=context)
    if not reply:
        reply = get_fallback_response()

    return jsonify({"reply": reply}), 200
