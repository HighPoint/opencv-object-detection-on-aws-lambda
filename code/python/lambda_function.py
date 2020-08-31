import json
import cv2 as cv
import base64
#from os import listdir
import boto3

def lambda_handler(event, context):

  (imageDataString, showHumanFaces,
    showCatFaces, showDogFaces,
    showDetectObject, showAWSRekognition,
    showLabel, showConfidence,
    minConfidence, maxLabels) = loadInitialParameters(event)

  if imageDataString != "":
    image, grayImage = readImageDataString(imageDataString)

    image = processImage(image, grayImage, showDetectObject, showAWSRekognition,
                  showHumanFaces, showCatFaces, showDogFaces,
                  maxLabels, minConfidence, showLabel, showConfidence)

    return returnJSON(image)
  else:
    return False


# processImage

def processImage(image, grayImage, showDetectObject, showAWSRekognition,
                  showHumanFaces, showCatFaces, showDogFaces,
                  maxLabels, minConfidence, showLabel, showConfidence):

  if showDetectObject:
    dnnModelResponse = dnnModel(image, maxLabels, minConfidence)
    image = dnnShowBoxandLabels(dnnModelResponse, image, maxLabels, minConfidence, showLabel, showConfidence)

  if showAWSRekognition:
    f = open("/tmp/photo.jpg","rb")
    rekognitionLabels = detectObjectRekognition(f.read(), maxLabels, minConfidence)
    image = rekognizitionShowBoxandLabels(image, rekognitionLabels, (0,0,0), showLabel, showConfidence)

  if showHumanFaces:
    image = haarCascadeFunction(image, grayImage, '/opt/cv2/data/haarcascade_frontalface_default.xml',(255,0,0), "H Face", showLabel, showConfidence)

  if showCatFaces:
    image = haarCascadeFunction(image, grayImage, '/opt/cv2/data/haarcascade_frontalcatface_extended.xml', (0,255,0), "C Face", showLabel, showConfidence)

  if showDogFaces:
    image = haarCascadeFunction(image, grayImage, '/var/task/Data/dogFace.xml', (0,0,255), "D Face", showLabel, showConfidence)

  return image


# Run the DNN Model against the imported image (image)
# The DNN Model is stored in the AWS Lambda Layer

def dnnModel(image, maxLabels, minConfidence):

  cvNet = cv.dnn.readNetFromTensorflow('/opt/frozen_inference_graph.pb', '/opt/faster_rcnn_inception_v2_coco_2018_01_28.pbtxt')

  cvNet.setInput(cv.dnn.blobFromImage(image, size=(300, 300), swapRB=True, crop=False))

  dnnModelResponse = cvNet.forward()

  return dnnModelResponse


# Show DNN Bounding Box and Optional Labels

def dnnShowBoxandLabels(cvOut, image, maxLabels, minConfidence, showLabel, showConfidence):

  rows = image.shape[0]
  cols = image.shape[1]

  COCO_model_list = getCOCOModelList()

  for detection in cvOut[0,0,:,:]:
    penSize = getImagePenSize(image)
    aConfidence = float(detection[2])

    if aConfidence >= minConfidence:
      aName = getCOCOModelName(COCO_model_list, int(detection[1]))

      left = detection[3] * cols
      top = detection[4] * rows
      right = detection[5] * cols
      bottom = detection[6] * rows
      cv.rectangle(image, (int(left), int(top)), (int(right), int(bottom)), (255, 255, 255), thickness=2*penSize)

      if showLabel or showConfidence:
        writeString = labelString(aName, aConfidence*100, showLabel, showConfidence)
        cv.putText(image, writeString, (int(left), int(top) - 5), cv.FONT_HERSHEY_SIMPLEX,
			      0.5*penSize, (255, 255, 255), 2*penSize)

  return image


# Run AWS Rekognition with the image (imageBytes)

def detectObjectRekognition(imageBytes, maxLabels, minConfidence, region="us-east-1"):

  client=boto3.client('rekognition', region)

  response = client.detect_labels(
    Image= {
        "Bytes": imageBytes
    },
    MaxLabels= maxLabels,
    MinConfidence= minConfidence*100    #AWS Rekognition uses percentage
	)

  labels=response['Labels']

  return labels


# Show the AWS Rekognizition Bounding Box and Optional Labels

def rekognizitionShowBoxandLabels(image, labels, borderColor, showLabel, showConfidence):

  height = image.shape[0]
  width = image.shape[1]
  penSize = getImagePenSize(image)
#  print(f"width = {width} height = {height}")

  for label in labels:
    instances = label.get('Instances')
    for boxes in instances:
      aName = label.get('Name')
      aConfidence = label.get("Confidence")
      aBox = boxes.get('BoundingBox')

      aTop = int(aBox.get('Top') * height)
      aLeft = int(aBox.get('Left') * width)
      aWidth = int(aBox.get('Width') * width)
      aHeight = int(aBox.get('Height') * height)

      cv.rectangle(image, (aLeft, aTop), (aLeft + aWidth, aTop + aHeight), borderColor, 2*penSize)

      if showLabel or showConfidence:
        writeString = labelString(aName, aConfidence, showLabel, showConfidence)
        cv.putText(image, writeString, (aLeft, aTop - 5), cv.FONT_HERSHEY_SIMPLEX,
			      0.5*penSize, borderColor, 2*penSize)

  return image


# Run the HAAR Cascade model in grayscale.
# The cascadeName is the file for the model.
# The human face and cat face models are part of OpenCV and stored in the OpenCV AWS Lambda Layer.
# The dog face model is stored locally on this AWS Lambda.

def haarCascadeFunction(image, gray, cascadeName, borderColor, labelName, showLabel, showConfidence):
  a_cascade = cv.CascadeClassifier(cascadeName)

  height = image.shape[0]
  width = image.shape[1]

  minDimension = min(height,width)
  minSide = int(minDimension*0.18)

  faces = a_cascade.detectMultiScale(gray, scaleFactor = 1.1, minNeighbors=3, minSize=(minSide, minSide))

  image = haarCascadeShowBoxandLabels(image, faces, borderColor, labelName, showLabel, False)

  return image


# Show the HAAR Cascade Bounding Boxes and Optional Label

def haarCascadeShowBoxandLabels(image, faces, borderColor, labelName, showLabel, showConfidence):

  penSize = getImagePenSize(image)
  for (x, y, w, h) in faces:
    cv.rectangle(image, (x, y), (x+w, y+h), borderColor, 2*penSize)

    if showLabel or showConfidence:
      writeString = labelString(labelName, 85.0, showLabel, showConfidence)
      cv.putText(image, writeString, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX,
			      0.5*penSize, borderColor, 2*penSize)

  return image


# Create the Bounding Box Label depending on the showLabel and showConfidence options.

def labelString(labelString, confidenceFloat, showLabel, showConfidence):

  aLabelString = ""

  if showConfidence:
    confidenceString = str(confidenceFloat)[0:4]

  if showLabel and showConfidence:
    aLabelString = labelString + " " + confidenceString
  elif showLabel:
    aLabelString = labelString
  elif showConfidence:
    aLabelString = confidenceString

  return aLabelString


# The DNN uses the COCO Model labels for Faster_RCNN_Inception_v2
def getCOCOModelList():

  f = open("/var/task/Data/COCO_model_label.txt", "r")

  list = []
  for x in f:
    list.append(x)

  f.close();

  return list


# Return the COCO Mode Name from the list

def getCOCOModelName(COCO_model_list, aClass):

  line = COCO_model_list[aClass +1]  # the COCO model list for the Faster_RCNN
  string = str(line).split(" ", 1)[1]

  return string[:-1]

# Resize the Image to the correct size.
# The DNN uses Faster_RCNN_Inception_v2. This model is limited to 300 x 300.
# AWS Rekognition is limited to 5MB images.

def resizeImage(image, maxSize):
  height = image.shape[0]
  width = image.shape[1]

  maxDimension = max(height,width)

  if maxDimension > maxSize:
    scale = maxSize / maxDimension
    width = int(width*scale)
    height = int(height*scale)
    dsize = (width, height)
    image = cv.resize(image, dsize)

  return image

# Convert image to utf-8 encoded base64.
# First write the image

def convertImageToBase64(image):

  cv.imwrite("/tmp/image.jpg", image)

  with open("/tmp/image.jpg", "rb") as imageFile:
    str = base64.b64encode(imageFile.read())
    encoded_image = str.decode("utf-8")

  return encoded_image


# Load the inital parameters

def loadInitialParameters(dict):

    imageDataString = dict.get('imageData',"")
    showHumanFaces = dict.get('humanFace',False)
    showCatFaces = dict.get('catFace', False)
    showDogFaces = dict.get('dogFace', False)
    showDetectObject = dict.get('detectObject', True)
    showAWSRekognition = dict.get('awsRekognition', False)
    showLabel = dict.get('showLabel', True)
    showConfidence = dict.get('showConfidence', True)
    minConfidence = float(dict.get('confidenceLevel', "70"))/100

    maxLabels = 10

    return imageDataString, showHumanFaces, showCatFaces, showDogFaces, showDetectObject, showAWSRekognition, showLabel, showConfidence, minConfidence, maxLabels


# the return JSON

def returnJSON(image):

  encoded_image = convertImageToBase64(image)

  return {
      "isBase64Encoded": True,
      "statusCode": 200,

      "headers": { "content-type": "image/jpeg",
                   "Access-Control-Allow-Origin" : "*",
                   "Access-Control-Allow-Credentials" : True
      },
      "body":   encoded_image
    }


# getImagePenSize

def getImagePenSize(image):

  height = image.shape[0]
  width = image.shape[1]

  maxDimension = max(height, width)

  penSize = int(maxDimension/640)
  if penSize == 0:
    penSize = 1

  return penSize


# readImageDataString

def readImageDataString(imageDataString):

  with open("/tmp/photo.jpg", "wb") as fh:
    fh.write(base64.b64decode(imageDataString))

  # Read the image
  image = cv.imread("/tmp/photo.jpg")
  gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

  return image, gray
