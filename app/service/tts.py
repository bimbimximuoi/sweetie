from flask import Blueprint, request, jsonify, send_file
from TTS.api import TTS
import os
from flask_socketio import emit
from tqdm import tqdm
import wave
from .. import socketio

speech_bp = Blueprint('speech_bp', __name__)

# Model name
MODEL_NAME = "tts_models/en/ljspeech/tacotron2-DDC"

# Initialize the TTS model
tts = TTS(model_name=MODEL_NAME, progress_bar=False, gpu=False)

def text_to_speech(text, speaker=None, socket_id=None):
    tts_output_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'output.wav')

    try:
        # Split the text into manageable chunks
        def split_text(text, max_length=500):
            words = text.split()
            chunks = []
            current_chunk = []
            current_length = 0
            for word in words:
                if current_length + len(word) + 1 > max_length:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word) + 1
                else:
                    current_chunk.append(word)
                    current_length += len(word) + 1
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            return chunks

        # Progress callback function
        def progress_callback(progress, chunk_idx, total_chunks):
            overall_progress = int((chunk_idx / total_chunks) * 100) + int((progress / total_chunks))
            if socket_id:
                socketio.emit('progress', {'progress': overall_progress}, to=socket_id)
        
        text_chunks = split_text(text)
        total_chunks = len(text_chunks)
        
        with wave.open(tts_output_path, 'wb') as f_out:
            for i, chunk in enumerate(text_chunks):
                chunk_output_path = os.path.join(os.path.dirname(__file__), '..', 'static', f'chunk_{i}.wav')
                with tqdm(total=100, desc=f"Generating TTS for chunk {i+1}/{total_chunks}", unit="%", position=0, leave=True) as pbar:
                    def update_progress_callback(progress):
                        pbar.update(progress - pbar.n)
                        progress_callback(progress, i, total_chunks)
                    
                    tts.tts_to_file(text=chunk, file_path=chunk_output_path, speaker=speaker, progress_callback=update_progress_callback)
                    
                    # Append each chunk to the final output file
                    with wave.open(chunk_output_path, 'rb') as f_in:
                        if i == 0:
                            # Set the parameters for the output file from the first chunk
                            f_out.setnchannels(f_in.getnchannels())
                            f_out.setsampwidth(f_in.getsampwidth())
                            f_out.setframerate(f_in.getframerate())
                        f_out.writeframes(f_in.readframes(f_in.getnframes()))
                    os.remove(chunk_output_path)
                # Ensure progress is updated to 100% for each chunk
                progress_callback(100, i + 1, total_chunks)
    except Exception as e:
        print(f"Error generating TTS output: {e}")
        return None
    return tts_output_path

@speech_bp.route('/api/book/speech', methods=['POST'])
def generate_tts():
    data = request.get_json()
    text = data.get('text')
    speaker = data.get('speaker')
    socket_id = data.get('socket_id')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    tts_output_path = text_to_speech(text, speaker, socket_id)
    
    if not tts_output_path or not os.path.exists(tts_output_path):
        return jsonify({'error': 'Failed to generate TTS output'}), 500
    
    response = send_file(tts_output_path, as_attachment=True)
    os.remove(tts_output_path)  # Clean up the generated file
    return response
