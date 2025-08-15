from django.http import HttpResponse
from django import template
from django.template import loader
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings

import mediapipe as mp
from pytube import YouTube as YT
from moviepy.editor import VideoFileClip, AudioFileClip
import librosa
import os
import cv2
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

@ensure_csrf_cookie
#首頁登入
def home(request):
    if request.method=="POST":
        form_name = request.POST.get('form_name')
        if form_name == 'file_upload':
            uploaded_file = request.FILES['file']

            #參數設定
            name_video = uploaded_file.name
            name_audio = name_video.replace('.mp4', '.wav')
            filename = name_video.replace('.mp4', '')

            #創一個資料夾
            output_folder = os.path.join(settings.MEDIA_ROOT, filename)
            os.makedirs(output_folder, exist_ok=True)

            # 儲存上傳的 MP4 檔案
            fss = FileSystemStorage(location=output_folder)
            file = fss.save(uploaded_file.name, uploaded_file)

            # 轉換 MP4 到 WAV
            input_video_path = os.path.join(output_folder, name_video)
            output_audio_path = os.path.join(output_folder, name_audio)

            video = VideoFileClip(input_video_path)
            audio = video.audio
            audio.write_audiofile(output_audio_path)

            #session設定
            request.session['videoname'] = name_video
            request.session['audioname'] = name_audio
            request.session['filename'] = filename
            

        elif form_name == 'url_input':
             # getting link from frontend
            link = request.POST['link']
            yt = YT(link, use_oauth=True, allow_oauth_cache=True)

            cleaned_title = yt.title.replace('/', '')
            name_video = cleaned_title + ".mp4"
            name_audio = cleaned_title + ".wav"
            #創一個資料夾
            output_folder = os.path.join(settings.MEDIA_ROOT, cleaned_title)
            os.makedirs(output_folder, exist_ok=True)
            #下載影片以及音樂
            yt.streams.filter().get_highest_resolution().download(output_path=output_folder, filename = name_video)
            yt.streams.filter().get_audio_only().download(output_path=output_folder, filename = name_audio)

            #session設定
            request.session['videoname'] = name_video
            request.session['audioname'] = name_audio
            request.session['filename'] = cleaned_title

            # returning HTML page
        return redirect('videocutting')
    return render(request, 'home.html')

#開啟鏡頭分析股價
def pose(request):
    template = get_template('pose.html')
    return HttpResponse(template.render())

"""
上傳檔案
def upload(request):
    if request.method=="POST":
        uploaded_file = request.FILES['file']

        #參數設定
        name_video = uploaded_file.name
        name_audio = name_video.replace('.mp4', '.wav')
        filename = name_video.replace('.mp4', '')

        #創一個資料夾
        output_folder = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(output_folder, exist_ok=True)

        # 儲存上傳的 MP4 檔案
        fss = FileSystemStorage(location=output_folder)
        file = fss.save(uploaded_file.name, uploaded_file)

        # 轉換 MP4 到 WAV
        input_video_path = os.path.join(output_folder, name_video)
        output_audio_path = os.path.join(output_folder, name_audio)

        video = VideoFileClip(input_video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)

        #session設定
        request.session['videoname'] = name_video
        request.session['audioname'] = name_audio
        request.session['filename'] = filename
        return redirect('videocutting')
    return render(request, "home.html")

#下載youtube影片音樂
def youtube(request):
  
    # checking whether request.method is post or not
    if request.method == 'POST':
        # getting link from frontend
        link = request.POST['link']
        yt = YT(link, use_oauth=True, allow_oauth_cache=True)

        cleaned_title = yt.title.replace('/', '')
        name_video = cleaned_title + ".mp4"
        name_audio = cleaned_title + ".wav"
        #創一個資料夾
        output_folder = os.path.join(settings.MEDIA_ROOT, cleaned_title)
        os.makedirs(output_folder, exist_ok=True)
        #下載影片以及音樂
        yt.streams.filter().get_highest_resolution().download(output_path=output_folder, filename = name_video)
        yt.streams.filter().get_audio_only().download(output_path=output_folder, filename = name_audio)

        #session設定
        request.session['videoname'] = name_video
        request.session['audioname'] = name_audio
        request.session['filename'] = cleaned_title

        # returning HTML page
        return redirect('videocutting')
    
    return render(request, 'youtube.html')
"""

#影片切割
def videocutting(request):
    #取得session數值
    videoname = request.session.get('videoname', 'Guest')
    audioname = request.session.get('audioname', 'Guest')
    filename = request.session.get('filename', 'Guest')
    #設定路徑
    video_file_path = os.path.join(settings.MEDIA_ROOT, filename, videoname)
    audio_file_path = os.path.join(settings.MEDIA_ROOT, filename, audioname)

    if request.method == "POST":
        #讀取參數
        #startmin = request.POST['startmin']
        startsec = request.POST['startsec']
        #endmin = request.POST['endmin']
        endsec = request.POST['endsec']

        #參數型態轉換
        #intstartmin = int(startmin)
        totalstartsec = float(startsec)
        #intendmin = int(endmin)
        totalendsec = float(endsec)
        #totalstartsec = intstartmin * 60 + intstartsec
        #totalendsec = intendmin * 60 + intendsec
        p = 0

        #分析bpm
        y, sr = librosa.load(audio_file_path)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        #切割bpm數值整理
        while beat_times[p] < totalstartsec:
            p = p + 1
        q = p
        while beat_times[q] < totalendsec:
            q = q + 1

        #切割影片
        video = VideoFileClip(video_file_path)
        output = video.subclip(beat_times[p], beat_times[q])
        output_name = 'output_without_pose.mp4'
        output_filepath = os.path.join(settings.MEDIA_ROOT, filename, output_name)
        output.write_videofile(output_filepath, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")

        #切割音樂
        audio = AudioFileClip(audio_file_path)
        output_music = audio.subclip(beat_times[p], beat_times[q])
        output_music_name = 'cut_music.mp3'
        output_music_filepath = os.path.join(settings.MEDIA_ROOT, filename, output_music_name)
        output_music.write_audiofile(output_music_filepath, codec='mp3')

        #儲存剪輯節拍的每個秒數
        bpm_times = []
        while p <= q:
            bpm_times.append(beat_times[p])
            p = p + 1

        process_video(output_filepath, output_music_filepath, filename)   

        request.session['bpm_times'] = bpm_times
        request.session['tempo'] = tempo

        return redirect('learning')

    context = {
            'MEDIA_URL': settings.MEDIA_URL,
            'filename': filename,
            'videoname': videoname,
        }
    
    return render(request, 'videocutting.html', context)

def process_video(output_filepath, output_music_filepath, filename):
    #輸出骨架影片
    video = output_filepath
    music = output_music_filepath
    cap = cv2.VideoCapture(video)

    #確保捕獲了足夠的視頻幀
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Number of frames in the video: {frame_count}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    fixed_fps = round(fps)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    filepath = os.path.join(settings.MEDIA_ROOT, filename, 'output_with_pose.mp4')
    out = cv2.VideoWriter(filepath, fourcc, fixed_fps, (width, height))

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

    # 合併影片與聲音
    video_clip = VideoFileClip(filepath)
    video_clip = video_clip.set_audio(AudioFileClip(music))
    output_filepath = os.path.join(settings.MEDIA_ROOT, filename, 'output.mp4')
    video_clip.write_videofile(output_filepath, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")

def learning(request):
    filename = request.session.get('filename', 'Guest')
    bpm_times = request.session.get('bpm_times', 'Guest')
    tempo =  request.session.get('tempo', 'Guest')
    countdowntime = (60 / int(tempo)) * 1000

    a = len(bpm_times)
    total_times = (bpm_times[a - 1] - bpm_times[0]) / 100
    #每個節拍位在的百分比
    bpm_percent = [{'id': i, 'left': (bpm_times[i] - bpm_times[0]) / total_times, 'content': i} for i in range(a)]
    #回傳影片
    context = {
        'MEDIA_URL': settings.MEDIA_URL,
        'filename': filename,
        'bpm_percent': bpm_percent,
        'countdowntime': countdowntime,
    }

    return render(request, 'learning.html', context)
# Create your views here.