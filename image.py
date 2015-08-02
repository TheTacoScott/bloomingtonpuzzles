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
    (l,a,b) = points.split(",")
    lab = np.array([[[l,a,b]]],dtype=np.float32)
    (r,g,b) = cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)[0][0]
    r = int(r *  255)
    g = int(g *  255)
    b = int(b *  255)
    color_lookup[(r,g,b)] = text

star = cv2.StarDetector()

with open(args.urls, "r") as f:
  for index,line in enumerate(f):
    (url,text) = line[0:-1].split("\t")
    r = requests.get(url)
    im = Image.open(StringIO(r.content))

    imbgr = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    imstar = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    imgray = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2GRAY)

    xp = []
    yp = []
    corners = cv2.goodFeaturesToTrack(imgray,25,0.01,10)
    corners = np.int0(corners)
    for i in corners:
      (x,y) = i.ravel()
      xp.append(x)
      yp.append(y)
    points = star.detect(imgray)
    #imstar = cv2.drawKeypoints(imstar,star.detect(imgray))
    for point in points:
      (x,y) = (int(point.pt[0]),int(point.pt[1]))
      xp.append(x)
      yp.append(y)
    if len(xp) > 0:
      (cx,cy) = (sum(xp) / len(xp), sum(yp) / len(xp))
    else:
      (cy,cx) = imgray.shape
      cx = cx / 2
      cy = cy / 2

    for x,y in zip(xp,yp):
      cv2.circle(imstar,(int(x),int(y)),10,(255,0,0))
    cv2.circle(imstar,(int(cx),int(cy)),10,(0,255,0))
    b,g,r = imbgr[cx,cy]
    print index,find_color(r,g,b),(r,g,b),(b,g,r)
    cv2.imwrite("/mnt/mondo/tmp/star{0}.jpg".format(index),imstar)
