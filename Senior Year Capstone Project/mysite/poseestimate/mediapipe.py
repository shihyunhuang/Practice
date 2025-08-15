import os
from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
from django.views.decorators.csrf import ensure_csrf_cookie
import mediapipe as mp
import cv2
from django.http import FileResponse
import os
from pytube import YouTube
from django.shortcuts import render, redirect
from .forms import YouTubeLinkForm
from django.http import JsonResponse

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

@ensure_csrf_cookie
def upload_display_video(request):
    
    if request.method == 'POST':
        if 'upload_form' in request.POST:
            upload_form = UploadFileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                file = request.FILES['file']
                handle_uploaded_file(file)
                output_video_path = process_local_video(file.name)          
                return render(request, "local.html", {'filename': file.name, 'processed_path': output_video_path})

        if 'youtube_form' in request.POST:
            youtube_form = YouTubeLinkForm(request.POST)
            if youtube_form.is_valid():
                youtube_link = youtube_form.cleaned_data['link']
                output_video_path = process_youtube_video(youtube_link)
                return render(request, 'local.html', {'processed_path': output_video_path})

    return render(request, 'local.html', {'upload_form': upload_form, 'youtube_form': youtube_form})
    
def handle_uploaded_file(f):
    with open(f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def process_youtube_video(video_url):

    output_video_path = "output.mp4"
    # Create a YouTube object
    yt = YouTube(
        video_url,
        use_oauth=True,
        allow_oauth_cache=True
    )

    # Access the highest resolution stream
    selected_stream = yt.streams.filter(res="480p", file_extension="mp4").first()

    # Download the video
    video_path=selected_stream.download()

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = frame
        results = holistic.process(image)

        # Draw landmarks and connections
        mp_drawing = mp.solutions.drawing_utils
    
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2))
    
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2))
    
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

        out.write(image)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
        
    return output_video_path

def process_local_video(filename):
    input_video_path = filename
    output_video_path = f"processed_{filename}"

    cap = cv2.VideoCapture(input_video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = frame
        results = holistic.process(image)

        # Draw landmarks and connections
        mp_drawing = mp.solutions.drawing_utils

        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                  mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2))

        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                                  mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2))

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                                  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

        out.write(image)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
        
    return output_video_path