from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
# For Flash Messages
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from django.core.files.storage import FileSystemStorage

import os
from pathlib import Path
import docx2txt  # for DOCX files
from PyPDF2 import PdfReader  # for PDF files
# from google.cloud import speech
import io

import re
import nltk
import heapq
from transformers import pipeline
import wave
import numpy as np
from pydub import AudioSegment
import assemblyai as aai
import whisper

# Create your views here.

# def sign(request):
#     return render(request, 'signup.html')



aai.settings.api_key = 'b887fb784c91426b981da8083e9c7208'


def homepage(request):
    return render(request, 'homepage.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after sign up
            return render(request,'base.html')  
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request,'base.html') # Use a URL name defined in your URL patterns
        else:
            # Optionally, you can add an error message here
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        messages.success(request, 'You do not have an account')
        return render(request, 'login.html')
    
def howitworks(request):
    return render(request, 'howitworks.html')


def main(request):
    return render(request,'base.html')







# def transcribe_audio(file_path, uploaded_file):
#     # Get the file extension
    
#     # Convert the audio file to a format that SpeechRecognition can handle
#     if uploaded_file.content_type in ['audio/mpeg', 'audio/mp3', 'audio/aac', 'audio/ogg']:
#         audio = AudioSegment.from_file(file_path, format=file_extension[1:])
#         file_path = 'temp.wav'
#         audio.export(file_path, format='wav')

#     # Initialize recognizer
#     recognizer = sr.Recognizer()

#     # Load the audio file
#     with sr.AudioFile(file_path) as source:
#         audio_data = recognizer.record(source)

#     # Transcribe the audio
#     try:
#         text = recognizer.recognize_google(audio_data)
#         return text
#     except sr.UnknownValueError:
#         return "Google Speech Recognition could not understand the audio"
#     except sr.RequestError as e:
#         return f"Could not request results from Google Speech Recognition service; {e}"

global text
text = ""

def upload_document(request):
    try:
        if request.method == 'POST':
            if 'document' in request.FILES:
                uploaded_file = request.FILES['document']
                

                if uploaded_file.content_type in ['audio/mp3', 'audio/mpeg' , 'audio/flac', 'audio/aac', 'audio/ogg', 'audio/wav']:
                    fs = FileSystemStorage()
                    filename = fs.save(uploaded_file.name, uploaded_file)
                
                    transcriber = aai.Transcriber()
                    transcript = transcriber.transcribe(filename)

                    if transcript.status == aai.TranscriptStatus.error:
                        print(transcript.error)
                    else:
                        text = transcript.text


                    
                    # model_path = 'models/deepspeech-0.9.3-models.pbmm'
                    # scorer_path = 'models/deepspeech-0.9.3-models_2.scorer'
                            
                    # # Load DeepSpeech model
                    # ds = deepspeech.Model(model_path)

                    # # Perform speech-to-text
                    # text = ds.stt(filename)
                    # print("Transcription: ", text)

            

                    fs.delete(filename)

                    messages.success(request, 'Text Extractted Successfully !')
                    return render(request, 'showText.html', {'extracted_text': text})

                else:

                    # Save the uploaded file to a temporary location
                    temporary_file_path = 'media/temporary_file'
                    
                    with open(temporary_file_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)

                    # Determine file format and extract text accordingly
                    if uploaded_file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                        # DOCX file
                        text = docx2txt.process(temporary_file_path)

                    elif uploaded_file.content_type == 'application/pdf':
                        # PDF file using PyPDF2
                        reader = PdfReader(temporary_file_path)
                        text = ''
                        for page in reader.pages:
                            text += page.extract_text()

                    elif uploaded_file.content_type == 'text/plain':
                        # TXT file
                        with open(temporary_file_path, 'r') as f:
                            text = f.read()

            elif request.POST.get('textarea'):
                temporary_file_path = 'media/temporary_file/example.txt'
                
                # Extract text from the textarea
                text = request.POST['textarea']

                messages.success(request, 'Text Extractted Successfully !')
                return render(request, 'showText.html', {'extracted_text': text})
            

            else:
                return HttpResponse('No file uploaded and no text entered.') 

                    
                
        # else:               
        #     messages.success(request, 'Unsupported file format !')

            
                
            os.remove(temporary_file_path)

            messages.success(request, 'Text Extractted Successfully !')
            
            return render(request, 'showText.html', {'extracted_text': text})

            
    except Exception as e:
        # Handle exceptions (e.g., file not found, extraction error)
        messages.error(request, 'Incorrect File Format: {}'.format(str(e)))
        return render(request, 'showText.html')            
                   


def summarization(request):
    if request.method == 'POST':
        global extract_text
        # Get the article text from the form data
        article_text = request.POST.get('extracted_text', '')


        # Preprocessing steps

        # Removing Square Brackets and Extra Spaces
        article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
        article_text = re.sub(r'\s+', ' ', article_text)
        # Removing special characters and digits
        formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
        formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)
        extract_text = formatted_article_text
        sentence_list = nltk.sent_tokenize(article_text)
        stopwords = nltk.corpus.stopwords.words('english')

        word_frequencies = {}
        for word in nltk.word_tokenize(formatted_article_text):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
            maximum_frequncy = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)
            sentence_scores = {}
        for sent in sentence_list:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]
        import heapq
        summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)

        formatted_sentences = ['- ' + sentence for sentence in summary_sentences]

        formatted_sum_text = '\n'.join(formatted_sentences)

        # summary = ' '.join(summary_sentences)
        # output_text = re.sub(r'\W', ' ', str(summary))

        messages.success(request, 'Summary Generated Successfully !')

        return render(request, 'showSumText.html', {'sum_text': formatted_sum_text, 'extracted_text': article_text})
    
def base(request):
    return render(request, 'base.html')

def question(request):
    return render(request,'question_page.html')

def answer_generation(request):
    if request.method == 'POST':

        qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")

        context = str(extract_text)

        messages.success(request, 'Text Extractted Successfully !')
        
        question = request.POST.get('textarea', '')
        question = str(question)
        if "?" in question:
            query = question
        else:
            query = question + "?"

        result = qa_pipeline(question=query, context=context)

        return render(request, 'answer_page.html', {'query_result': result['answer']})
    
def home(request):
    return render(request, 'base.html')

def logout_view(request):
    logout(request)
    return render(request, 'login.html')
    

    