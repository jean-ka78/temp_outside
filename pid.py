# from TemperatureSensors import Thermistor
from mem import St_Enum
eeprom = St_Enum
from dep import Temp_dep

# pin1 = 26
# pin2 = 27
# pin3 = 28
# pin4 = 22
# t_out = Thermistor(pin1)
# t_bat = Thermistor(pin1)
# t_kol = Thermistor(pin1)
# t_boy = Thermistor(pin1)
# T_OUT = t_out.ReadTemperature()

eeprom.heat_otop = True # Флаг вглячення опалення
eeprom.valve_mode = True # Влаг автоматичної роботи клапана
eeprom.per_on = 10 #  період роботи
eeprom.per_off = 120 # Максимальний період роботи клапана 
eeprom.kof_p = 1.0# П
eeprom.kof_i = 30.0 # І 
eeprom.kof_d = 1.0 # Д
eeprom.dead_zone = 2.0 # Гістерезіс

class Pid_reg:

    def constrain(self, x, a, b):
        return max(min(b, x), a)

    def regul(self, set_value):
        hand_up = False
        hand_down = False
        _gtv2 = True # Імпульс 100 мс
        _tempVariable_float = 0

        ON_OFF = eeprom.heat_otop
        AUTO_HAND = eeprom.valve_mode
        HAND_UP = hand_up
        HAND_DOWN = hand_down
        self.SET_VALUE = set_value
        PRESENT_VALUE = 35.0
        PULSE_100MS = _gtv2
        TIMER_PID = 0.0
        PID_PULSE = False
        UP = False
        DOWN = False
       



        CYCLE = eeprom.per_on
        VALVE = eeprom.per_off
        K_P = eeprom.kof_p
        K_I = eeprom.kof_i
        K_D = eeprom.kof_d
        DEAD_ZONE = eeprom.dead_zone

        E_1 =  self.SET_VALUE -  PRESENT_VALUE #Текущее рассогласование
        print('E_1: ', str(E_1), '`C')
        E_2 = 0.0 # Рассогласование на -1 шаг
        E_3 = 0.0 # Рассогласование на -2 шага
        SUM_D_T = 0.0 #Накопленное время воздействия
        D_T = 0.0
        TIMER_PID_UP = 0.0
        TIMER_PID_DOWN = 0.0


        if K_I == 0:
            K_I = 9999.0
        if CYCLE == 0:
            CYCLE = 9999.0
        

        # Ограничения
        K_P = self.constrain(K_P, (-99.0), (99.0)) #// Кр -99.0...99.0 %/С, знак + для нагревателя, знак - для холодильника
        K_I = self.constrain(K_I, (1.0), (9999.0)) # // Ти 1...9999.0 сек
        K_D = self.constrain(K_D, (0.0), (9999.0)) # // Тд 0...9999.0 сек
        CYCLE = self.constrain(CYCLE, (1.0), (25.0))# // Цикл 1...25.0 сек
        VALVE = self.constrain(VALVE, (15.0), (250.0)) # // Время привода 15...250.0 сек
        # print('K_P: ', str(K_P))
        # print('K_I: ', str(K_I))
        # print('K_D: ', str(K_D))
        # print('CYCLE: ', str(CYCLE))
        # print('VALVE: ', str(VALVE))

        if PULSE_100MS and (TIMER_PID == 0.0) and not PID_PULSE:
            PID_PULSE = 1
            D_T = K_P * (E_1 - E_2 + CYCLE * E_2 / K_I +  K_D * (E_1 - 2 * E_2 +  E_3) / CYCLE) * VALVE / 100.0
            E_3 = E_2 # // Запись рассогласования -2 шага назад
            E_2 = E_1 # // Запись рассогласования -1 шаг назад
            SUM_D_T = SUM_D_T + D_T  # // Накопленное время воздействия
            if SUM_D_T >= 0.5: #Сброс накопленного времени закрытия
                TIMER_PID_DOWN = 0.0
            if SUM_D_T <= -0.5: #Сброс накопленного времени открытия
                TIMER_PID_UP = 0.0
            if E_1 < DEAD_ZONE and E_1 > - DEAD_ZONE: #Зона нечувствительности
                D_T = 0.0
                SUM_D_T = 0.0
        if PULSE_100MS:
            TIMER_PID = TIMER_PID + 0.1 #Внутренний таймер ПИД
        if ON_OFF and  AUTO_HAND:
            if TIMER_PID >= CYCLE: #Сброс таймера при окончание цикла регулирования
                PID_PULSE = 0 #Сбросить шаг 
                TIMER_PID = 0.0
                if SUM_D_T>=0.5 or SUM_D_T<=-0.5: #Сброа накопленного времени воздействия
                    SUM_D_T = 0.0
        else:
            PID_PULSE = 0
            D_T = 0.0
            SUM_D_T = 0.0
            TIMER_PID = 0.0
            E_3 = E_1
            E_2 = E_1
            TIMER_PID_UP = 0.0
            TIMER_PID_DOWN = 0.0
        UP = ((((SUM_D_T >= TIMER_PID and (SUM_D_T >= 0.5)) or D_T >= (CYCLE - 0.5) or TIMER_PID_UP >= VALVE) and AUTO_HAND) or (HAND_UP and not AUTO_HAND)) and ON_OFF and not DOWN #Открытие клапана 
        if PULSE_100MS and UP and TIMER_PID_UP <  VALVE:
            TIMER_PID_UP = TIMER_PID_UP + 0.1
        DOWN = ((((SUM_D_T <= - TIMER_PID and SUM_D_T <= - 0.5) or D_T <= -(CYCLE + 0.5) or  TIMER_PID_DOWN  >= VALVE) and AUTO_HAND) or (HAND_DOWN  and not AUTO_HAND)) and ON_OFF and not UP #// Закрытие клапана
        if PULSE_100MS and  DOWN and TIMER_PID_DOWN <  VALVE:
            TIMER_PID_DOWN = TIMER_PID_DOWN + 0.1
    
        return UP, DOWN







