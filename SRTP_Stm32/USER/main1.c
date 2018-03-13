//#define osObjectsPublic                     // define objects in main module
//#include "osObjects.h"                      // RTOS object definitions
//#include <cmsis_os.h> 
#include "sys.h"
#include "delay.h"
#include "usart.h"
#include "led.h" 
#include "sram.h"   
#include "malloc.h" 
#include "usmart.h"  
#include "sdio_sdcard.h"    
#include "w25qxx.h"    
#include "ff.h"  
#include "exfuns.h"  
#include "mpu6050.h"
#include "inv_mpu.h"
#include "inv_mpu_dmp_motion_driver.h" 
#include "myiic.h"
#include "filter.h"
#include "filter2.h"

#define PI (3.1415f)

//void Get_Angle(void);
//void Thread1 (void const *argument);

//osThreadId tid_Thread1,main_id;
//osThreadDef(Thread1, osPriorityNormal, 1, 0); 
//float Omega1,Theta1,temp,Omega2,Theta2; 
//FIL fil1;
//FRESULT res;
//UINT bwww;
//char buf[80];

char sf[8];
u8 Chip_Selection;

//int Init_Thread (void) {
	
//  tid_Thread1 = osThreadCreate (osThread(Thread1), NULL);
//  if (!tid_Thread1) return(-1);

//  return(0);
//}
//void printangle(u8 select){
	//	Chip_Selection = 0;
	//	Get_Angle();
	//	sprintf(sf,"%3.2f",Theta1);
	//	f_write(&fil1,sf,8,&bwww);
	//	f_write(&fil1,"\r\n",4,&bwww);
//}
void Thread1 (void const *argument) {
	while(1){
		LED0!=LED0;
		osDelay(200);
	}
}




int main(void)
{        
 	u32 total,free;
	u8 res=0;	
	u8 i;
	
//	osKernelInitialize (); // initialize CMSIS-RTOS
//	main_id = osThreadGetId();
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);
	delay_init(168);  //��ʼ����ʱ����
	LED_Init();					//��ʼ��LED	
	//W25QXX_Init();				//��ʼ��W25Q128
	
	//my_mem_init(SRAMIN);		//��ʼ���ڲ��ڴ�� 
	//my_mem_init(SRAMCCM);		//��ʼ��CCM�ڴ��
	
	// Initialize 2 MPU6050 modules
 	//IIC_Init();
	//Chip_Selection = 0;
	//MPU6050_initialize();
	//DMP_Init();
	//Chip_Selection = 1;
	//MPU6050_initialize();
	//DMP_Init();
	
	//Initialize Memory
 //	exfuns_init();			//Ϊfatfs��ر��������ڴ�		
 // f_mount(fs[0],"0:",1); 					//����SD��
 //	res=f_mount(fs[1],"1:",1); 				//����FLASH.
	//while(exf_getfree("0",&total,&free))	//�õ�SD������������ʣ������
	//{
	//	;
	//}		
	
	//res=f_open(&fil1,"0:/message.txt",FA_CREATE_ALWAYS|FA_WRITE);
//	Init_Thread();
//	osKernelStart (); 
	while(1) {
		LED0 != LED0;	
		delay_ms(300);
	}
}

//void Get_Angle()
//{ 
	  //  float Accel_Y,Accel_Angle,Accel_Z,Gyro_X;
		//	Gyro_X = (I2C_ReadOneByte(devAddr,MPU6050_RA_GYRO_XOUT_H)<<8) + I2C_ReadOneByte(devAddr,MPU6050_RA_GYRO_XOUT_L);    //��ȡY��������
		//	Accel_Y = (I2C_ReadOneByte(devAddr,MPU6050_RA_ACCEL_YOUT_H)<<8) + I2C_ReadOneByte(devAddr,MPU6050_RA_ACCEL_YOUT_L); //��ȡX����ٶȼ�
	 // 	Accel_Z = (I2C_ReadOneByte(devAddr,MPU6050_RA_ACCEL_ZOUT_H)<<8) + I2C_ReadOneByte(devAddr,MPU6050_RA_ACCEL_ZOUT_L); //��ȡZ����ٶȼ�
		//  if(Gyro_X>32768)  Gyro_X -= 65536;                       //��������ת��  Ҳ��ͨ��shortǿ������ת��
	  //	if(Accel_Y>32768) Accel_Y -= 65536;                      //��������ת��
		//  if(Accel_Z>32768) Accel_Z -= 65536;                      //��������ת��
		//	if(Chip_Selection == 0){
		//		Omega1 = Gyro_X;                                  //����ƽ����ٶ�
		//		Accel_Angle = atan2(Accel_Y,Accel_Z)*180/PI;                 //�������	
		//		Gyro_X = Gyro_X/16.4f;                                    //����������ת��	
		//		Theta1= Kalman_Filter(Accel_Angle,Gyro_X);//�������˲�
		//	}
		//	if(Chip_Selection == 1){
		//		Omega2 = Gyro_X;                                  //����ƽ����ٶ�
		//		Accel_Angle = atan2(Accel_Y,Accel_Z)*180/PI;                 //�������	
		//		Gyro_X = Gyro_X/16.4f;                                    //����������ת��	
		//		Theta2= Kalman_Filter2(Accel_Angle,Gyro_X);//�������˲�
		//	}
//}




