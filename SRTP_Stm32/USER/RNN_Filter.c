#include "RNN_Filter.h"
const float Q_angle = 0.004;
const float Q_omega = 0.04;
const float dt = 0.01;
static float P00 = Q_angle,P01 = 0,P10 = 0,P11 = Q_omega;
static char is_start = 0;
const float R = 0.0001;
static float pre_angle,Theta_K,omega;
static float K0,K1,diff;

float RNN_filter(float angle){
	if(is_start){
		Theta_K = pre_angle + omega * dt;
		P00 += (P10 + P01) * dt + Q_angle;
		P10 += P11 * dt;
		P01 += P11 * dt;
		P11 += Q_omega;
		K0 = P00/(R + P00);
		K1 = P10/(R + P00);
		diff = angle - Theta_K;
		angle = Theta_K + K0*diff;
		omega = omega + K1*diff;
	}
	else{
		pre_angle =angle; 
	}
	return angle;
}
