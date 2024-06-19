import pandas as pd

# we want to take in CHICAGO_matched.csv,
# look at all of the BLDGIDs
# and make a new csv for each one that summarizes the values from CHICAGO_matched.csv

prefix = 'CHICAGO_weather_summaries/Chi0_BldgWeather_90m_'

fp = 'CHICAGO_matched.csv'
df = pd.read_csv(fp)

building_ids = list(set(df['BLDGID']))
for bldg_id in building_ids:
    rows = df.loc[df['BLDGID'] == bldg_id]
    #                 summarise(T_K=mean(Temp.K.),
    #                           T_F=mean(T_F),
    #                           RH=mean(RelHumid),
    #                           DewPoint_K=mean(DewPoint.K.),
    #                           Pressure=mean(Pressure),
    #                           RadDir_Wm2=mean(RadDir.Wm.2.),
    #                           RadDiff_Wm2=mean(RadDiff.Wm.2.),
    #                           LWRad=mean(LWRad),
    #                           SWNorm=mean(SWNorm),
    #                           SWRad=mean(SWRad),
    #                           WindDir_from=mean(WindDir.from.),
    #                           WindSpd_ms=mean(WindSpeed.ms.1.)),
    foo = {'T_K': 'Temp.K.', 'T_F': 'T_F', 'RH': 'RelHumid', 'DewPoint': 'DewPoint.K.',
           'Pressure': 'Pressure', 'RadDir_Wm2': 'RadDir.Wm.2.', 'RadDiff_Wm2': 'RadDiff.Wm.2.',
           'LWRad': 'LWRad', 'SWNorm': 'SWNorm', 'SWRad': 'SWRad', 'WindDir': 'WindDir.from.',
           'WindSpd_ms': 'WindSpeed.ms.1.'}
    new_df = pd.DataFrame()
    for key, val in foo.items():
        new_df[key] = [rows[val].mean()]
    new_df.to_csv(prefix + str(bldg_id) + '.csv')
