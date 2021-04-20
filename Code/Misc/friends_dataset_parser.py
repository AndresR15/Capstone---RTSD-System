import pandas as pd
import subprocess
from moviepy.editor import *
from tqdm import tqdm
from textblob import TextBlob

from features import stFeatureExtraction
from helper import get_audio, pad_sequence_into_array

import numpy as np

from os import listdir
from os.path import isfile, join

# data_path = "F:/Capstone Project/Capstone---RTSD-System/Data/MELD.Raw/train_splits/" #+ "dia0_utt0.mp4"
# output_audio_path = "F:\Capstone Project\Capstone---RTSD-System\Data\MELD.Raw/audio/"# + "test_audio.wav"

def extract_audio(data_path, output_audio_path):
    skipped = 0
    for file in tqdm(listdir(data_path)):
        file_path = join(data_path, file)
        if isfile(file_path) and ".mp4" in file:
            try:
                file_wav = output_audio_path + str(file.split(".")[0]) + ".wav"

                audioclip = AudioFileClip(file_path)
                _ = audioclip.write_audiofile(file_wav, verbose=False, logger=None)
            except:
                skipped += 1
                print("skipping " + str(file))
                print("skipped total = " + str(skipped))

def extract_features(csv_file_path, output_audio_path, limit=1000):

    label_df = pd.read_csv(csv_file_path)
    wav_in = []
    labels = []
    transcription = []

    skipped = 0
    for _ , sample in tqdm(label_df[["Utterance", "Emotion", "Dialogue_ID", 'Utterance_ID']][:limit].iterrows()):

        if sample["Emotion"] in ["disgust", "joy", "fear"]:
            continue # skip any emotion that we're not using for testing
        try:
            audio_path = "dia" + str(sample['Dialogue_ID']) + "_utt" + str(sample['Utterance_ID']) + ".wav"

            wav = get_audio(output_audio_path, audio_path)
            (nchannels, sampwidth, framerate, nframes, comptype, compname), samples_wav = wav

            st_features = calculate_features(samples_wav[0::nchannels], framerate)
            st_features, _ = pad_sequence_into_array(st_features, maxlen=100)

            wav_in.append(st_features.T)
            labels.append(sample["Emotion"])
            transcription.append(sample["Utterance"])
        except:
            skipped += 1
            print("skipped total = " + str(skipped))

    features = np.array(wav_in)
    labels = np.array(labels)
    transcription = np.array(transcription)
    return labels, features, transcription


def calculate_features(frames, freq):
    window_sec = 0.1
    window_n = int(freq * window_sec)

    st_f = stFeatureExtraction(frames, freq, window_n, window_n / 2)

    if st_f.shape[1] > 2:
        i0 = 1
        i1 = st_f.shape[1] - 1
        if i1 - i0 < 1:
            i1 = i0 + 1

        deriv_st_f = np.zeros((st_f.shape[0], i1 - i0), dtype=float)
        for i in range(i0, i1):
            i_left = i - 1
            i_right = i + 1
            deriv_st_f[:st_f.shape[0], i - i0] = st_f[:, i]
        return deriv_st_f
    elif st_f.shape[1] == 2:
        deriv_st_f = np.zeros((st_f.shape[0], 1), dtype=float)
        deriv_st_f[:st_f.shape[0], 0] = st_f[:, 0]
        return deriv_st_f
    else:
        deriv_st_f = np.zeros((st_f.shape[0], 1), dtype=float)
        deriv_st_f[:st_f.shape[0], 0] = st_f[:, 0]
        return deriv_st_f

csv_path = 'F:\Capstone Project\Capstone---RTSD-System\Data\MELD.Raw/train_sent_emo.csv'
audio_path = 'F:\Capstone Project\Capstone---RTSD-System\Data\MELD.Raw/audio/'
output_features, labels, transcription = extract_features(csv_path, audio_path)
np.save(audio_path + "../train_features", ([output_features], labels, transcription), allow_pickle=True)
