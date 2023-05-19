<p align="center">
  <img src="https://raw.githubusercontent.com/CandeiasV2/AutoPong/main/ignore/banner.png" alt="Banner">
  <br>
  <img src="https://img.shields.io/pypi/pyversions/cv" alt="PyPI - Python Version">
  <br>
</p>

## Preview
<p align="center">
  <img src="ignore/play.gif" alt="GIF">
  <br>
  <em>Self-playing user that analyzes the ball's trajectory and moves the paddle to intercept the ball at the game of Pong.</em>
</p>


## How does it work
The automated Pong game was developed on the NVIDIA Jetson TX2 Developer Kit, utilizing a screen mirroring technique to capture video feed from a phone running the Pong game downloaded from the Google Pay Store. This was achieved through the use of a screen mirroring software called 'scrcpy'. The self-playing user analyzes the trajectory of the incoming ball and moves the paddle to its predicted destination. This is accomplished by leveraging an ADB Client to simulate swipes on the screen, effectively controlling the paddle's movement.

The development of the game involved the utilization of the following libraries:
- __scrcpy__: To mirror the video feed of the phone via USB.
- __ppadb__: To simulate screen swipes for controlling the paddle.
- __mss__: For capturing screenshots of the phone mirror video feed, which were then processed for image analysis.
- __cv2__: For performing image processing tasks, including ball and paddle detection.
- __threading__: To enable parallel execution of swipe movements and image processing, without introducing delays.


## Inspiration
Special thanks to [Engineer Man](https://youtu.be/U2dS8pu2baY) for providing the idea that inspired this project, which focused on ball altitude-based paddle movement.


## Code Snippet
Below is a brief code snippet that highlights the project's implementation:
<p align="center">
  <img src="https://github.com/CandeiasV2/AutoPong/assets/119818078/f68fd983-128b-4b0b-9256-3fbb4b703c02" alt="Image">
</p>

