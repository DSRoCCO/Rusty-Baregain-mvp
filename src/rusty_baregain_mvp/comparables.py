"""Comparables locales explicables para la demo histórica."""
def comparable_summary(history, profile):
    keys=["Brand","Model","VehicleType","Gearbox","FuelType","NotRepaired"]
    selected=history
    for key in keys+["AgeAtCrawl","PowerForModel","Mileage"]: selected=selected.loc[selected[key].eq(profile[key])]
    level="exacta"
    if len(selected)<10:
        selected=history
        for key in keys: selected=selected.loc[selected[key].eq(profile[key])]
        selected=selected.loc[(selected.AgeAtCrawl-profile["AgeAtCrawl"]).abs().le(4) & (selected.PowerForModel-profile["PowerForModel"]).abs().le(40) & (selected.Mileage-profile["Mileage"]).abs().le(50000)]
        level="bandas"
    if len(selected)<10: return {"level":"sin cobertura","n":0,"p25":None,"median":None,"p75":None}
    return {"level":level,"n":len(selected),"p25":selected.Price.quantile(.25),"median":selected.Price.median(),"p75":selected.Price.quantile(.75)}
