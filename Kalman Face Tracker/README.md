Abandoned prototype for mouse+keyboard control using facial tracking. I was able to find a facial tracking model that works pretty well, but I quickly found critical problems with the facial landmarking model:
1) The landmarks are very noisy
2) The model was primarily trained off of front-facing faces, and can't handle 3D movements and rotations very well
3) The landmarks are not very responsive to facial gestures

I was able to solve problem #1 by running all 68 points through a Kalman filter, which works pretty well, but problems #2 and #3 are a big problem, since this project requires high-accuracy landmarks. I eventually decided that it would be easier to swap to a different framework, and landed on MediaPipe's facial mesh model. The code for the 68-point 2D model is mostly incompatible with MediaPipe's 478-point 3D model, so I decided that it would be easiest to abandon this and start over. I still like the look of the filtered 68-point model, though!

![grab-landing-page]()