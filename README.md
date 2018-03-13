# SRTP_Predicting_Knee_Joint_Angle

## SRTP_Data

This file contains the dataset, the jupyter notebook, and the checkpointset of tensorflow. As mentioned in the paper, RNN and ANN are trained in tensorflow while SVR is trained using sklearn. Codes on RNN are presented in "Mea_2_7" and codes on ANN and SVR are presented in "ANN".

The evaluation of each single algorithms are tested on MCU_Test_3.txt and MCU_Test_4.txt. Some parts of the sitting phases in test set are trimmed to ensure a proper proportion between static and dynamic gaits. 

Most data-related pictures have been presented on the default notebook.

## SRTP_Stm32

This files contains most program files for controlling the Stm32F407 to perform the stuffs we mentioned in the paper. Most important parts:Users/Deep_RNN.c & main.c. "main.c" shows the program structure and main logics while "Deep_RNN.c" shows the implementation of the RNN
