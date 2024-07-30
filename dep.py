from TemperatureSensors import Thermistor, _thread
from mem import St_Enum
from mqtt import Clien
import time


eeprom = St_Enum


eeprom.T_X1 = -10.0 #мінімальна зовнішня температура
eeprom.T_X2 = 18.0 #Максимальна зовнішня температура 
eeprom.T_Y1 = 70.0 #Максимальна температура контура опалення
eeprom.T_Y2 = 30.0 #Мінімальна температура контура опалення 

class Temp_dep:
    def __init__(self):
        self.client = Clien()
        self.client.start()
        
    def start(self):
        _thread.start_new_thread(self.graf, ())
        
    def graf(self):
        T_X1 = eeprom.T_X1 #мінімальна зовнішня температура
        T_X2 = eeprom.T_X2 #Максимальна зовнішня температура 
        T_Y1 = eeprom.T_Y1 #Максимальна температура контура опалення
        T_Y2 = eeprom.T_Y2 #Мінімальна температура контура опалення 
        T_OUT = self.client.values.get('home/heat_on/temp_out', None)
        print('T_OUT:', str(T_OUT))
        # print(self.client.values)
        # print('home/heat_on/temp_out' in self.client.values)
        if T_OUT is not None:
            T_OUT  = float(T_OUT)
        else:
            T_OUT = 0
        T_SET = 0.0
        if T_OUT <= T_X1:
            T_SET = T_Y1
        #  График между верхней и нижней срезкой
        if T_OUT > T_X1 and T_OUT < T_X2:
            if T_X1 == T_X2:  # Деление на 0
                T_X1 = T_X1 + 0.1
                
            T_SET = (T_OUT - T_X1) * (T_Y1 - T_Y2) / (T_X1 - T_X2) + T_Y1
            
        if T_OUT >= T_X2:#// Нижняя срезка
            T_SET = T_Y2
        return round(T_SET,2)


t_g = Temp_dep()
# t_g.start()

while True:
    t_set = t_g.graf()
    print('T dep', str(t_set), '`C')
    time.sleep(1)