#include "myiic.h"
#include "delay.h"
#include "stm32f4xx_gpio.h"
#include "stm32f4xx_rcc.h"

#include "mpu6050.h"
u8 Errorstate = 0;
//////////////////////////////////////////////////////////////////////////////////	 
//������ֻ��ѧϰʹ�ã�δ��������ɣ��������������κ���;
//ALIENTEK STM32F407������
//IIC ��������	   
//����ԭ��@ALIENTEK
//������̳:www.openedv.com
//��������:2014/5/6
//�汾��V1.0
//��Ȩ���У�����ؾ���
//Copyright(C) ������������ӿƼ����޹�˾ 2014-2024
//All rights reserved									  
////////////////////////////////////////////////////////////////////////////////// 	
void SDA_IN(void){
	if(Chip_Selection) {
		GPIOD->MODER&=~(3<<(5*2));GPIOD->MODER|=0<<5*2;
	}
	else{
	GPIOB->MODER&=~(3<<(7*2));GPIOB->MODER|=0<<7*2;
	}
	
}
void SDA_OUT(void){
	if(Chip_Selection) {
		{GPIOD->MODER&=~(3<<(5*2));GPIOD->MODER|=1<<5*2;}
	}
	else{
	GPIOB->MODER&=~(3<<(7*2));GPIOB->MODER|=1<<7*2;
	}
	
}

//��ʼ��IIC
void IIC_Init(void)
{			
  GPIO_InitTypeDef  GPIO_InitStructure;

  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB|RCC_AHB1Periph_GPIOD, ENABLE);//ʹ��GPIOBʱ��

  //GPIOB6,B7��ʼ������
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_6 | GPIO_Pin_7;
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;//��ͨ���ģʽ
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;//�������
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz;//100MHz
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;//����
  GPIO_Init(GPIOB, &GPIO_InitStructure);//��ʼ��
	
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5|GPIO_Pin_6;
	GPIO_Init(GPIOD,&GPIO_InitStructure);
	
	
	PBout(6) = 1;
	PBout(7) = 1;
	
	PDout(6) = 1;
	PDout(5) = 1;
	//IIC_SCL=1;
	//IIC_SDA=1;
}
//����IIC��ʼ�ź�
int IIC_Start(void)
{
	SDA_OUT();     //sda�����
	if(Chip_Selection == 0){
		IIC_SDA=1;
		if(!READ_SDA) 
			{Errorstate = 1;return 0;}
		IIC_SCL=1;
		delay_us(2);
		IIC_SDA=0;//START:when CLK is high,DATA change form high to low 
		if(READ_SDA) {Errorstate = 1;return 0;}
		delay_us(2);
		IIC_SCL=0;//ǯסI2C���ߣ�׼�����ͻ�������� 
		return 1;
	}
	else{
		IIC2_SDA=1;
		if(!READ2_SDA) {Errorstate = 1;return 0;}
		IIC2_SCL=1;
		delay_us(2);
		IIC2_SDA=0;//START:when CLK is high,DATA change form high to low 
		if(READ2_SDA) {Errorstate = 1;return 0;}
		delay_us(2);
		IIC2_SCL=0;//ǯסI2C���ߣ�׼�����ͻ�������� 
		return 1;
	}
}	  
//����IICֹͣ�ź�
void IIC_Stop(void)
{
	SDA_OUT();//sda�����
	if(Chip_Selection == 0){
	IIC_SCL=0;
	IIC_SDA=0;//STOP:when CLK is high DATA change form low to high
 	delay_us(2);
	IIC_SCL=1; 
	IIC_SDA=1;//����I2C���߽����ź�
	}
	else{
	IIC2_SCL=0;
	IIC2_SDA=0;//STOP:when CLK is high DATA change form low to high
 	delay_us(2);
	IIC2_SCL=1; 
	IIC2_SDA=1;//����I2C���߽����ź�
	}
	delay_us(2);							   	
}
//�ȴ�Ӧ���źŵ���
//����ֵ��1������Ӧ��ʧ��
//        0������Ӧ��ɹ�
u8 IIC_Wait_Ack(void)
{
	u8 ucErrTime=0;
	SDA_IN();      //SDA����Ϊ���� 
	if(Chip_Selection == 0){
		IIC_SDA=1;
		delay_us(1);	   
		IIC_SCL=1;
		delay_us(1);	
		while(READ_SDA)
		{
		ucErrTime++;
		if(ucErrTime>250)
		{
			IIC_Stop();
			{Errorstate = 2;return 1;}
		}
		}
	}
	else{
		IIC2_SDA=1;
		delay_us(1);	   
		IIC2_SCL=1;	
		delay_us(1);
		while(READ2_SDA)
		{
		ucErrTime++;
		if(ucErrTime>250)
		{
			IIC_Stop();
			{Errorstate = 2;return 1;}
		}
		}
	}
	
	
	if(Chip_Selection == 0)
		IIC_SCL=0;//ʱ�����0 	 
	else
		IIC2_SCL= 0;
	return 0;  
} 
//����ACKӦ��
void IIC_Ack(void)
{
	if(Chip_Selection == 0){
	IIC_SCL=0;
	SDA_OUT();
	IIC_SDA=0;
	delay_us(2);
	IIC_SCL=1;
	delay_us(2);
	IIC_SCL=0;
	}
	else{
	IIC2_SCL=0;
	SDA_OUT();
	IIC2_SDA=0;
	delay_us(2);
	IIC2_SCL=1;
	delay_us(2);
	IIC2_SCL=0;
	}
}
//������ACKӦ��		    
void IIC_NAck(void)
{if(Chip_Selection == 0){
	IIC_SCL=0;
	SDA_OUT();
	IIC_SDA=1;
	delay_us(2);
	IIC_SCL=1;
	delay_us(2);
	IIC_SCL=0;
	}
else{
	IIC2_SCL=0;
	SDA_OUT();
	IIC2_SDA=1;
	delay_us(2);
	IIC2_SCL=1;
	delay_us(2);
	IIC2_SCL=0;
}

}					 				     
//IIC����һ���ֽ�
//���شӻ�����Ӧ��
//1����Ӧ��
//0����Ӧ��			  
void IIC_Send_Byte(u8 txd)
{                        
    u8 t;   
	SDA_OUT(); 	    
	if(Chip_Selection == 0){
    IIC_SCL=0;//����ʱ�ӿ�ʼ���ݴ���
    for(t=0;t<8;t++)
    {              
      IIC_SDA=(txd&0x80)>>7;
      txd<<=1; 	  
			delay_us(2);   //��TEA5767��������ʱ���Ǳ����
			IIC_SCL=1;
			delay_us(2); 
			IIC_SCL=0;	
			delay_us(2);
    }	 
	}
	else{
		IIC2_SCL=0;//����ʱ�ӿ�ʼ���ݴ���
    for(t=0;t<8;t++)
    {              
      IIC2_SDA=(txd&0x80)>>7;
      txd<<=1; 	  
			delay_us(2);   //��TEA5767��������ʱ���Ǳ����
			IIC2_SCL=1;
			delay_us(2); 
			IIC2_SCL=0;	
			delay_us(2);
    }	 
	}
} 	    
//��1���ֽڣ�ack=1ʱ������ACK��ack=0������nACK   


int i2cWrite(uint8_t addr, uint8_t reg, uint8_t len, uint8_t *data)
{
		int i;
    if (!IIC_Start())
        {Errorstate = 4;return 1;}
    IIC_Send_Byte(addr << 1 );
    if (!IIC_Wait_Ack()) {
        IIC_Stop();
        {Errorstate = 4;return 1;}
    }
    IIC_Send_Byte(reg);
    IIC_Wait_Ack();
		for (i = 0; i < len; i++) {
        IIC_Send_Byte(data[i]);
        if (!IIC_Wait_Ack()) {
            IIC_Stop();
            return 0;
        }
    }
    IIC_Stop();
    return 0;
}


/**************************ʵ�ֺ���********************************************
*����ԭ��:		bool i2cWrite(uint8_t addr, uint8_t reg, uint8_t data)
*��������:		
*******************************************************************************/
int i2cRead(uint8_t addr, uint8_t reg, uint8_t len, uint8_t *buf)
{
    if (!IIC_Start())
        {Errorstate = 3;return 1;}
    IIC_Send_Byte(addr << 1);
    if (!IIC_Wait_Ack()) {
        IIC_Stop();
        {Errorstate = 3;return 1;}
    }
    IIC_Send_Byte(reg);
    IIC_Wait_Ack();
    IIC_Start();
    IIC_Send_Byte((addr << 1)+1);
    IIC_Wait_Ack();
    while (len) {
        if (len == 1)
            *buf = IIC_Read_Byte(0);
        else
            *buf = IIC_Read_Byte(1);
        buf++;
        len--;
    }
    IIC_Stop();
    return 0;
}

u8 IIC_Read_Byte(unsigned char ack)
{
	unsigned char i,receive=0;
	SDA_IN();//SDA����Ϊ����
	if(Chip_Selection == 0){
    for(i=0;i<8;i++ )
		{
        IIC_SCL=0; 
        delay_us(2);
				IIC_SCL=1;
        receive<<=1;
        if(READ_SDA)
					receive++;   
				delay_us(1); 
		}
	}
	else{
		for(i=0;i<8;i++ )
		{
        IIC2_SCL=0; 
        delay_us(2);
				IIC2_SCL=1;
        receive<<=1;
        if(READ2_SDA)
					receive++;   
				delay_us(1); 
		}
	}
		
    if (!ack)
        IIC_NAck();//����nACK
    else
        IIC_Ack(); //����ACK   
    return receive;
}



/**************************ʵ�ֺ���********************************************
*����ԭ��:		unsigned char I2C_ReadOneByte(unsigned char I2C_Addr,unsigned char addr)
*��������:	    ��ȡָ���豸 ָ���Ĵ�����һ��ֵ
����	I2C_Addr  Ŀ���豸��ַ
		addr	   �Ĵ�����ַ
����   ��������ֵ
*******************************************************************************/ 
unsigned char I2C_ReadOneByte(unsigned char I2C_Addr,unsigned char addr)
{
	unsigned char res=0;
	
	IIC_Start();	
	IIC_Send_Byte(I2C_Addr);	   //����д����
	res++;
	IIC_Wait_Ack();
	IIC_Send_Byte(addr); res++;  //���͵�ַ
	IIC_Wait_Ack();	  
	//IIC_Stop();//����һ��ֹͣ����	
	IIC_Start();
	IIC_Send_Byte(I2C_Addr+1); res++;          //�������ģʽ			   
	IIC_Wait_Ack();
	res=IIC_Read_Byte(0);	   
  IIC_Stop();//����һ��ֹͣ����

	return res;
}

/**************************ʵ�ֺ���********************************************
*����ԭ��:		u8 IICreadBytes(u8 dev, u8 reg, u8 length, u8 *data)
*��������:	    ��ȡָ���豸 ָ���Ĵ����� length��ֵ
����	dev  Ŀ���豸��ַ
		reg	  �Ĵ�����ַ
		length Ҫ�����ֽ���
		*data  ���������ݽ�Ҫ��ŵ�ָ��
����   ���������ֽ�����
*******************************************************************************/ 
u8 IICreadBytes(u8 dev, u8 reg, u8 length, u8 *data){
    u8 count = 0;
	
	IIC_Start();
	IIC_Send_Byte(dev);	   //����д����
	IIC_Wait_Ack();
	IIC_Send_Byte(reg);   //���͵�ַ
    IIC_Wait_Ack();	  
	IIC_Start();
	IIC_Send_Byte(dev+1);  //�������ģʽ	
	IIC_Wait_Ack();
	
    for(count=0;count<length;count++){
		 
		 if(count!=length-1)data[count]=IIC_Read_Byte(1);  //��ACK�Ķ�����
		 	else  data[count]=IIC_Read_Byte(0);	 //���һ���ֽ�NACK
	}
    IIC_Stop();//����һ��ֹͣ����
    return count;
}

/**************************ʵ�ֺ���********************************************
*����ԭ��:		u8 IICwriteBytes(u8 dev, u8 reg, u8 length, u8* data)
*��������:	    ������ֽ�д��ָ���豸 ָ���Ĵ���
����	dev  Ŀ���豸��ַ
		reg	  �Ĵ�����ַ
		length Ҫд���ֽ���
		*data  ��Ҫд�����ݵ��׵�ַ
����   �����Ƿ�ɹ�
*******************************************************************************/ 
u8 IICwriteBytes(u8 dev, u8 reg, u8 length, u8* data){
  
 	u8 count = 0;
	IIC_Start();
	IIC_Send_Byte(dev);	   //����д����
	IIC_Wait_Ack();
	IIC_Send_Byte(reg);   //���͵�ַ
    IIC_Wait_Ack();	  
	for(count=0;count<length;count++){
		IIC_Send_Byte(data[count]); 
		IIC_Wait_Ack(); 
	 }
	IIC_Stop();//����һ��ֹͣ����

    return 1; //status == 0;
}

/**************************ʵ�ֺ���********************************************
*����ԭ��:		u8 IICreadByte(u8 dev, u8 reg, u8 *data)
*��������:	    ��ȡָ���豸 ָ���Ĵ�����һ��ֵ
����	dev  Ŀ���豸��ַ
		reg	   �Ĵ�����ַ
		*data  ���������ݽ�Ҫ��ŵĵ�ַ
����   1
*******************************************************************************/ 
u8 IICreadByte(u8 dev, u8 reg, u8 *data){
	*data=I2C_ReadOneByte(dev, reg);
    return 1;
}

/**************************ʵ�ֺ���********************************************
*����ԭ��:		unsigned char IICwriteByte(unsigned char dev, unsigned char reg, unsigned char data)
*��������:	    д��ָ���豸 ָ���Ĵ���һ���ֽ�
����	dev  Ŀ���豸��ַ
		reg	   �Ĵ�����ַ
		data  ��Ҫд����ֽ�
����   1
*******************************************************************************/ 
unsigned char IICwriteByte(unsigned char dev, unsigned char reg, unsigned char data){
    return IICwriteBytes(dev, reg, 1, &data);
}

/**************************ʵ�ֺ���********************************************
*����ԭ��:		u8 IICwriteBits(u8 dev,u8 reg,u8 bitStart,u8 length,u8 data)
*��������:	    �� �޸� д ָ���豸 ָ���Ĵ���һ���ֽ� �еĶ��λ
����	dev  Ŀ���豸��ַ
		reg	   �Ĵ�����ַ
		bitStart  Ŀ���ֽڵ���ʼλ
		length   λ����
		data    ��Ÿı�Ŀ���ֽ�λ��ֵ
����   �ɹ� Ϊ1 
 		ʧ��Ϊ0
*******************************************************************************/ 
u8 IICwriteBits(u8 dev,u8 reg,u8 bitStart,u8 length,u8 data)
{

    u8 b;
    if (IICreadByte(dev, reg, &b) != 0) {
        u8 mask = (0xFF << (bitStart + 1)) | 0xFF >> ((8 - bitStart) + length - 1);
        data <<= (8 - length);
        data >>= (7 - bitStart);
        b &= mask;
        b |= data;
        return IICwriteByte(dev, reg, b);
    } else {
        return 0;
    }
}

/**************************ʵ�ֺ���********************************************
*����ԭ��:		u8 IICwriteBit(u8 dev, u8 reg, u8 bitNum, u8 data)
*��������:	    �� �޸� д ָ���豸 ָ���Ĵ���һ���ֽ� �е�1��λ
����	dev  Ŀ���豸��ַ
		reg	   �Ĵ�����ַ
		bitNum  Ҫ�޸�Ŀ���ֽڵ�bitNumλ
		data  Ϊ0 ʱ��Ŀ��λ������0 ���򽫱���λ
����   �ɹ� Ϊ1 
 		ʧ��Ϊ0
*******************************************************************************/ 
u8 IICwriteBit(u8 dev, u8 reg, u8 bitNum, u8 data){
    u8 b;
    IICreadByte(dev, reg, &b);
    b = (data != 0) ? (b | (1 << bitNum)) : (b & ~(1 << bitNum));
    return IICwriteByte(dev, reg, b);
}

























