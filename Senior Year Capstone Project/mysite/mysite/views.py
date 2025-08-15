from django.http import HttpResponse
from django import template
from django.template import loader
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from pytube import YouTube as YT
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import librosa
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def index(request):
    return HttpResponse("Hello World!")