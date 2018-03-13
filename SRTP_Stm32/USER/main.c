#include "sys.h"
#include "delay.h"
#include "usart.h"
#include "led.h" 
#include "sram.h"   
#include "malloc.h" 
//#include "usmart.h"  
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
#include "ADCDMA.h"
#include "TIM.h"
#include "arm_math.h"
#include "NeuralNet.h"



//Angle Relevant
//#define PI (3.1415f)
float angle=0,angle2=0,angle_dot=0,angle_dot2=0,Q_bias,Q_bias2;
float Accel_Y,Accel_Angle,Accel_Z,Gyro_X=0;
float testnumber[2][7] = {{-77.17 ,0.55   ,-97.93   ,  0.16   ,  0.1992,   0.1161,1.2},
												{-77.15   ,  0.62  , -97.92 ,    0.35   ,  0.2121 ,  0.1097,0.5}};
//RNN Relevant
float output;
float inputbuffer[7];

	
FIL fil1;
FRESULT res;
UINT bwww;
//char buf[80];
char sf[7];
u8 Chip_Selection;

#define f_write_title() f_write(&fil1,"angle1,omega1,angle2,omega2,spike1,spike2,spike3,pred1\r\n",56,&bwww)

static u16 advalue[15];
float readadvalue1,readadvalue2,readadvalue3;

u8 j;	
u32 i=0;


void Get_Angle()
{ 
			Gyro_X = (I2C_ReadOneByte(devAddr,MPU6050_RA_GYRO_XOUT_H)<<8) + I2C_ReadOneByte(devAddr,MPU6050_RA_GYRO_XOUT_L);    //读取Y轴陀螺仪
			Accel_Y = (I2C_ReadOneByte(devAddr,MPU6050_RA_ACCEL_YOUT_H)<<8) + I2C_ReadOneByte(devAddr,MPU6050_RA_ACCEL_YOUT_L); //读取X轴加速度计
	  	Accel_Z = (I2C_ReadOneByte(devAddr,MPU6050_RA_ACCEL_ZOUT_H)<<8) + I2C_ReadOneByte(devAddr,MPU6050_RA_ACCEL_ZOUT_L); //读取Z轴加速度计
		  if(Gyro_X>32768)  Gyro_X -= 65536;                       //数据类型转换  也可通过short强制类型转换
	  	if(Accel_Y>32768) Accel_Y -= 65536;                      //数据类型转换
		  if(Accel_Z>32768) Accel_Z -= 65536;                      //数据类型转换
			if(Chip_Selection == 0){
				                                 //更新平衡角速度
				Accel_Angle = atan2(Accel_Y,Accel_Z)*180/PI;                 //计算倾角	
				Gyro_X = Gyro_X/16.4f;                                    //陀螺仪量程转换	
				Kalman_Filter(Accel_Angle,Gyro_X);//卡尔曼滤波
			}
			if(Chip_Selection == 1){
				                                //更新平衡角速度
				Accel_Angle = atan2(Accel_Y,Accel_Z)*180/PI;                 //计算倾角	
				Gyro_X = Gyro_X/16.4f;                                    //陀螺仪量程转换	 
				Kalman_Filter2(Accel_Angle,Gyro_X);//卡尔曼滤波
			}
			
}
void main_task(){
	
				Chip_Selection = 0;
				Get_Angle();
		
				Chip_Selection = 1;
				Get_Angle();
				
				readadvalue1 = 0;
				readadvalue2 = 0;
				readadvalue3 = 0;
				for(j=0;j<15;j = j + 3){
					readadvalue1 += (float)advalue[j];
					readadvalue2 += (float)advalue[j + 1];
					readadvalue3 += (float)advalue[j + 2];
				}
				readadvalue1 = (float)readadvalue1 * 3.3f/4096/5;
				readadvalue2 = (float)readadvalue2 * 3.3f/4096/5;
				readadvalue3 = (float)readadvalue3 * 3.3f/4096/5;
				
				
				if(i>=100){
					
				inputbuffer[0] = angle;
				inputbuffer[1] = angle_dot;
				inputbuffer[2] = -(angle2+180);
				inputbuffer[3] = -angle_dot2;
				inputbuffer[4] = readadvalue1;
				inputbuffer[5] = readadvalue2;
				inputbuffer[6] = readadvalue3;
				//RNN_SetInput(inputbuffer);
				RNN_Predict(inputbuffer);
					
					/*
					inputbuffer[0] = testnumber[i-1][0];
					inputbuffer[1] = testnumber[i-1][1];
					inputbuffer[2] = testnumber[i-1][2];
					inputbuffer[3] = testnumber[i-1][3];
					inputbuffer[4] = testnumber[i-1][4];
					inputbuffer[5] = testnumber[i-1][5];
					inputbuffer[6] = testnumber[i-1][6];
					RNN_SetInput(inputbuffer);
					RNN_Predict();
					*/
				}
				f_lseek(&fil1,fil1.fsize);
				sf[6] = 0;
				sprintf(sf,"%7.2f",angle);
				f_write(&fil1,sf,7,&bwww);
				f_write(&fil1,",",1,&bwww);
				sf[6] = 0;
				sprintf(sf,"%7.2f",angle_dot);
				f_write(&fil1,sf,7,&bwww);
				f_write(&fil1,",",1,&bwww);
				sf[6] = 0;
				sprintf(sf,"%7.2f",angle2);
				f_write(&fil1,sf,7,&bwww);
				f_write(&fil1,",",1,&bwww);
				sf[6] = 0;
				sprintf(sf,"%7.2f",angle_dot2);
				f_write(&fil1,sf,7,&bwww);
				f_write(&fil1,",",1,&bwww);
				
				sf[6] = 0;
				sprintf(sf,"%7.4f",readadvalue1);
				f_write(&fil1,sf,7,&bwww);
				f_write(&fil1,",",1,&bwww);
				sf[6] = 0;
				sprintf(sf,"%7.4f",readadvalue2);
				f_write(&fil1,sf,7,&bwww);
				f_write(&fil1,",",1,&bwww);
				sf[6] = 0;
				sprintf(sf,"%7.4f",readadvalue3);
				f_write(&fil1,sf,7,&bwww);
				if(i>100){
					f_write(&fil1,",",1,&bwww);
					
					sf[6] = 0;
					sprintf(sf,"%7.2f",output);
					f_write(&fil1,sf,7,&bwww);
					f_write(&fil1,"\r\n",2,&bwww);
				}
				else{
					f_write(&fil1,"\r\n",2,&bwww);
				}

				
}
int main(void)
{        
 	u32 total,free;

	
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_2);//设置系统中断优先级分组2
	delay_init(168);  //初始化延时函数
	LED_Init();					//初始化LED 
	W25QXX_Init();				//初始化W25Q128
	my_mem_init(SRAMIN);		//初始化内部内存池 
	my_mem_init(SRAMCCM);		//初始化CCM内存池
	TIM_Configuration();
 	IIC_Init();
	Gyro_X = 0;
	Chip_Selection = 0;
	MPU6050_initialize();
	DMP_Init();
	Get_Angle();
	
	
	while(Gyro_X == 0||(Accel_Angle<-134&&Accel_Angle>136)||Gyro_X>200||Gyro_X<-200||Accel_Angle == 0){
		MPU6050_initialize();
		DMP_Init();
		Get_Angle();
		delay_ms(5);
	}
	
	Gyro_X = 0;
	Chip_Selection = 1;
	MPU6050_initialize();
	DMP_Init();
	Get_Angle();
	
	while(Gyro_X == 0||(Accel_Angle<-134&&Accel_Angle>136)||Gyro_X>200||Gyro_X<-200||Accel_Angle == 0){
		MPU6050_initialize();
		DMP_Init();
		Get_Angle();
		delay_ms(5);
	}
	
	
	
 	exfuns_init();			//为fatfs相关变量申请内存		
  f_mount(fs[0],"0:",1); 					//挂载SD卡
 	f_mount(fs[1],"1:",1); 				//挂载FLASH.
	
	
	RNN_Init();
	DMA_Configuration((u32) advalue);
	
	while(exf_getfree("0",&total,&free))	//得到SD卡的总容量和剩余容量
	{
		LED0=!LED0;//DS0闪烁
		delay_ms(300);
	}		

	f_open(&fil1,"0:/train.txt",FA_CREATE_ALWAYS|FA_WRITE);
	f_write_title();
	//f_write(&fil1,"angle1,omega1,angle2,omega2,spike1,spike2,spike3,pred1,pred2\r\n",62,&bwww);
	//f_write(&fil1,"angle1,omega1,angle2,omega2,spike1,spike2\r\n",43,&bwww);
	f_close(&fil1);

	TIM_Cmd(TIM4,ENABLE);

	while(i<50000){
		if(TIM_GetFlagStatus(TIM4,TIM_FLAG_Update)==RESET){
			;
		}
		else{
				TIM_ClearFlag(TIM4,TIM_FLAG_Update);
				TIM4->CNT = 0;//Important for long-term work
				i++;
				f_open(&fil1,"0:/train.txt",FA_WRITE);
				main_task();
				if(i%50 == 0){
					LED0 =!LED0;
				}
				f_close(&fil1);
		}
	}
	TIM_Cmd(TIM4,DISABLE);
	
	
	f_open(&fil1,"0:/test.txt",FA_CREATE_ALWAYS|FA_WRITE);
	f_write_title();
	//f_write(&fil1,"angle1,omega1,angle2,omega2,spike1,spike2,spike3,pred1,pred2\r\n",55,&bwww);
	//f_write(&fil1,"angle1,omega1,angle2,omega2,spike1,spike2\r\n",43,&bwww);
	f_close(&fil1);
	TIM_Cmd(TIM4,ENABLE);
	TIM4->CNT = 0;
	i = 0;
		while(i<10000){
		if(TIM_GetFlagStatus(TIM4,TIM_FLAG_Update)==RESET){
			;
		}
		else{
				TIM_ClearFlag(TIM4,TIM_FLAG_Update);
				TIM4->CNT = 0;//Important for long-term work
				i++;
				f_open(&fil1,"0:/test.txt",FA_WRITE);
				main_task();
				if(i%100 == 0){
					LED0 =!LED0;
				}
				f_close(&fil1);
		}
	}
	
	while(1)
	{
		LED0=!LED0;//DS0闪烁
		delay_ms(300);
	} 
}





