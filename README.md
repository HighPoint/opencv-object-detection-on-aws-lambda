# OpenCV Object Detection on AWS Lambda

[![OpenCV Object Detection Launch Stack](read-me-images/OpenCVObjectDetectionLaunchStack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=OpenCVObjectDetectionStack&templateURL=https://opencv-source.s3.amazonaws.com/template.yaml)

Serverless Object Detection using OpenCV on AWS Lambda. Compare AWS Rekognition, OpenCV DNN, and OpenCV Haar Cascades image results directly. 

Sample Human Faces Input:

![Two women](/read-me-images/FaceInput.jpg?raw=true)

Sample Human Faces Output:

![Two women with bounding boxes](/read-me-images/FaceOutput.jpg?raw=true)

OpenCV Object Detection on AWS Lambda placed black bounding boxes around the humans found by AWS Rekognition. The 99.7 is AWS Rekognition's confidence level that this is a person. 

The white bounding boxes around the humans is from OpenCV's Deep Neural Network (DNN). The DNN, in this project, uses the "Faster RCNN Inception Version 2" model. However, you can use any OpenCV DNN compatible model you'd like. This DNN model shows a slightly lower confidence for the humans at 98.5 and 92.2.

The blue bounding boxes shows the OpenCV Haar Cascade for faces. This is an older technology, and not nearly as accurate as neural networks for image detection. The Haar Cascades work best if the picture is already known to contain faces, or dogs, or cats. 
