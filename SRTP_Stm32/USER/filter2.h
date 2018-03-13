#ifndef __FILTER2_H
#define __FILTER2_H

extern float angle2, angle_dot2,Q_bias2; 	
void Kalman_Filter2(float Accel,float Gyro);		
#endif
