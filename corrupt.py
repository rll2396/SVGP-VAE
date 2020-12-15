from pytube import YouTube  
import pytube
import imageio
import matplotlib.pyplot as plt
import random
import numpy as np
import os
import pickle
import glob
from pathlib import Path
from shutil import copyfile

def corrupt_video(filename, frames = "random", frame_percent = 30, video_percent = 30, framerange = 'all'):
    '''
    "Corrupts" video file and returns the video with corrupt frames, as well as the frame rate
    parameters:
    filename: file path for entire video
    frames: a list of specific frames or "random" if a random set of frames are to be corrupted
    frame_percent: percent of each frame to be corrupted
    video_percent: percent of total video to have corrupted frames; ignored if frames is not "random"
    framerange: 'all' or a list [a, b] that tells the function to take all frames between a and b only
    '''
    vid = imageio.get_reader(filename,  'ffmpeg')
    fps = vid.get_meta_data()['fps']
    a = 12345
    random.seed(a=a)
    meta = vid.get_meta_data()
    frate = meta['fps']
    nframes = meta['nframes']
    
    if framerange == 'all':
        framerange = range(nframes-2)
    else:
        framerange = range(framerange[0],framerange[1])
        
    frameslist = np.arange(len(framerange))
    size = meta['size']
    imlist = np.zeros((len(framerange), size[1], size[0]), dtype=np.float64)
    
    if frames == "random":
        random.shuffle(frameslist)
        lim = int(np.round(nframes*video_percent/100))    
        frameslist = frameslist[:lim]
    else:
        frameslist = frames

    for frame in range(len(framerange)-1):
        a+=1
        random.seed(a=a)
        if frame in frameslist:
            image = vid.get_data(frame)
            l, w = image.shape[:2]
            k = int(np.round(l*w*frame_percent/100))
            im = corrupt_frame(image, l, w, frame_percent)
        else:
            im = vid.get_data(frame)
        imlist[frame] = im[:,:,1]
    return imlist, fps
        
def corrupt_frame(image, l, w, frame_percent):
    '''corrupts image up to a given frame_percent'''
    im = np.copy(image)
    vals = np.array([[i, j] for i in range(l) for j in range(w)])
    vlist = np.arange(len(vals))
    random.shuffle(vlist)
    fp = int(np.round(l*w*frame_percent/100))
    corrupt_cords = vals[vlist][:fp]
    corrupt = [tuple(corrupt_cords[i]) for i in range(len(corrupt_cords))]
    for coord in corrupt:
        im[coord] = [0,0,0]
    return im

def generate_video(img, videoname, fps = 30):
    '''save a corrupted video
    parameters:
    img: list of frames to save into a video
    videoname: path + name of video to be saved
    fps: fps of video
    '''
    writer = imageio.get_writer(videoname, format='FFMPEG', fps = fps)
    for im in img:
        writer.append_data(im)
    writer.close()
    
def run():
    # install ffmpeg plugin if needed
    imageio.plugins.ffmpeg.download()
#     link of the video to be downloaded  
    link = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    root = os.getcwd()
    filename = root + '\Rick Astley - Never Gonna Give You Up (Video).mp4'
#     link = "https://www.youtube.com/watch?v=QC8iQqtG0hg"
#     https://stackoverflow.com/questions/49643206/attributeerror-youtube-object-has-no-attribute-get-videos
#     download video
    if not os.path.exists(filename):
        yt = pytube.YouTube(link)
        stream = yt.streams.first()
        stream.download()
    
    frames = "random"
    video_percent = 0
    frame_percent = 30
    # filename = fpath
#     filename = root + "\\5 Second Video Watch the Milky Way Rise.mp4"
#     generate list of all frames from video, takes a couple minutes for the 5 min. video I was testing, and takes 
# longer if you corrupt more frames. Could probably be improved.
    print("generating corruption")
    imlist, fps = corrupt_video(filename, frames = frames, frame_percent = frame_percent,
                                video_percent = video_percent, framerange=[65,185])
    
#--------------cropping video-------------------------------------------------    
    horiz_width = 60
    vert_width = 60
    
    orig_horiz, orig_vert = imlist.shape[1], imlist.shape[2]
    
    hw1, hw2 = (orig_horiz - horiz_width)//2, (orig_horiz + horiz_width)//2
    vw1, vw2 = (orig_vert - vert_width)//2, (orig_vert + vert_width)//2
    
    imlist = imlist[:,hw1:hw2, vw1:vw2]
#-------------------------------------------------------------------------------
    
    #videoname = root + "\\test.mp4"
    images = imlist.reshape(imlist.shape+(1,))
    print(images.shape)
    aux_data = np.arange(len(imlist), dtype=np.float64).reshape(len(imlist), 1)
    print("saving video")
#     save video, takes a while on longer videos
    dataset = {'images':images, 'aux_data':aux_data}
    Path("test data").mkdir(parents=True, exist_ok=True)
    with open("test data/train_data3.p", 'wb+') as test_pickle:
        pickle.dump(dataset, test_pickle)
    copyfile("test data/train_data3.p", "test data/test_data3.p")
    copyfile("test data/train_data3.p", "test data/eval_data3.p")
    copyfile("MNIST data/train_ids_mask3.p", "test data/train_ids_mask3.p")
    
    
if __name__ == "__main__":
    run()