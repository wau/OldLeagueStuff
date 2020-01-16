from pytube import YouTube, Playlist
import sys
import os
import dask.array as da
import cv2
import logging

logger = logging.getLogger()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [youtube] %(message)s",
    handlers=[
        logging.StreamHandler()
    ])

class Video_Download():

    def __init__(self, path, print_progress=True, resolution=(1280,720), target_resolution=(1280,720), crop=None, fps=60, adaptive=True):
        self.print_progress = print_progress
        self.resolution = resolution
        self.target_resolution = target_resolution
        self.fps = fps
        self.adaptive = adaptive
        self.path = path
        self.crop = crop
        
    def download_videos(self, videos):
        num_videos = len(videos)
        i = 1
        for video in videos:
            yt = YouTube(video)
            if self.print_progress is True:
                yt.register_on_progress_callback(self._show_progress_bar)
                print(f"Starting video download {i} of {num_videos}: \n")
            yt.streams.filter(resolution=self.resolution[1], adaptive=self.adaptive, fps=self.fps).all()
            yt.streams.first().download(self.path)
            i+=1

    def _show_progress_bar(self, stream, chunk, file_handle, bytes_remaining):
        current = ((stream.filesize - bytes_remaining)/stream.filesize)
        percent = ('{0:.1f}').format(current*100)
        progress = int(50*current)
        status = '█' * progress + '-' * (50 - progress)
        sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
        sys.stdout.flush()  

    def process_videos(self, video_path, dest_path, skip=0):
        video_num = 1
        for video in os.listdir(video_path):
            if not video.startswith('.'):
                #do something
                vidcap = cv2.VideoCapture(video_path+video)
                total = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
                success,image = vidcap.read()
                count = 1
                skip+=1
                while success:
                    if count%skip == 0:
                        if self.resolution != self.target_resolution:
                            if self.crop != None:
                                image = cv2.resize(image, dsize=(self.target_resolution[1], self.target_resolution[0]), interpolation=cv2.INTER_CUBIC)
                                image = image[int(self.target_resolution[0]/2-self.crop[0]/2):int(self.target_resolution[0]/2-self.crop[0]/2)+self.crop[0], 
                                            int(self.target_resolution[1]/2-self.crop[1]/2):int(self.target_resolution[1]/2-self.crop[1]/2)+self.crop[1]]

                            else:
                                image = cv2.resize(image, dsize=(self.target_resolution[1], self.target_resolution[0]), interpolation=cv2.INTER_CUBIC)
                        cv2.imwrite(dest_path+f'{video[:-3].replace(" ", "")}im_{count}.png', image)   # save frame as JPEG file
                    count += 1
                    self._show_process_bar(count, total, video_num)
                    success,image = vidcap.read()
                video_num+=1
                count=0

    def _show_process_bar(self, current, total, video):
        current = (total - (total-current))/total
        percent = ('{0:.1f}').format(current*100)
        progress = int(50*current)
        status = '█' * progress + '-' * (50 - progress)
        sys.stdout.write('Processing video: {video} ↳ |{bar}| {percent}%\r'.format(video=video, bar=status, percent=percent))
        sys.stdout.flush()  