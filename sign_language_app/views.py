import os
import numpy as np
import tensorflow as tf
from PIL import Image
import matplotlib.pyplot as plt
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import wave
import json
import vosk
import logging

# Ensure the punkt tokenizer models are downloaded
from nltk import download
download('punkt')

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the pre-trained autoencoder model
model = tf.keras.models.load_model(r'C:\Users\Sejal\Desktop\FOSS\MODEL\smodel.keras')

# Initialize and fit the tokenizer
tokenizer = Tokenizer(char_level=True)
tokenizer.fit_on_texts('abcdefghijklmnopqrstuvwxyz')
max_label_length = 5  # Define based on your model's requirements

def preprocess_text(text, tokenizer, max_label_length):
    seq = tokenizer.texts_to_sequences([text])
    return pad_sequences(seq, maxlen=max_label_length)

def generate_image_from_letter(model, letter, tokenizer, max_label_length):
    seq = preprocess_text(letter, tokenizer, max_label_length)
    generated_image = model.predict(seq)
    generated_image = np.clip(generated_image.squeeze(), 0, 1)  # Clip values to [0, 1] to prevent noise
    image_array = (generated_image * 255).astype(np.uint8)
    return Image.fromarray(image_array)

def generate_images_from_word(model, word, tokenizer, max_label_length):
    images = []
    for letter in word:
        img = generate_image_from_letter(model, letter, tokenizer, max_label_length)
        images.append(img)
    return images

def combine_images_into_word(images, word):
    widths, heights = zip(*(img.size for img in images))
    total_width = sum(widths)
    max_height = max(heights)

    combined_image = Image.new('RGB', (total_width, max_height), (255, 255, 255))
    x_offset = 0
    for img in images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width

    return combined_image

def extract_audio_from_video(video_path, audio_path):
    try:
        video = VideoFileClip(video_path)
        logging.info(f"Video file loaded successfully: {video_path}")

        if video.audio is None:
            logging.error("The video file has no audio stream.")
            return False

        video.audio.write_audiofile(audio_path)
        logging.info(f"Audio extracted and saved to: {audio_path}")
        return True
    except Exception as e:
        logging.error(f"Error extracting audio from video: {e}")
        return False

def transcribe_audio_to_text(audio_path):
    try:
        wf = wave.open(audio_path, "rb")
        model = vosk.Model(r'C:\Users\Sejal\Desktop\FOSS\vosk-model-small-en-us-0.15')  # Specify the path to the Vosk model
        recognizer = vosk.KaldiRecognizer(model, wf.getframerate())

        transcript = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                transcript += result.get("text", "") + " "
                logging.info(f"Intermediate Result: {result}")

        result = json.loads(recognizer.FinalResult())
        transcript += result.get("text", "")
        logging.info(f"Final Result: {result}")
        
        wf.close()
        
        return transcript.strip()
    except Exception as e:
        logging.error(f"Error in transcription: {e}")
        return ""

def index(request):
    return render(request, 'index.html')

def overlay_images_on_video(video_path, images_data, output_video_path):
    video = VideoFileClip(video_path)
    clips = [video]

    current_time = 0
    duration_per_image = video.duration / len(images_data)

    for word_data in images_data:
        word_image = word_data['word_image']
        img = ImageClip(word_image).set_duration(duration_per_image).set_start(current_time).resize(height=100).margin(right=8, opacity=0).set_pos(('center', 'bottom'))
        clips.append(img)
        current_time += duration_per_image

    
    final_video = CompositeVideoClip(clips)
    
    # Ensure the original audio is included in the final video
    final_video = final_video.set_audio(video.audio)  
    final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
    logging.info(f"Video with audio written to {output_video_path}")

def upload_video(request):
    if request.method == 'POST':
        video_file = request.FILES['video']
        video_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        # Verify the video file exists
        if not os.path.exists(video_path):
            logging.error(f"Video file does not exist: {video_path}")
            return JsonResponse({'error': 'Video file does not exist'}, status=400)

        logging.info(f"Video file uploaded and saved to: {video_path}")

        audio_path = os.path.join(settings.MEDIA_ROOT, 'extracted_audio.wav')
        if not extract_audio_from_video(video_path, audio_path):
            return JsonResponse({'error': 'Failed to extract audio from video'}, status=400)
        
        text = transcribe_audio_to_text(audio_path)

        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            os.makedirs(media_root)

        images_data = []
        words = text.split()

        for word in words:
            images = generate_images_from_word(model, word, tokenizer, max_label_length)
            combined_image = combine_images_into_word(images, word)
            img_path = os.path.join(media_root, f'{word}.png')
            combined_image.save(img_path)
            images_data.append({
                'word': word,
                'word_image': img_path,
                'letters': [{'char': letter, 'image_url': img_path} for letter in word]  # Ensure each letter data is included
            })

        output_video_path = os.path.join(media_root, 'output_video.mp4')
        overlay_images_on_video(video_path, images_data, output_video_path)

        response_data = {
            'output_video_url': settings.MEDIA_URL + 'output_video.mp4',
            'images': images_data
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request'}, status=400)
