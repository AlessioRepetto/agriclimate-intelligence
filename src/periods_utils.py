import numpy as np
import pandas as pd


#A function created to filter a climate dataframe so that it keeps only the rows corresponding to the months of interest.
def filter_by_period(df, months_to_keep):
    df = df.copy()
    df["MONTH_NUM"] = df["YEAR_MONTH"].str[-2:].astype(int)
    filtered = df[df["MONTH_NUM"].isin(months_to_keep)].copy()
    filtered.drop(columns=["MONTH_NUM"], inplace=True)
    return filtered



#Aggregates monthly climate data into annual features for each period.
#variables = list of climate variables to aggregate (e.g. ["rain", "temp_mean"])
def aggregate_period(df, variables):
    agg_dict = {}

    for var in variables:
        agg_dict[var + "_sum"] = ("{}".format(var), "sum")
        agg_dict[var + "_mean"] = ("{}".format(var), "mean")
        agg_dict[var + "_max"] = ("{}".format(var), "max")
        agg_dict[var + "_min"] = ("{}".format(var), "min")

    return df.groupby(["province", "year"]).agg(**agg_dict).reset_index()


#Creates planting, vegetative, ripening features for a crop.
#Returns a single merged DataFrame province-year with all features.
def build_crop_features(climate_df, crop, variables):
    filtered = filter_by_period(climate_df, crop)
    
    agg_results = {}
    for period_name, df_period in filtered.items():
        agg_results[period_name] = aggregate_period(df_period, variables)
        # rename columns to include period name
        agg_results[period_name] = agg_results[period_name].rename(
            columns={col: f"{period_name}_{col}" for col in agg_results[period_name].columns if col not in ["province", "year"]}
        )
        
    final = agg_results["planting"]
    final = final.merge(agg_results["vegetative"], on=["province", "year"], how="left")
    final = final.merge(agg_results["ripening"], on=["province", "year"], how="left")

    return final
