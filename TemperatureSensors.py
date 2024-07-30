from machine import ADC
import math
import _thread
adc_count = 100
raw = [0]*adc_count

class Thermistor:
    def __init__(self, pin):
        self.thermistor = ADC(pin)
    
        
    def ReadTemperature(self):
        # Get Voltage value from ADC   
        Vin = 3.3
        Ro = 10000  # 10k Resistor
        adc_resolution = 65535
        # Steinhart Constants
        A = 0.001129148
        B = 0.000234125
        C = 0.0000000876741
        adc_value = 0
        #adc_value = self.thermistor.read_u16()

        for i in range(len(raw)):
            adc_value = self.thermistor.read_u16()
            raw[i] = adc_value

        for i in range(len(raw)):
            for j in range(len(raw)-1):
                if raw[j] > raw[j+1]:
                    temp = raw[j]
                    raw[j] = raw[j+1]
                    raw[j+1] = temp
        
        sum_list = sum(raw)
        middle = sum_list/len(raw)


        # Vout = (Vin/adc_resolution)*adc_value
        Vout = (middle * Vin) / adc_resolution;
        # Voltage Divider
        
        # Calculate Resistance
        z = Vin-Vout
        if z == 0:
            z=1

        # Rt = (Vout * Ro) / z 
        Rt = (Vin * Ro / Vout) - Ro;
        # Steinhart - Hart Equation

        TempK = 1 / (A + (B * math.log(Rt)) + C * math.pow(math.log(Rt), 3))

        # Convert from Kelvin to Celsius
        TempC = TempK - 273.15

        return round(TempC,2)
    
    def start(self):
        _thread.start_new_thread(self.ReadTemperature, ())
    
