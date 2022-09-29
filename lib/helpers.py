import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline


def heaviside_step(x):
    return np.heaviside([x], 1)[0]


def normal_trapezoidal(m, suitable_min, suitable_max, optimal_min, optimal_max):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif (m < suitable_min) or (m > suitable_max):
        ret = 0
    else:
        ret = min(
            (
                (m - suitable_min) / (optimal_min - suitable_min),
                1,
                (suitable_max - m) / (suitable_max - optimal_max),
            )
        )

    return ret


def left_trapezoidal(m, suitable_min, suitable_max, optimal_max):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif (m < suitable_min) or (m > suitable_max):
        ret = 0
    else:
        ret = min((1, (suitable_max - m) / (suitable_max - optimal_max)))

    return ret


def source_data(**kwargs):
    if kwargs["path"]:
        df = pd.read_csv(kwargs["path"], sep=";") #Temp;DO;NH4;NO2;ABW;DOC
        doc = df["DOC"].tolist()
        score_uia = []
        score_o2 = []
        score_temp = []

        for i in doc:
            score_uia.append(
                left_trapezoidal(
                    df[df["DOC"] == i]["NH4"].values[0],
                    kwargs["ua_suitable_min"],
                    kwargs["ua_suitable_max"],
                    kwargs["ua_optimal_max"],
                )
            )

            score_o2.append(
                normal_trapezoidal(
                    df[df["DOC"] == i]["DO"].values[0],
                    kwargs["do_suitable_min"],
                    kwargs["do_suitable_max"],
                    kwargs["do_optimal_min"],
                    kwargs["do_optimal_max"],
                )
            )

            score_temp.append(
                normal_trapezoidal(
                    df[df["DOC"] == i]["Temp"].values[0],
                    kwargs["temp_suitable_min"],
                    kwargs["temp_suitable_max"],
                    kwargs["temp_optimal_min"],
                    kwargs["temp_optimal_max"],
                )
            )

            suhu = df[["DOC", "Temp"]]

    else:
        try:
            chem = pd.read_csv(kwargs["chemical_path"])
            bio = pd.read_csv(kwargs["biological_path"])

            bio.replace("-", np.nan, inplace=True)
            bio.fillna(np.nan, inplace=True)
            
            chem.replace("-", np.nan, inplace=True)
            chem.fillna(np.nan, inplace=True)
        except:
            chem = pd.read_csv("data/data_chemical_v2.csv")
            bio = pd.read_csv("data/data_sample - biological.csv")

        doc = chem["Doc"].tolist()

        score_uia = []
        score_o2 = []
        score_temp = []

        for i in doc:
            score_uia.append(
                left_trapezoidal(
                    chem[chem["Doc"] == i]["uia"].values[0],
                    kwargs["ua_suitable_min"],
                    kwargs["ua_suitable_max"],
                    kwargs["ua_optimal_max"],
                )
            )

            score_o2.append(
                normal_trapezoidal(
                    bio[bio["DOC"] == i]["DO_s"].values[0],
                    kwargs["do_suitable_min"],
                    kwargs["do_suitable_max"],
                    kwargs["do_optimal_min"],
                    kwargs["do_optimal_max"],
                )
            )

            score_temp.append(
                normal_trapezoidal(
                    bio[bio["DOC"] == i]["Suhu_s"].values[0],
                    kwargs["temp_suitable_min"],
                    kwargs["temp_suitable_max"],
                    kwargs["temp_optimal_min"],
                    kwargs["temp_optimal_max"],
                )
            )

            suhu = bio[["DOC", "Suhu_s"]]

    f_uia = CubicSpline(doc, score_uia)
    f_o2 = CubicSpline(doc, score_o2)
    f_temp = CubicSpline(doc, score_temp)

    

    return f_uia, f_o2, f_temp, suhu


def score_csc_compute(
    biomass, volume, csc_suitable_min=0.00, csc_suitable_max=5, csc_optimal_max=3
):

    return left_trapezoidal(
        biomass / volume, csc_suitable_min, csc_suitable_max, csc_optimal_max
    )


def price_function(path, sep=";", col_size="size_count", col_price="price"):
    """
    path: path file for the price's data
    sep: delimiter/separator for the csv file
    col_size: columns name for size count of shrimp
    col_price: columns name for price of shrimp
    """
    df = pd.read_csv(path, sep=sep)
    x_sample = df[col_size].tolist()[::-1]
    y_sample = df[col_price].tolist()[::-1]
    f = CubicSpline(x_sample, y_sample, bc_type="natural")
    return f


def feed_formula3(path, sep=";", colname="Formula 3"):
    df = pd.read_csv(path, sep=sep)
    return df[colname].tolist()


def get_cycle_data(index, t, df):
    # index and t must be at the same row
    if t < index:
        start_index = index - t + 1
    else:
        start_index = index - index
    
    data = df.loc[start_index:index]
    if data.shape[0] == 1:
        data = df.loc[start_index:index+1]

    return data

def generate_interpolate_function(df, col_doc, col_function):
    f = CubicSpline(df[col_doc].values, df[col_function].values)
    return f

def generate_spline_function(df, col_doc, condition, col_function="Temp", biochem_type="temperature"):
    # col_function example is temperature
    # condition (suitable_min, optimal_min, optimal_max, suitable_max)
    if biochem_type == "temperature":
        data = [normal_trapezoidal(x, condition[0], condition[3], condition[1], condition[2]) for x in df[col_function].values]
    elif biochem_type == "nh4":
        data = [left_trapezoidal(x, condition[0], condition[3], condition[2]) for x in df[col_function].values]
    else:
        data = [normal_trapezoidal(x, condition[0], condition[3], condition[1], condition[2]) for x in df[col_function].values]

    f = CubicSpline(df[col_doc].values, data)
    return f

def integrate_function(t, function, condition, kind):
    """
    t: the time value
    function: interpolation function
    condition: list of condition
    type: type of function. ex: temperature
    """
    if (kind == "temperature") or (kind == "do"):
        return normal_trapezoidal(function(t), condition[0], condition[3], condition[1], condition[2])
    elif kind == "nh4":
        return left_trapezoidal(function(t), condition[0], condition[3], condition[2])

def get_cycle_range(df, col_doc="DOC"):
    list_index = df[df[col_doc] == 1].index
    cycles = []
    for index, value in enumerate(list_index):
        if value != list_index[-1]:
            cycles.append([value, list_index[index+1]])
        else:
            cycles.append([value])

    return cycles

import requests
from bs4 import BeautifulSoup

def fahrenheit_to_celcius(temperature):
    return 5/9*(temperature - 32)

def get_temperature_data():
    file = requests.get("https://weather.com/weather/tenday/l/6f82c91e634d2dcbac7505574acad8ec83e506bcf6ab5aa7664be72ffc76555e")
    soup = BeautifulSoup(file.content, "html.parser")

    ten_html_data = soup.find("div", {"class":"DailyForecast--DisclosureList--msYIJ"}).find_all("div", {"data-testid": "DetailsSummary"})

    time = []
    high_temperature = []
    low_temperature = []
    desc_weather = []
    percentage = []
    wind = []

    for data in ten_html_data:
        time.append(data.find("h3").text)
        try:
            high_temp = int(data.find("span", {"class": "DetailsSummary--highTempValue--3Oteu"}).text.replace("°", ""))
            high_temperature.append(fahrenheit_to_celcius(high_temp))
        except:
            high_temperature.append(None)

        try:
            low_temp = int(data.find("span", {"class": "DetailsSummary--lowTempValue--3H-7I"}).text.replace("°", ""))    
            low_temperature.append(fahrenheit_to_celcius(low_temp))
        except:
            low_temperature.append(None)
            
        desc_weather.append(data.find("span", {"class": "DetailsSummary--extendedData--365A_"}).text)
        percentage.append(data.find("span", {"data-testid": "PercentageValue"}).text)
        wind.append(data.find("span", {"data-testid": "Wind"}).text)


    df = pd.DataFrame({
        "time": time,
        "high_temperature": np.array(high_temperature),
        "low_temperature": np.array(low_temperature),
        "desc_weather": desc_weather,
        "percentage": percentage,
        "wind": wind
    })

    return df

def dawn_water_temperature(atp_max, atp_min, ptp):
    """
    atp: air temperatur on the previous day
    ptp: pond temperature on the previous afternoon
    """
    return 2.218 + 0.062*atp_max + 0.285*atp_min + 0.561*ptp

def afternoon_water_temperature(ats_max, ats_min, pts):
    """
    ats: air temperature on the same day
    pts: pond temperature at dawn of the same day
    """
    return 2.071 - 0.068*ats_min + 0.651*pts + 0.373*ats_max

def air_to_pond_temperature(df, prev_temp):
    previous_low = []
    previous_heigh = []
    current_temp = []
    for x, y in df.iterrows():
        if x == 0:
            ptp_max, ptp_min, pts_max, pts_min = prev_temp, prev_temp, prev_temp, prev_temp
            atp = (ptp_max + ptp_min)/2
            ats = (pts_max + pts_min)/2
        else:
            high = y["high_temperature"]
            low = y["low_temperature"]
            ptp_max, ptp_min, pts_max, pts_min = previous_heigh[-1], previous_low[-1], high, low
            atp = (ptp_max + ptp_min)/2
            ats = (pts_max + pts_min)/2

        dawn = dawn_water_temperature(ptp_max, ptp_min, atp)
        noon = afternoon_water_temperature(pts_max, pts_min, ats)

        previous_low.append(min((dawn, noon)))
        previous_heigh.append(max((dawn, noon)))
        current_temp.append(np.mean((dawn, noon)))

    df["pond_low"] = previous_low
    df["pond_heigh"] = previous_heigh
    df["pond_temp"] = current_temp

    return df


#########################################
# feeding
#########################################
def feeding_expense(t, fc, biomassa, final_doc, formula_type=2, r=None):
    """
    r: feeding rate
    fc: feed cost per kg
    biomassa: biomassa in gr
    formula_type: formula_type for feeding cost expense calculation. There are 1 and 2.
    """
    if formula_type == 1:
        return biomassa / 1000 * r * fc
    else:
        formula3 = feed_formula3("data/data-feeding-formula-3.csv", ",")
        if t < final_doc:
            return (formula3[t] / 1000) * (1 + 0.2) * fc
        else:
            return 0