import cv
import cv2
import time
from PIL import Image
import numpy as np
import csv
import logistic
import mouthdetection as m
import json
import sys
import inspect
import os

WIDTH, HEIGHT = 28, 10  # all mouth images will be resized to the same size
dim = WIDTH * HEIGHT  # dimension of feature vector

path_to_file = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))

CONFIG = json.loads(sys.argv[1])
# print(CONFIG)


def get_config(key):
  return CONFIG[key]


def to_node(type, message):
  # convert to json and print (node helper will read from stdout)
  try:
    print(json.dumps({type: message}))
  except Exception:
    pass
  # stdout has to be flushed manually to prevent delays in the node helper
  # communication
  sys.stdout.flush()

to_node("test", CONFIG)

"""
pop up an image showing the mouth with a blue rectangle
"""


def show(area):
  cv.Rectangle(img, (area[0][0], area[0][1]),
               (area[0][0] + area[0][2], area[0][1] + area[0][3]),
               (255, 0, 0), 2)
  cv.NamedWindow('Face Detection', cv.CV_WINDOW_NORMAL)
  cv.ShowImage('Face Detection', img)
  cv.WaitKey()

"""
given an area to be cropped, crop() returns a cropped image
"""


def crop(area):
  crop = img[area[0][1]:area[0][1] + area[0][3], area[0]
             [0]:area[0][0] + area[0][2]]  # img[y: y + h, x: x + w]
  return crop

"""
given a jpg image, vectorize the grayscale pixels to 
a (width * height, 1) np array
it is used to preprocess the data and transform it to feature space
"""


def vectorize(filename):
  size = WIDTH, HEIGHT  # (width, height)
  im = Image.open(filename)
  resized_im = im.resize(size, Image.ANTIALIAS)  # resize image
  im_grey = resized_im.convert('L')  # convert the image to *greyscale*
  im_array = np.array(im_grey)  # convert to np array
  oned_array = im_array.reshape(1, size[0] * size[1])
  return oned_array


"""
load training data
"""
# create a list for filenames of smiles pictures
smilefiles = []
with open(path_to_file + '/smiles.csv', 'rb') as csvfile:
  for rec in csv.reader(csvfile, delimiter='	'):
    smilefiles += rec

# create a list for filenames of neutral pictures
neutralfiles = []
with open(path_to_file + '/neutral.csv', 'rb') as csvfile:
  for rec in csv.reader(csvfile, delimiter='	'):
    neutralfiles += rec

# N x dim matrix to store the vectorized data (aka feature space)
phi = np.zeros((len(smilefiles) + len(neutralfiles), dim))
# 1 x N vector to store binary labels of the data: 1 for smile and 0 for
# neutral
labels = []

# load smile data
DATAPATH = path_to_file + "/../data/"
for idx, filename in enumerate(smilefiles):
  phi[idx] = vectorize(DATAPATH + "smile/" + filename)
  labels.append(1)

# load neutral data
# PATH = "../data/neutral/"
offset = idx + 1
for idx, filename in enumerate(neutralfiles):
  phi[idx + offset] = vectorize(DATAPATH + "neutral/" + filename)
  labels.append(0)

"""
  training the data with logistic regression
  """
lr = logistic.Logistic(dim)
lr.train(phi, labels)

"""
  open webcam and capture images
  """
cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened():  # try to get the first frame
  rval, frame = vc.read()
else:
  rval = False

# print "\n\n\n\n\npress space to take picture; press ESC to exit"
# print("emotion detection")

while True:  # rval:
  time.sleep(2)  # get_config("interval"))
  cv2.imshow("preview", frame)
  rval, frame = vc.read()
  # key = cv2.waitKey(40)
  # print(key)
  # if key == 27:  # exit on ESC
  # break
  # if key == 32:  # press space to save images
  cv.SaveImage("webcam.jpg", cv.fromarray(frame))
  img = cv.LoadImage("webcam.jpg")  # input image
  mouth = m.findmouth(img)
  # show(mouth)
  if mouth != 2:  # did not return error
    mouthimg = crop(mouth)
    cv.SaveImage("webcam-m.jpg", mouthimg)
    # predict the captured emotion
    result = lr.predict(vectorize('webcam-m.jpg'))
    if result == 1:
      to_node("result", {"smiling": True})
      # print "you are smiling! :-) "
    else:
      to_node("result", {"smiling": False})
      # print "you are not smiling :-| "
  else:
    # error message
    to_node("error", {"message": "failed to detect mouth."})
    # print "failed to detect mouth. Try hold your head straight and make sure
    # there is only one face."

# cv2.destroyWindow("preview")
