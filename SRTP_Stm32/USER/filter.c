#include "filter.h"	
static float Q_angle=0.004;// ����������Э����
static float Q_gyro=0.003;//0.003 ����������Э���� ����������Э����Ϊһ��һ�����о���
static float R_angle=0.5;// ����������Э���� �Ȳ���ƫ��
static float dt=0.01;//                 
static char  C_0 = 1;
static float Angle_err;
static float PCt_0, PCt_1, E;
static float K_0, K_1, t_0, t_1;
static float Pdot[4] ={0,0,0,0};
static float PP[2][2] = { { 1, 0 },{ 0, 1 } };
static char has_started = 0;
void Kalman_Filter(float Accel,float Gyro)		
{
	if(has_started){
	angle+=(Gyro - Q_bias) * dt; //�������
		
	if(Gyro>75 || Gyro<-75){
		Q_angle = 0.4;
	}
	else 
	{
			if(Gyro>20||Gyro<20){
				Q_angle = 0.01;
			}
			else{
					Q_angle = 0.004;
			}
	}
	
	Pdot[0]=Q_angle - PP[0][1] - PP[1][0]; // Pk-����������Э�����΢��

	Pdot[1]=-PP[1][1];
	Pdot[2]=-PP[1][1];
	Pdot[3]=Q_gyro;
	PP[0][0] += Pdot[0] * dt;   // Pk-����������Э����΢�ֵĻ���
	PP[0][1] += Pdot[1] * dt;   // =����������Э����
	PP[1][0] += Pdot[2] * dt;
	PP[1][1] += Pdot[3] * dt;
		
	Angle_err = Accel - angle;	//zk-�������
	
	PCt_0 = C_0 * PP[0][0];
	PCt_1 = C_0 * PP[1][0];
	
	E = R_angle + C_0 * PCt_0;
	
	K_0 = PCt_0 / E;
	K_1 = PCt_1 / E;
	
	t_0 = PCt_0;
	t_1 = C_0 * PP[0][1];

	PP[0][0] -= K_0 * t_0;		 //����������Э����
	PP[0][1] -= K_0 * t_1;
	PP[1][0] -= K_1 * t_0;
	PP[1][1] -= K_1 * t_1;
		
	angle	+= K_0 * Angle_err;	 //�������
	Q_bias	+= K_1 * Angle_err;	 //�������
	angle_dot   = Gyro - Q_bias;	 //���ֵ(�������)��΢��=���ٶ�
  }
	else{
		angle = Accel;
		Q_bias = 0;
		has_started = 1;
	}
}
