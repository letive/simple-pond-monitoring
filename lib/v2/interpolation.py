from scipy.interpolate import CubicSpline
import pandas as pd
from lib.helpers_mod import normal_trapezoidal, left_trapezoidal

class Interpolate:

    def __init__(self, df = None, path: str = None, sep: str =","):
        if type(df) == pd.DataFrame:
            self.df = df
        else:
            self.df = pd.read_csv(path, sep=sep)

    
    def get_function(self, x: str, y: str, conditon: tuple, trapezoidal_function="normal"):
        if trapezoidal_function == "normal":
            y = [normal_trapezoidal(i, conditon[0], conditon[3], conditon[1], conditon[2]) for i in self.df[y].tolist()]
        else:
            y = [left_trapezoidal(i, conditon[0], conditon[3], conditon[2]) for i in self.df[y].tolist()]

        function = CubicSpline(x = self.df[x].tolist(), y = y)
        return function
        
