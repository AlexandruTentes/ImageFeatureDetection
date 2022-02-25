# Image Feature Detection

The program is still under development.
The end goal of the project is to use image recognition and AI to create a self-playing table football game. The program would eventually be controlling robots to play the football match based on the webcam feedback.

This part of the code focuses mostly on the webcam and feature detection parts of the project.
It is using the OpenCV library to handle the window creation, webcam feedback, and image processing parts.
The CVUI library is used to create simple UI components.

![image](https://user-images.githubusercontent.com/35760618/155772642-7813071c-9b06-4703-a56b-f4a18d237310.png)

As in any football match, only 2 teams are playing, therefore the program also only recognizes 2 teams. In the figure above, the bound team is team number one. And the color set for this team is mostly in the blue color range (as shown in the figure above, the program detects only the blue square).

The program works by focusing only on the chosen color range of each team, after which the Canny edge detector is being applied.

Binding the second team (green):

![image](https://user-images.githubusercontent.com/35760618/155773509-9ae0d9cc-d1e2-4450-87db-9cd8032986ae.png)

Everything is based on the color range which means that the lighting has a significant impact on the image processing algorithm.

The program is made in such a way that if the webcam fails, the code still runs on the last rendered frame (backend) and meaningful logs and warnings will let the user know the problem.

![image](https://user-images.githubusercontent.com/35760618/155773782-834c9cfe-8801-4d1d-ad9f-f67080784128.png)

The program also includes several cmd commands in case anything goes wrong at runtime:

![image](https://user-images.githubusercontent.com/35760618/155773964-d59491fe-f0cd-4bbb-9085-c4effa6b91b2.png)

And lastly, the configuration system allows for persistent modifications to multiple options during runtime:

![image](https://user-images.githubusercontent.com/35760618/155774136-8f6a89d5-c82e-49f9-9086-b33d56aca363.png)
