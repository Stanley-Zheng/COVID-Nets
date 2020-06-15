import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from imutils import paths
import tensorflow as tf
from tensorflow import keras
import shutil
from cv2 import cv2

tf.config.experimental.list_physical_devices('GPU')
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

keras.backend.clear_session()
workingDirectory = os.path.dirname(os.path.realpath(__file__))
covidPath = os.path.sep.join([f'{workingDirectory}', 'COVID-19 Radiography Database', 'COVID-19'])
normalPath = os.path.sep.join([f'{workingDirectory}', 'COVID-19 Radiography Database', 'NORMAL'])
testPath = os.path.sep.join([f'{workingDirectory}', 'COVID-19 Radiography Database', 'TEST'])
normalImages = list(paths.list_images(f'{normalPath}'))
covidImages = list(paths.list_images(f'{covidPath}'))
images = []
labels = []

def makeDataset(workingDirectory = workingDirectory): #Combines all COVID images into one singular dataset to make it easier to process
    global covidPath
    global normalPath
    imagePath = os.path.sep.join([f'{workingDirectory}', 'covid-chestxray-dataset', 'images'])
    covidPath = os.path.sep.join([f'{workingDirectory}', 'COVID-19 Radiography Database', 'COVID-19'])
    normalPath = os.path.sep.join([f'{workingDirectory}', 'COVID-19 Radiography Database', 'NORMAL'])
    for row in pd.read_csv(os.path.sep.join([f'{workingDirectory}', 'covid-chestxray-dataset', 'metadata.csv'])).iterrows():#Add covid-chestxray-dataset and metadata.csv to current working directory
        if row['finding'] != 'COVID-19' or row['view'] != 'PA':#Skip everything except if the case is COVID-19 and is in PA view. 
            continue
        singleImagePath = os.path.sep.join([imagePath, row['filename']])
        if not os.path.exists(imagePath):
            continue
        filename = row['filename'].split(os.path.sep)[-1]
        outputPath = os.path.sep.join([f'{covidPath}', filename])
        shutil.copy2(singleImagePath, outputPath)
    print('finished copying.')
    print('creating test files')


def ceildiv(a, b):
    return -(-a // b)

def plotImages(imagePath, figureSize=(10,5), rows=5, titles=None, mainTitle=None, number = 20): #Plots a 5x4 grid of images (not processed)
    f = plt.figure(figsize=figureSize)
    if mainTitle is not None: plt.suptitle(mainTitle, fontsize=50)
    for i in range(0, number):
        sp = f.add_subplot(rows, ceildiv(number, rows), i+1)
        sp.axis('Off')
        if titles is not None: sp.set_title(titles[i], fontsize=16)
        img = plt.imread(imagePath[i])
        plt.imshow(img)

def processImages(normalImages = normalImages, covidImages = covidImages): #converts image directories to resized greyscale numpy arrays
    global images
    global labels
    for i in covidImages:
        label = i.split(os.path.sep)[-2]
        image = cv2.imread(i)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#Turn image into greyscale to save memory
        image = cv2.resize(image,(480, 480)) #Resizes images to 240x240 to save memory. 
        images.append(image)
        labels.append(label)
    for i in normalImages:
        label = i.split(os.path.sep)[-2]
        image = cv2.imread(i)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #Turn image into greyscale to save memory. 
        image = cv2.resize(image,(480, 480))
        images.append(image)
        labels.append(label)
    images = np.asarray(images)
    labels = np.asarray(labels)

def plotArray (nparray, pos): #For a 3d numpy array, plots the image with a colorbar.
    plt.figure()
    plt.imshow(nparray[pos])
    plt.colorbar()
    plt.grid(False)
    plt.show()

def buildModel():
    global labels
    global images
    labels = [1 if x=='COVID-19' else x for x in labels]
    labels = [0 if x=='NORMAL' else x for x in labels]
    labels = np.asarray(labels)
    images = images / 255.0

    model = keras.Sequential([
    #    keras.layers.Flatten(input_shape=(480, 480, 3)),
        keras.layers.Flatten(input_shape=(480, 480)),
        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dense(2, activation = 'softmax')#Relu or softmax/sigmoid for output layer
#        keras.layers.Dense(2)
    ])
#Relu tanh
    model.compile(optimizer='adadelta',
#                loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['accuracy'])
    
    model.fit(images, labels, epochs = 3, batch_size = 10)
    #model.fit(images, labels, epochs = 2, batch_size = 10)

if __name__ == "__main__":
#    makeDataset() #Include makeDataset() when running for the first time in order to create the datset
    processImages()
    buildModel()
'''
177/177 [==============================] - 4s 24ms/step - loss: 0.2609 - accuracy: 0.9043
Epoch 2/2
177/177 [==============================] - 4s 24ms/step - loss: 0.1529 - accuracy: 0.9502
using 480x480, dense 128 neuron sigmoid activation, dense 2 output, adadelta optimimizer'''
'''177/177 [==============================] - 15s 85ms/step - loss: 0.2480 - accuracy: 0.9100
Epoch 2/5
177/177 [==============================] - 15s 85ms/step - loss: 0.1357 - accuracy: 0.9473
using 480x480, dense 512 neuron tanh activation, dense 128 neruon sigmoid activation, dense 2 layer output '''
'''177/177 [==============================] - 16s 89ms/step - loss: 0.1835 - accuracy: 0.9309
Epoch 2/5
177/177 [==============================] - 16s 88ms/step - loss: 0.1079 - accuracy: 0.9592
using 480x480, dense 512 neuron swish activation, dense 2 layer output, adadelta optimizer'''
'''177/177 [==============================] - 15s 85ms/step - loss: 0.4679 - accuracy: 0.8046
Epoch 2/5
177/177 [==============================] - 15s 85ms/step - loss: 0.3815 - accuracy: 0.9451
with 480x480, dense 512 neuron tanh, dense 2 neuron sigmoid output, adadelta optimizer'''
'''177/177 [==============================] - 15s 83ms/step - loss: 0.2175 - accuracy: 0.9190
Epoch 2/5
177/177 [==============================] - 15s 86ms/step - loss: 0.1005 - accuracy: 0.9615
using 480x480, dense 512 neuron tanh, dense 2 neuron relu output to adadelta. '''
'''177/177 [==============================] - 4s 24ms/step - loss: 0.2681 - accuracy: 0.8635
Epoch 2/3
177/177 [==============================] - 4s 23ms/step - loss: 0.1237 - accuracy: 0.9570
using same settings as above one, but 240x240. There is not a major corelation between accuracy and image resolution'''
'''177/177 [==============================] - 15s 87ms/step - loss: 0.3923 - accuracy: 0.9270
Epoch 2/3
177/177 [==============================] - 15s 87ms/step - loss: 0.3595 - accuracy: 0.9575
relu + softmax'''
'''Epoch 1/3
1766/1766 [==============================] - 1091s 618ms/step - loss: 0.7783 - accuracy: 0.7661
Epoch 2/3
580/1766 [========>.....................] - ETA: 10:57 - loss: 0.1389 - accuracy: 0.7500 resmax 50. How does loss go down but accuracy goes down too?'''
'''Epoch 1/3
1766/1766 [==============================] - 1091s 618ms/step - loss: 0.7783 - accuracy: 0.7661
Epoch 2/3
1766/1766 [==============================] - 985s 558ms/step - loss: 0.1529 - accuracy: 0.7593'''
#What the fuck
'''Epoch 1/3
1766/1766 [==============================] - 177s 100ms/step - loss: 0.5405 - accuracy: 0.7610
Epoch 2/3
1766/1766 [==============================] - 74s 42ms/step - loss: 0.1188 - accuracy: 0.7605
Epoch 3/3
1766/1766 [==============================] - 74s 42ms/step - loss: 0.0768 - accuracy: 0.7571 using adamax optimiser with resnext50'''
'''Epoch 1/30
1766/1766 [==============================] - 161s 91ms/step - loss: 0.2889 - accuracy: 0.5187
Epoch 2/30
1766/1766 [==============================] - 71s 40ms/step - loss: 0.0796 - accuracy: 0.5413
Epoch 3/30
1766/1766 [==============================] - 71s 40ms/step - loss: 0.0825 - accuracy: 0.3414 using adam optimiser with resnext50'''

'''lots of epochs with resnet 50 and 16 cardinality:
		Epoch 1/30
		1766/1766 [==============================] - 196s 111ms/step - loss: 0.4258 - accuracy: 0.8171
		Epoch 2/30
		1766/1766 [==============================] - 150s 85ms/step - loss: 0.3752 - accuracy: 0.7911
		Epoch 3/30
		1766/1766 [==============================] - 150s 85ms/step - loss: 0.3577 - accuracy: 0.7650
		Epoch 4/30
		1766/1766 [==============================] - 150s 85ms/step - loss: 0.3445 - accuracy: 0.7616
		Epoch 5/30
		1766/1766 [==============================] - 150s 85ms/step - loss: 0.3395 - accuracy: 0.7667
		Epoch 6/30
		1766/1766 [==============================] - 150s 85ms/step - loss: 0.3297 - accuracy: 0.7622
		Epoch 7/30
		150/1766 [=>............................] - ETA: 2:17 - loss: 0.3266 - accuracy: 0.7400'''