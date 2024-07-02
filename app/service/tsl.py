from flask import Blueprint, request, jsonify
from transformers import MarianMTModel, MarianTokenizer
from flask_socketio import emit
from .. import socketio  # Correctly import socketio

translate_bp = Blueprint('translate_bp', __name__)

# Supported language models
models = {
    'es': 'Helsinki-NLP/opus-mt-en-es',
    'zh': 'Helsinki-NLP/opus-mt-en-zh',
    'fr': 'Helsinki-NLP/opus-mt-en-fr',
    'ar': 'Helsinki-NLP/opus-mt-en-ar',
    'ru': 'Helsinki-NLP/opus-mt-en-ru',
    'de': 'Helsinki-NLP/opus-mt-en-de',
    'ja': 'Helsinki-NLP/opus-mt-en-ja',
    'pt': 'Helsinki-NLP/opus-mt-en-pt',
    'it': 'Helsinki-NLP/opus-mt-en-it',
    'hi': 'Helsinki-NLP/opus-mt-en-hi',
    'vi': 'Helsinki-NLP/opus-mt-en-vi',
}

def translate_text(text, language, socket_id):
    sentences = text.split('\n')
    translated_sentences = []
    model_name = models[language]
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    total_sentences = len(sentences)

    for i, sentence in enumerate(sentences):
        if sentence.strip():
            tokenized_text = tokenizer.prepare_seq2seq_batch([sentence], return_tensors='pt')
            translated = model.generate(**tokenized_text)
            translated_sentence = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
            translated_sentences.append(translated_sentence)
        else:
            translated_sentences.append('')

        # Emit progress update
        progress = (i + 1) / total_sentences * 100
        socketio.emit('progress', {'progress': progress}, room=socket_id)
    
    translated_text = '\n'.join(translated_sentences)
    return translated_text

@translate_bp.route('/book/translate', methods=['POST'])
def translate():
    data = request.get_json()
    if 'book_data' not in data or 'language' not in data or 'socket_id' not in data:
        return jsonify({'error': 'No book data, language, or socket ID specified'}), 400

    book_data = data['book_data']
    language = data['language']
    socket_id = data['socket_id']

    if language not in models:
        return jsonify({'error': 'Unsupported language'}), 400
    
    translated_text = translate_text('\n'.join(book_data.values()), language, socket_id)
    return jsonify({'success': True, 'translated_text': translated_text})

