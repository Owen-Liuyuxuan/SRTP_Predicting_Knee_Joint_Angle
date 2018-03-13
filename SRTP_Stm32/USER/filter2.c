#include "filter2.h"	
static float Q_angle2=0.004;// ����������Э����
static float Q_gyro2=0.003;//0.003 ����������Э���� ����������Э����Ϊһ��һ�����о���
static float R_angle2=0.5;// ����������Э���� �Ȳ���ƫ��
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
	angle2+=(Gyro - Q_bias2) * dt2; //�������
		
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
	Pdot2[0]=Q_angle2 - PP2[0][1] - PP2[1][0]; // Pk-����������Э�����΢��

	Pdot2[1]=-PP2[1][1];
	Pdot2[2]=-PP2[1][1];
	Pdot2[3]=Q_gyro2;
	PP2[0][0] += Pdot2[0] * dt2;   // Pk-����������Э����΢�ֵĻ���
	PP2[0][1] += Pdot2[1] * dt2;   // =����������Э����
	PP2[1][0] += Pdot2[2] * dt2;
	PP2[1][1] += Pdot2[3] * dt2;
		
	Angle_err2 = Accel - angle2;	//zk-�������
	
	PCt_02 = C_02 * PP2[0][0];
	PCt_12 = C_02 * PP2[1][0];
	
	E2 = R_angle2 + C_02 * PCt_02;
	
	K_02 = PCt_02 / E2;
	K_12 = PCt_12 / E2;
	
	t_02 = PCt_02;
	t_12 = C_02 * PP2[0][1];

	PP2[0][0] -= K_02 * t_02;		 //����������Э����
	PP2[0][1] -= K_02 * t_12;
	PP2[1][0] -= K_12 * t_02;
	PP2[1][1] -= K_12 * t_12;
		
	angle2	+= K_02 * Angle_err2;	 //�������
	Q_bias2	+= K_12 * Angle_err2;	 //�������
	angle_dot2   = Gyro - Q_bias2;	 //���ֵ(�������)��΢��=���ٶ�
	}
	else{
		angle2 = Accel;
		Q_bias2 = 0;
		has_started2 = 1;
	}
} 
