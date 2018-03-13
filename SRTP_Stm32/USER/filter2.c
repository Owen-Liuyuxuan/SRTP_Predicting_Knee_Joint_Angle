#include "filter2.h"	
static float Q_angle2=0.004;// 过程噪声的协方差
static float Q_gyro2=0.003;//0.003 过程噪声的协方差 过程噪声的协方差为一个一行两列矩阵
static float R_angle2=0.5;// 测量噪声的协方差 既测量偏差
static float dt2=0.01;//                 
static char  C_02 = 1;
static float Angle_err2;
static float PCt_02, PCt_12, E2;
static float K_02, K_12, t_02, t_12;
static float Pdot2[4] ={0,0,0,0};
static float PP2[2][2] = { { 1, 0 },{ 0, 1 } };
static char has_started2 = 0;
void Kalman_Filter2(float Accel,float Gyro)		
{
	if(has_started2){
	angle2+=(Gyro - Q_bias2) * dt2; //先验估计
		
	if(Gyro>75 || Gyro<-75){
		Q_angle2 = 0.04;
	}
	else 
	{
			if(Gyro>20||Gyro<20){
				Q_angle2 = 0.01;
			}
			else{
					Q_angle2 = 0.004;
			}
	}
	Pdot2[0]=Q_angle2 - PP2[0][1] - PP2[1][0]; // Pk-先验估计误差协方差的微分

	Pdot2[1]=-PP2[1][1];
	Pdot2[2]=-PP2[1][1];
	Pdot2[3]=Q_gyro2;
	PP2[0][0] += Pdot2[0] * dt2;   // Pk-先验估计误差协方差微分的积分
	PP2[0][1] += Pdot2[1] * dt2;   // =先验估计误差协方差
	PP2[1][0] += Pdot2[2] * dt2;
	PP2[1][1] += Pdot2[3] * dt2;
		
	Angle_err2 = Accel - angle2;	//zk-先验估计
	
	PCt_02 = C_02 * PP2[0][0];
	PCt_12 = C_02 * PP2[1][0];
	
	E2 = R_angle2 + C_02 * PCt_02;
	
	K_02 = PCt_02 / E2;
	K_12 = PCt_12 / E2;
	
	t_02 = PCt_02;
	t_12 = C_02 * PP2[0][1];

	PP2[0][0] -= K_02 * t_02;		 //后验估计误差协方差
	PP2[0][1] -= K_02 * t_12;
	PP2[1][0] -= K_12 * t_02;
	PP2[1][1] -= K_12 * t_12;
		
	angle2	+= K_02 * Angle_err2;	 //后验估计
	Q_bias2	+= K_12 * Angle_err2;	 //后验估计
	angle_dot2   = Gyro - Q_bias2;	 //输出值(后验估计)的微分=角速度
	}
	else{
		angle2 = Accel;
		Q_bias2 = 0;
		has_started2 = 1;
	}
} 
