
from resemblyzer import VoiceEncoder, preprocess_wav

import numpy as np
import io ## like pillow for audio files
import librosa
import streamlit as st

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

def get_voice_embeddings(audio_bytes):
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)

        return embedding.tolist() # 256 
    except Exception as e:
        st.error("Voice Recognition Error")

        return None

def identify_speaker(new_embedding, candidate_dict, threshold=0.65):

    if new_embedding is None or not candidate_dict:
        return None
    best_student_id = None
    best_score=-1

    for student_id, stored_embedding in candidate_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding)

            if similarity >= best_score:
                best_score = similarity
                best_student_id = student_id
    if best_score >= threshold:
        return best_student_id, best_score
    return None, best_score

def process_bulk_audio(audio_bytes, candidate_dict, threshold=0.65):
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = librosa.effects.split(audio, top_db=30) ## split the audio into segments and also removing the useless audio
        ## top_db => high means it will take only loud audio 
        ## top_db => low means it can take very low audio so 30 is optimal

        identified_results = {}

        for start, end in segments:
            if len(start-end) < sr*0.5:
                continue
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)


            student_id, score = identify_speaker(embedding, candidate_dict, threshold)

            if student_id not in identified_results or score > identified_results[student_id]:
                 identified_results[student_id] = score
        return identified_results
    except Exception as e:
        st.error("Bulk process error")
        return {}



