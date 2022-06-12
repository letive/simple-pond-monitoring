import numpy as np
class GrowthFunction:
    def __init__(self, temperature, 
        temp_suitable_min, temp_suitable_max, temp_optimal_min, temp_optimal_max, temp_upper_limit,
        oxygen,
        do_suitable_min, do_suitable_max, do_optimal_min, do_optimal_max, do_upperlimit, 
        uia,
        ua_suitable_min, ua_suitable_max, ua_optimal_min, ua_optimal_max, ua_upperlimit,
        biomass,
        volume,
        csc_suitable_min,
        csc_suitable_max, 
        csc_optimal_min,
        csc_optimal_max,
        csc_upper_limit
        ):
        
        self.temperature = temperature
        self.temp_suitable_min = temp_suitable_min
        self.temp_suitable_max = temp_suitable_max
        self.temp_optimal_min = temp_optimal_min
        self.temp_optimal_max = temp_optimal_max
        self.temp_upper_limit = temp_upper_limit
        
        self.oxygen = oxygen
        self.do_suitable_min = do_suitable_min
        self.do_suitable_max = do_suitable_max
        self.do_optimal_min = do_optimal_min
        self.do_optimal_max =  do_optimal_max 
        self.do_upperlimit =  do_upperlimit

        self.uia = uia
        self.ua_suitable_min = ua_suitable_min
        self.ua_suitable_max = ua_suitable_max
        self.ua_optimal_min = ua_optimal_min
        self.ua_optimal_max = ua_optimal_max
        self.ua_upperlimit = ua_upperlimit

        self.biomass = biomass
        self.volume = volume
        self.csc_suitable_min = csc_suitable_min
        self.csc_suitable_max = csc_suitable_max
        self.csc_optimal_min = csc_optimal_min
        self.csc_optimal_max = csc_optimal_max
        self.csc_upper_limit = csc_upper_limit

    @staticmethod
    def _check_condition(value, suitable_min, suitable_max):
        if value < suitable_min or value > suitable_max:
            return False
        else:
            return True
    
    @staticmethod
    def _normal_trapezoidal(m, suitable_min, suitable_max, optimal_min, optimal_max, upper_limit):
        """
        m: value in t
        """
        if np.isnan(m):
            ret = 0.25
        elif m < suitable_min:
            ret = 0 
        elif m > suitable_max:
            ret = 0
        else:
            ret = min(((m-suitable_min)/(optimal_min-suitable_min), 1, (suitable_max-m)/(suitable_max-optimal_max)))
            
        return ret

    @staticmethod
    def _left_trapezoidal(m, suitable_min, suitable_max, optimal_min, optimal_max, upper_limit):
        """
        m: value in t
        """
        if np.isnan(m):
            ret = 0.25
        elif m < suitable_min:
            ret = 0
        elif m > suitable_max:
            ret = 0
        else:
            ret = min((1, (suitable_max-m)/(suitable_max-optimal_max)))
            
        return ret

    def _temperature(self):
        check = self._check_condition(self.temperature, self.temp_suitable_min, self.temp_suitable_max)
        if check:
            value = self._normal_trapezoidal(self.temperature, self.temp_suitable_min, self.temp_suitable_max, self.temp_optimal_min, self.temp_optimal_max, self.temp_upper_limit)
        else:
            value = 0    
        return value

    def _oxygen(self):
        check = self._check_condition(self.oxygen, self.do_suitable_min, self.do_suitable_max)
        if check:
            value = self._normal_trapezoidal(self.oxygen, self.do_suitable_min, self.do_suitable_max, self.do_optimal_min, self.do_optimal_max, self.do_upperlimit)
        else:
            value = 0    
        return value

    def _uia(self):
        check = self._check_condition(self.uia, self.ua_suitable_min, self.ua_suitable_max)
        if check:
            value = self._left_trapezoidal(self.uia, self.ua_suitable_min, self.ua_suitable_max, self.ua_optimal_min, self.ua_optimal_max, self.ua_upperlimit)
        else:
            value = 0    
        return value

    def _csc(self):

        value = self.biomass/self.volume
        check = self._check_condition(value, self.csc_suitable_min, self.csc_suitable_max)
        if check:
            value = self._left_trapezoidal(value, self.csc_suitable_min, self.csc_suitable_max, self.csc_optimal_min, self.csc_optimal_max, self.csc_upper_limit)
        else:
            value = 0

        return value

    def get_result(self):
        if any((self._temperature() == 0, self._oxygen() == 0, self._uia() ==0, self._csc() == 0)):
            res = 0
        else:
            res = (self._temperature() + self._oxygen() + self._uia() + self._csc())/4
        return res
