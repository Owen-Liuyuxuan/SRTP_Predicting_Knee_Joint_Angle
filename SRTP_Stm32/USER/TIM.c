#include "stm32f4xx_rcc.h"
#include "stm32f4xx_tim.h"
#include "sys.h"
#include "TIM.h"

void TIM_Configuration(){
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM4,ENABLE);

	TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
	
	TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
	TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;
	TIM_TimeBaseStructure.TIM_Period = 4200*10-1;
	TIM_TimeBaseStructure.TIM_Prescaler = 19;
	TIM_TimeBaseInit(TIM4,&TIM_TimeBaseStructure);
}
