import numpy as np


class HeatwaveDetector:
    def __init__(self, max_temps, min_temps):
        self.max_temps = max_temps
        self.min_temps = min_temps
        self.avg_temps = [(max_temp + min_temp) / 2 for max_temp, min_temp in zip(max_temps, min_temps)]

    def calculate_EHF(self):
        self.EHF = []
        for i in range(2, len(self.max_temps)):
            avg_max_prev_3_days = np.mean(self.max_temps[i-2:i+1])
            avg_min_prev_3_days = np.mean(self.min_temps[i-2:i+1])
            avg_temp_prev_3_days = (avg_max_prev_3_days + avg_min_prev_3_days) / 2

            daily_excess = max(0, self.avg_temps[i] - avg_temp_prev_3_days)
            EHF = daily_excess if daily_excess > 0 else 0

            self.EHF.append(EHF)
        
        # Adding two None at the beginning since EHF cannot be calculated for the first two days
        self.EHF = [None, None] + self.EHF

    def detect_heatwave(self):
        self.calculate_EHF()

        heatwave_days = []
        for i in range(len(self.EHF)):
            if self.EHF[i] > 0:
                heatwave_days.append(i)

        return heatwave_days


max_temps = [30, 31, 32, 33, 34, 35, 30, 29, 30, 31]
min_temps = [25, 26, 27, 28, 29, 30, 25, 24, 25, 26]

detector = HeatwaveDetector(max_temps, min_temps)
heatwave_days = detector.detect_heatwave()

print(heatwave_days)  # This will print the indices of the days where a heatwave was detected
