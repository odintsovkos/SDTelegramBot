from faster_whisper import WhisperModel

def transcribe_audio(audio_file_path, model_size="large-v2", device="cuda", vad_filter=True, language="ru"):
    model = WhisperModel(model_size, device=device, compute_type="float16")
    segments, _ = model.transcribe(audio_file_path, beam_size=5, vad_filter=vad_filter, language=language)
    all_text = ""

    for segment in segments:
        all_text += segment.text

    return all_text