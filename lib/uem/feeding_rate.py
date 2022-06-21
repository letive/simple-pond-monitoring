import pandas as pd

df = pd.DataFrame(
    {
        "wt": ["1-3", "3-5", "5-7", "7-9", "9-11", "11-13", "13-15", "15-17", "17-30"],
        "21-24": [0.08, 0.07, 0.065, 0.06, 0.055, 0.05, 0.045, 0.04, 0.03],
        "24-28": [0.06, 0.05, 0.045, 0.04, 0.035, 0.03, 0.024, 0.025, 0.02],
        "28-32": [0.07, 0.06, 0.055, 0.05, 0.045, 0.04, 0.035, 0.03, 0.025],
    }
)


def check_range_wt(wt):
    if (wt >= 0) and (wt <= 3):
        ret = "1-3"
    elif (wt > 3) and (wt <= 5):
        ret = "3-5"
    elif (wt > 5) and (wt <= 7):
        ret = "5-7"
    elif (wt > 7) and (wt <= 9):
        ret = "7-9"
    elif (wt > 9) and (wt <= 11):
        ret = "9-11"
    elif (wt > 11) and (wt <= 13):
        ret = "11-13"
    elif (wt > 13) and (wt <= 15):
        ret = "13-15"
    elif (wt > 15) and (wt <= 17):
        ret = "15-17"
    elif (wt > 17) and (wt <= 30):
        ret = "17-30"
    else:
        ret = None

    return ret


def check_temperature(temperture):
    if (temperture >= 21) and (temperture <= 24):
        ret = "21-24"
    elif (temperture > 24) and (temperture <= 28):
        ret = "24-28"
    elif (temperture > 28) and (temperture <= 32):
        ret = "28-32"
    else:
        ret = None

    return ret


def feeding_ratio(wt, temperature):
    index_wt = check_range_wt(wt)
    index_temp = check_temperature(temperature)

    try:
        return df[df["wt"] == index_wt][index_temp].values[0]
    except:
        return 0


def feeding_rate(wt, temperature, biomass):
    """
    wt: weight in t-1s
    temperature: temperature in t
    biomass: biomass t-1
    """
    return feeding_ratio(wt, temperature) * biomass
