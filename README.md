# OpenCV Object Detection on AWS Lambda

[![OpenCV Object Detection Launch Stack](read-me-images/OpenCVObjectDetectionLaunchStack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=OpenCVObjectDetectionStack&templateURL=https://opencv-source.s3.amazonaws.com/template.yaml)

Serverless Object Detection using OpenCV on AWS Lambda. Compare AWS Rekognition, OpenCV DNN, and OpenCV Haar Cascades image results directly. 

Sample Human Image Input:

![Two women](/read-me-images/FaceInput.jpg?raw=true)

Sample Human Image Output:

![Two women with bounding boxes](/read-me-images/FaceOutput.jpg?raw=true)

OpenCV Object Detection on AWS Lambda places black bounding boxes around the humans found by AWS Rekognition. The 99.7 is AWS Rekognition's confidence level that this is a person. 

The white bounding boxes around the humans is from OpenCV's Deep Neural Network (DNN). The DNN, in this project, uses the "Faster RCNN Inception Version 2" model. However, you can use any OpenCV DNN compatible model you'd like. This DNN model shows a slightly lower confidence for the humans at 98.5 and 92.2.

The blue bounding boxes shows the OpenCV Haar Cascade for faces. This is an older technology, and not nearly as accurate as neural networks for image detection. The Haar Cascades work best if the picture is already known to contain faces, or dogs, or cats. 

Sample Dog Image Input:

![Dog with bounding boxes](/read-me-images/DogInput.jpg?raw=true)

Sample Dog Image Output:

![Dog with bounding boxes](/read-me-images/DogOutput.jpg?raw=true)

# How to Use

1. Click the "OpenCV Object Detection Launch Stack" button:
&nbsp;

[![OpenCV Object Detection Launch Stack](read-me-images/OpenCVObjectDetectionLaunchStack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/new?stackName=OpenCVObjectDetectionStack&templateURL=https://opencv-source.s3.amazonaws.com/template.yaml)

&nbsp;

This will bring you to either the Cloudformation UI or the AWS console if you are not signed in. Sign in, if you are not already. From the Cloudformation UI, click "Next" at the bottom of the screen. Repeat clicking "Next" on the two following pages. You will reach a page with this towards the bottom:

![CloudFormation Shot](/read-me-images/CloudFormationShot.png?raw=true)

&nbsp;

Checkmark the three "I acknowledgement" statements and select "Create Stack." This will start building the CloudFormation stack.

&nbsp;

2) Navigate to S3.

&nbsp;


7) Congratulations! The Aerolite Step Function will start executing the PowerShell commands in the S3 file. It's that easy.

&nbsp;
