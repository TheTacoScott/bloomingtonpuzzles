import argparse
import cv2
from math import sqrt
import requests
from PIL import Image
from StringIO import StringIO
import numpy as np

parser = argparse.ArgumentParser(description='')
parser.add_argument('--palette', action="store", dest="palette")
parser.add_argument('--urls', action="store", dest="urls")
args = parser.parse_args()

color_lookup = {}
def find_color(x1,y1,z1):
  x1 = float(x1)
  y1 = float(y1)
  z1 = float(z1)
  best_distance = None
  color = None
  for (x,y,z) in color_lookup:
    dist = distance(x,y,z,x1,y1,z1)
    if not color:
      color = color_lookup[(x,y,z)]
      best_distance = dist
    else:
      if dist < best_distance:
        color = color_lookup[(x,y,z)]
        best_distance = dist
  return color
    
def distance(x,y,z,x2,y2,z2):
  return sqrt((x - x2)**2 + (y - y2)**2 + (z - z2)**2)

with open(args.palette, "r") as f:
  for line in f:
    (points,text) = line[0:-1].split("\t")
    (x,y,z) = points.split(",")
    x = float(x)
    y = float(y)
    z = float(z)
    color_lookup[(x,y,z)] = text

star = cv2.StarDetector()
with open(args.urls, "r") as f:
  for index,line in enumerate(f):
    (url,text) = line[0:-1].split("\t")
    r = requests.get(url)
    im = Image.open(StringIO(r.content))
    imcolor = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    imgray = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY)
    xp = []
    yp = []
    points = star.detect(imgray)
    for point in points:
      (x,y) = (point.pt[0],point.pt[1])
      xp.append(x)
      yp.append(y)
      cv2.circle(imcolor,(int(x),int(y)),10,(0,255,0))
      print x,y
    if len(points) > 0:
      (cx,cy) = (sum(xp) / len(points), sum(yp) / len(points))
    else:
      print imgray.shape
      (cy,cx) = imgray.shape
      cx = cx / 2
      cy = cy / 2
    cv2.circle(imcolor,(int(cx),int(cy)),10,(0,0,255))
    cv2.imwrite("/mnt/mondo/tmp/{0}.jpg".format(index),imcolor)

