

"""

green = np.uint8([[[0,130,120]]])
hsv_green = cv.cvtColor(green,cv.COLOR_BGR2HSV)
print( hsv_green )

img = cv.imread('greencircle.jpg',0)
ret,thresh = cv.threshold(img,127,255,0)
contours,hierarchy = cv.findContours(thresh, 1, 2)
cnt = contours[0]
M = cv.moments(cnt)
print( M )

x,y,w,h = cv.boundingRect(cnt)
cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

"""

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


def find_histogram(clt):
    """
    create a histogram with k clusters
    :param: clt
    :return:hist
    """
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)

    hist = hist.astype("float")
    hist /= hist.sum()

    return hist
def plot_colors2(hist, centroids):
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0

    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv.rectangle(bar, (int(startX), 0), (int(endX), 50),
                      color.astype("uint8").tolist(), -1)
        startX = endX

    # return the bar chart
    return bar


cap = cv.VideoCapture(0)
while(1):
    # Take each frame
    _, frame = cap.read()
    # Convert BGR to HSV
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
     # hsv = frame
    # define range of green color in HSV
    lower_green = np.array([30,50,50])
    upper_green = np.array([90,255,255])
    # Threshold the HSV image to get only green colors
    mask = cv.inRange(hsv, lower_green, upper_green)
    # Create bounding rectangle
     # ret,thresh = cv.threshold(mask,127,255,0)
    

    thresh = mask
    contours,hierarchy = cv.findContours(thresh, 1, 2)

    if len(contours) == 0:
        continue

    for cnt in contours:
        x,y,w,h = cv.boundingRect(cnt)
        cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)


    # Bitwise-AND mask and original image
    res = cv.bitwise_and(frame,frame, mask= mask)

    img = cv.cvtColor(res, cv.COLOR_BGR2RGB)

    img = img.reshape((img.shape[0] * img.shape[1],3)) #represent as row*column,channel number
    clt = KMeans(n_clusters=3) #cluster number
    clt.fit(img)

    hist = find_histogram(clt)
    bar = plot_colors2(hist, clt.cluster_centers_)

    #plt.axis("off")
    cv.imshow('bar',bar)
    cv.imshow('frame',frame)
    #plt.show()

    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break
cv.destroyAllWindows()


