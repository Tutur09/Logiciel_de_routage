import requests
import json
import math

import xml.etree.ElementTree as ET
from urllib.parse import quote,urlencode
import matplotlib.pyplot as plt
import cfgrib
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs

from datetime import datetime, timedelta,timezone
from PIL import Image
import io
import os
from time import sleep



# pip install ecmwflibs
# pip install eccodes==1.3.1

# pip install cfgrib
#pip install pyshp (sinon cartopy ne fonctionne pas bien)




url = 'https://portail-api.meteofrance.fr/web/fr/api/AROME'
id = 'sergelhoste'
password = 'Secret123-'

speed_limit = 2

def list_data_variable():
    data = {
        'Altitude': {'Coverage name': 'GEOMETRIC_HEIGHT__GROUND_OR_WATER_SURFACE', 'Height cluster': False, 'Variable': 'h','Suffix':''},
        'Brightness': {'Coverage name': 'BRIGHTNESS_TEMPERATURE__GROUND_OR_WATER_SURFACE', 'Height cluster': False, 'Variable': 'unknown','Suffix':''},
        'Convective energy': {'Coverage name': 'CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY__GROUND_OR_WATER_SURFACE', 'Height cluster': False, 'Variable': 'CAPE_INS','Suffix':''},
        'Precipitation water': {'Coverage name': 'TOTAL_WATER_PRECIPITATION__GROUND_OR_WATER_SURFACE', 'Height cluster': None, 'Variable': 'tirf','Suffix':'PT1H'},
        'Wind gust': {'Coverage name': 'WIND_SPEED_GUST__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster': True, 'Variable': 'fg10','Suffix':''},
        'Wind speed': {'Coverage name': 'WIND_SPEED__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster': True, 'Variable': 'si10','Suffix':''},
        'Humidity': {'Coverage name': 'RELATIVE_HUMIDITY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster': True, 'Variable': 'r','Suffix':''},
        'Low cloud': {'Coverage name': 'LOW_CLOUD_COVER__GROUND_OR_WATER_SURFACE', 'Height cluster': None, 'Variable': 'lcc','Suffix':''},
        'High cloud': {'Coverage name': 'HIGH_CLOUD_COVER__GROUND_OR_WATER_SURFACE', 'Height cluster': None, 'Variable': 'hcc','Suffix':''},
        'Medium cloud': {'Coverage name': 'MEDIUM_CLOUD_COVER__GROUND_OR_WATER_SURFACE', 'Height cluster': None, 'Variable': 'mcc','Suffix':''},
        'Snow': {'Coverage name': 'TOTAL_SNOW_PRECIPITATION__GROUND_OR_WATER_SURFACE', 'Height cluster': None, 'Variable': None,'Suffix':''},
        'Precipitation': {'Coverage name': 'TOTAL_PRECIPITATION__GROUND_OR_WATER_SURFACE', 'Height cluster': None, 'Variable': 'tp','Suffix':'PT1H'},
        'Pressure': {'Coverage name': 'PRESSURE__GROUND_OR_WATER_SURFACE', 'Height cluster': False, 'Variable': 'sp','Suffix':''},
        'Precipitation rate': {'Coverage name': 'TOTAL_PRECIPITATION_RATE__GROUND_OR_WATER_SURFACE', 'Height cluster': None, 'Variable': 'unkown','Suffix':''},
        'Temperature': {'Coverage name': 'TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster': True, 'Variable': None,'Suffix':''},
        'X gust': {'Coverage name': 'U_COMPONENT_OF_WIND_GUST__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster': True, 'Variable': 'efg10','Suffix':''}, #ugust efg10
        'X wind': {'Coverage name': 'U_COMPONENT_OF_WIND__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster': True, 'Variable': 'u10','Suffix':''},
        'Y gust': {'Coverage name': 'V_COMPONENT_OF_WIND_GUST__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster': True, 'Variable': 'nfg10','Suffix':''}, #vgust nfg10
        'Y wind': {'Coverage name': 'V_COMPONENT_OF_WIND__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster': True, 'Variable': 'v10','Suffix':''}
    }
#U is East_West, V is North_South
    return data


def list_data_variable_PI():
    data = {
        'Adiabatic TWP 27315': { 'Coverage name':'TPW_27315_HEIGHT__LEVEL_OF_ADIABATIC_CONDESATION', 'Height cluster':False ,'Variable':'h' ,'Suffix':'' } ,
        'Adiabatic TWP 27415': { 'Coverage name':'TPW_27415_HEIGHT__LEVEL_OF_ADIABATIC_CONDESATION ', 'Height cluster':False ,'Variable':'h' ,'Suffix':'' } ,
        'Adiabatic TWP 27465': { 'Coverage name':'TPW_27465_HEIGHT__LEVEL_OF_ADIABATIC_CONDESATION', 'Height cluster':False ,'Variable':'h' ,'Suffix':'' } ,
        'Brightness': { 'Coverage name':'BRIGHTNESS_TEMPERATURE__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'unknown' ,'Suffix':'' } ,
        'Convective energy': { 'Coverage name':'CONVECTIVE_AVAILABLE_POTENTIAL_ENERGY__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'CAPE_INS' ,'Suffix':'' } ,
        'Grele': { 'Coverage name':'DIAG_GRELE__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'unknown' ,'Suffix':'' } ,
        'Total water precipitation': { 'Coverage name':'TOTAL_WATER_PRECIPITATION__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Wind speed': { 'Coverage name':'WIND_SPEED_GUST_15MIN__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'' ,'Suffix':'' } ,
        'Wind speed max': { 'Coverage name':'WIND_SPEED_MAXIMUM_GUST__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'' ,'Suffix':'' } ,
        'Wind speed gust': { 'Coverage name':'WIND_SPEED_GUST__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'fg10' ,'Suffix':'' } ,
        'Graupel': { 'Coverage name':'GRAUPEL__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Hail': { 'Coverage name':'HAIL__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Relative humidity': { 'Coverage name':'RELATIVE_HUMIDITY__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'' ,'Suffix':'' } ,
        'Mocon': { 'Coverage name':'MOCON__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Low cloud': { 'Coverage name':'LOW_CLOUD_COVER__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'lcc' ,'Suffix':'' } ,
        'Total snow': { 'Coverage name':'TOTAL_SNOW_PRECIPITATION__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Total precipitation': { 'Coverage name':'TOTAL_PRECIPITATION__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Solid precipitation': { 'Coverage name':'SOLID_PRECIPITATION__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Severe precipitation type': { 'Coverage name':'SEVERE_PRECIPITATION_TYPE_15_MIN__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'ptype' ,'Suffix':'' } ,
        'Precipitation type 15': { 'Coverage name':'PRECIPITATION_TYPE_15_MIN__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'ptype' ,'Suffix':'' } ,
        'Pressure': { 'Coverage name':'PRESSURE__SEA_SURFACE', 'Height cluster':False ,'Variable':'prmsl' ,'Suffix':'' } ,
        'Reflectivity': { 'Coverage name':'REFLECTIVITY_MAX_DBZ__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'unknown' ,'Suffix':'' } ,
        'Total precipitation rate': { 'Coverage name':'TOTAL_PRECIPITATION_RATE__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'unkwown' ,'Suffix':'' } ,
        'Dew point': { 'Coverage name':'DEW_POINT_TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'' ,'Suffix':'' } ,
        'Temperature ground': { 'Coverage name':'TEMPERATURE__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Temperature': { 'Coverage name':'TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'X wind': { 'Coverage name':'U_COMPONENT_OF_WIND_GUST_15MIN__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'efg10' ,'Suffix':'' } ,
        'X gust': { 'Coverage name':'U_COMPONENT_OF_WIND_GUST__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'efg10' ,'Suffix':'' } ,
        'Visibility mini precipitation': { 'Coverage name':'VISIBILITY_MINI_PRECIP_15MIN__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Visibility mini': { 'Coverage name':'VISIBILITY_MINI_15MIN__GROUND_OR_WATER_SURFACE', 'Height cluster':False ,'Variable':'' ,'Suffix':'' } ,
        'Y wind': { 'Coverage name':'V_COMPONENT_OF_WIND_GUST_15MIN__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'nfg10' ,'Suffix':'' } ,
        'Y gust': { 'Coverage name':'V_COMPONENT_OF_WIND_GUST__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'nfg10' ,'Suffix':'' } ,
        'Wetb temperature': { 'Coverage name':'WETB_TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND', 'Height cluster':True ,'Variable':'' ,'Suffix':'' }
    }
    return data


# Arome
arome = {'name': 'Arome',
         'API_key' : 'eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJzZXJnZWxob3N0ZUBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6InNlcmdlbGhvc3RlIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6MTA1ODEsInV1aWQiOiJhZTE2MTcxNi1mZGRlLTRkMWQtYjFlNC03ZjBiMWYzMTZhOTgifSwiaXNzIjoiaHR0cHM6XC9cL3BvcnRhaWwtYXBpLm1ldGVvZnJhbmNlLmZyOjQ0M1wvb2F1dGgyXC90b2tlbiIsInRpZXJJbmZvIjp7IjUwUGVyTWluIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJncmFwaFFMTWF4Q29tcGxleGl0eSI6MCwiZ3JhcGhRTE1heERlcHRoIjowLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOiJzZWMifX0sImtleXR5cGUiOiJQUk9EVUNUSU9OIiwic3Vic2NyaWJlZEFQSXMiOlt7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiQVJPTUUtUEkiLCJjb250ZXh0IjoiXC9wdWJsaWNcL2Fyb21lcGlcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluX21mIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJQcmV2aXNpb25JbW1lZGlhdGVQcmVjaXBpdGF0aW9ucyIsImNvbnRleHQiOiJcL3Byb1wvcGlhZlwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkFST01FIiwiY29udGV4dCI6IlwvcHVibGljXC9hcm9tZVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn1dLCJ0b2tlbl90eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzEwMzI1MDI2LCJqdGkiOiJlM2VlNjcxOC00NjU0LTRlZDMtODIwNy04YmI3YmUyZGE0ZjYifQ==.BZQydOZlbhNKqc8JcSH15u2ajnFVvLm1D0MzQ-abG92UBSWu0bi7LOBKBcEqZJTHE2C4q6sw_Mc3ne4IBA-fcVVK4dtgS17hVDyQWiW2kyqkG96l5xGyVX_WCEH671taZ1zBx4BAsp1uOHHQIF9t1xiuVDEDSPZYnsWqxvPzdNyStZXpP2Co4Q9wbE-Z4GMXf8i3sOlkNAv-RjVwevAJPTF3tIt0DlLyrH0HaMlNBl_Cy11VVnoRCbnu1I47_T0P-cL_RWj5wgZVPTUOYzUCsUezYEuv0MvpTvs_j_eff_MmpOdb6AiylJvbt3f6lzxX1IA0hffbCjTg7rWKrMvdhA==',
        'url' : 'https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS/',
         'capa' : 'GetCapabilities?service=WCS&version=2.0.1&language=eng',
         'describe' : 'DescribeCoverage?service=WCS&version=2.0.1',
         'coverage' : 'GetCoverage?service=WCS&version=2.0.1',
         'field': list_data_variable }

#Arome PI
arome_PI = { 'name': 'Arome_PI',
             'API_key' : 'eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJzZXJnZWxob3N0ZUBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6InNlcmdlbGhvc3RlIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6MTA1ODEsInV1aWQiOiJhZTE2MTcxNi1mZGRlLTRkMWQtYjFlNC03ZjBiMWYzMTZhOTgifSwiaXNzIjoiaHR0cHM6XC9cL3BvcnRhaWwtYXBpLm1ldGVvZnJhbmNlLmZyOjQ0M1wvb2F1dGgyXC90b2tlbiIsInRpZXJJbmZvIjp7IjUwUGVyTWluIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJncmFwaFFMTWF4Q29tcGxleGl0eSI6MCwiZ3JhcGhRTE1heERlcHRoIjowLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOiJzZWMifX0sImtleXR5cGUiOiJQUk9EVUNUSU9OIiwic3Vic2NyaWJlZEFQSXMiOlt7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiQVJPTUUiLCJjb250ZXh0IjoiXC9wdWJsaWNcL2Fyb21lXC8xLjAiLCJwdWJsaXNoZXIiOiJhZG1pbl9tZiIsInZlcnNpb24iOiIxLjAiLCJzdWJzY3JpcHRpb25UaWVyIjoiNTBQZXJNaW4ifSx7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiUHJldmlzaW9uSW1tZWRpYXRlUHJlY2lwaXRhdGlvbnMiLCJjb250ZXh0IjoiXC9wcm9cL3BpYWZcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluX21mIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJBUk9NRS1QSSIsImNvbnRleHQiOiJcL3B1YmxpY1wvYXJvbWVwaVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNPYnNlcnZhdGlvbiIsImNvbnRleHQiOiJcL3B1YmxpY1wvRFBPYnNcL3YxIiwicHVibGlzaGVyIjoiYmFzdGllbmciLCJ2ZXJzaW9uIjoidjEiLCJzdWJzY3JpcHRpb25UaWVyIjoiNTBQZXJNaW4ifV0sImV4cCI6MTgxMTExNDE1NSwidG9rZW5fdHlwZSI6ImFwaUtleSIsImlhdCI6MTcxMTExNDE1NSwianRpIjoiM2Y2YzRmNDItMjc1My00ZjdkLTg3ZTUtOTNiZDEyN2NmMmMzIn0=.MI_X5Am5oNv-EfuvKHkb1j1Xi-4NwYZAQpcNaKFc72mQww9jUFj_rGMv34DqMyco3e_Y7uCIL-hMRWoHNghgjem2lonH9q5ZBfouUBI-BksTdLRj168BTdUKeStCtvC_-JvITBuDUkOH_-8PWBIMbLi6r3pRF_bw6WSrbgN2XgZy90trjDsJU1MkdFoEaNJ8NM1IeKqADjvXaE7MUOA9Ee7hfGSY_-NewqqQpKYWS2DVz94Ak4JeGqRw7SNeOIOFE8bASv7wCylVvQzYqwbiYEe4rhUKWkVhm4x0xJeWcPBwZN_8hVuy9LeI8-P3GKQRA4qJsX68cvrJS-xluxrc5w==',
            'url' : 'https://public-api.meteofrance.fr/public/aromepi/1.0/wcs/MF-NWP-HIGHRES-AROMEPI-001-FRANCE-WCS/',
            'capa' : 'GetCapabilities?service=WCS&version=2.0.1&language=eng',
            'describe': 'DescribeCoverage?service=WCS&version=2.0.1',
            'coverage' : 'GetCoverage?service=WCS&version=2.0.1',
            'field': list_data_variable_PI}



#Observation
observation = { 'API_key' : 'eyJ4NXQiOiJZV0kxTTJZNE1qWTNOemsyTkRZeU5XTTRPV014TXpjek1UVmhNbU14T1RSa09ETXlOVEE0Tnc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJzZXJnZWxob3N0ZUBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6InNlcmdlbGhvc3RlIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJEZWZhdWx0QXBwbGljYXRpb24iLCJpZCI6MTA1ODEsInV1aWQiOiJhZTE2MTcxNi1mZGRlLTRkMWQtYjFlNC03ZjBiMWYzMTZhOTgifSwiaXNzIjoiaHR0cHM6XC9cL3BvcnRhaWwtYXBpLm1ldGVvZnJhbmNlLmZyOjQ0M1wvb2F1dGgyXC90b2tlbiIsInRpZXJJbmZvIjp7IjUwUGVyTWluIjp7InRpZXJRdW90YVR5cGUiOiJyZXF1ZXN0Q291bnQiLCJncmFwaFFMTWF4Q29tcGxleGl0eSI6MCwiZ3JhcGhRTE1heERlcHRoIjowLCJzdG9wT25RdW90YVJlYWNoIjp0cnVlLCJzcGlrZUFycmVzdExpbWl0IjowLCJzcGlrZUFycmVzdFVuaXQiOiJzZWMifX0sImtleXR5cGUiOiJQUk9EVUNUSU9OIiwic3Vic2NyaWJlZEFQSXMiOlt7InN1YnNjcmliZXJUZW5hbnREb21haW4iOiJjYXJib24uc3VwZXIiLCJuYW1lIjoiQVJPTUUtUEkiLCJjb250ZXh0IjoiXC9wdWJsaWNcL2Fyb21lcGlcLzEuMCIsInB1Ymxpc2hlciI6ImFkbWluX21mIiwidmVyc2lvbiI6IjEuMCIsInN1YnNjcmlwdGlvblRpZXIiOiI1MFBlck1pbiJ9LHsic3Vic2NyaWJlclRlbmFudERvbWFpbiI6ImNhcmJvbi5zdXBlciIsIm5hbWUiOiJQcmV2aXNpb25JbW1lZGlhdGVQcmVjaXBpdGF0aW9ucyIsImNvbnRleHQiOiJcL3Byb1wvcGlhZlwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkFST01FIiwiY29udGV4dCI6IlwvcHVibGljXC9hcm9tZVwvMS4wIiwicHVibGlzaGVyIjoiYWRtaW5fbWYiLCJ2ZXJzaW9uIjoiMS4wIiwic3Vic2NyaXB0aW9uVGllciI6IjUwUGVyTWluIn0seyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IkRvbm5lZXNQdWJsaXF1ZXNPYnNlcnZhdGlvbiIsImNvbnRleHQiOiJcL3B1YmxpY1wvRFBPYnNcL3YxIiwicHVibGlzaGVyIjoiYmFzdGllbmciLCJ2ZXJzaW9uIjoidjEiLCJzdWJzY3JpcHRpb25UaWVyIjoiNTBQZXJNaW4ifV0sInRva2VuX3R5cGUiOiJhcGlLZXkiLCJpYXQiOjE3MTAzNjgxNDUsImp0aSI6ImU1ZWU3YjMxLTBmNTMtNDEyZS04ZWQzLWRlOGQyMWJmNmJiNCJ9.TxuyCyluACdhKNlO8Y01n0jmug89fx7uVa-Xdf2JrKSrtgHEUKDfIJ4dPTnAChmoDEG74ci8GACvINZgo_6RzOR32PtguXbBardFTGPiYPKk-t12U_mi6-9cEjIld_sUeeBSSDoIE9v9GWKy2HLO9eBHX6aq-x6sDv0g_7aMCIQsiCKe6NM1Jv0nCVi70nRaHt3mYvlNtqA0l1XEOTYy4PKTTTRjPL6so7kz6-tepn0RtfHhITRcylg-F3ki9ulyOP20VScvT0dh2zMeDMBt9rTMmx05FsMWe509a8eqdC3EAWlKXiye6i5GmrWQPMauzCo-RKmOGBLjFe61EfOJ6w==',
                'url' : 'https://public-api.meteofrance.fr/public/DPObs/v1/station/infrahoraire-6m' }








def encode_string(string_to_encode):

    # URL-encode the string
    return quote(string_to_encode)



def get_suffix(value,splitter):
    return value[len(value.split(splitter)[0])+len(splitter):]


def uv_to_speed_direction(u, v):
    """
    Convert U and V wind components to wind speed and direction.

    Parameters:
    - u: U component of wind (wind speed in the east-west direction, m/s).
    - v: V component of wind (wind speed in the north-south direction, m/s).

    Returns:
    - speed: Wind speed (m/s).
    - direction: Wind direction (degrees from geographic north, clockwise).
    """
    speed = np.sqrt(u**2 + v**2)
    direction = np.arctan2(-u, -v) * (180 / np.pi)  # Convert radians to degrees
    direction = np.mod(direction, 360)  # Ensure direction is in range [0, 360)
    
    return speed, direction

#Get capabilities
def get_capabilities(api = arome):
    print('Get capabilitities')
    # Set the URL for the GET request
    url = api['url'] + api['capa']

    # Add headers, including the API key
    headers = {
        'accept': '*/*',
        'apikey': api['API_key']
    }
        

    # Send the GET request
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Parse the XML from the response
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()

        ET.indent(root, space="  ", level=0)

        # Convert the tree to a string
        pretty_xml = ET.tostring(root, 'utf-8').decode('utf-8')

        if False:
        # Print the nicely formatted XML
            print(pretty_xml)



        layers = {}
        time_data = []
        
        for coverage in tree.findall('.//{http://www.opengis.net/wcs/2.0}CoverageId'):
            split_name = coverage.text.split('___')
            if len(split_name) > 1:  # Ensure there are at least two elements after splitting
                if split_name[0] not in layers:
                    layers[split_name[0]] = [{'Time serie':split_name[1],'Time stamp':datetime.strptime(split_name[1].split('_')[0].replace(".", ":"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),'Suffix':get_suffix(split_name[1],'_')}]
                else:
                    layers[split_name[0]].append({'Time serie':split_name[1],'Time stamp':datetime.strptime(split_name[1].split('_')[0].replace(".", ":"), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc),'Suffix':get_suffix(split_name[1],'_')})
            if split_name[1] not in time_data:
                time_data.append(split_name[1])
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(response.text)
        return layers

    time_value = [datetime.strptime(ts.split('_')[0].replace(".", ":"), "%Y-%m-%dT%H:%M:%SZ") for ts in time_data]
    
    
    time_slots={}
    time_suffix=[]
    for data in time_data:
        split_name = data.split('_')
        if len(split_name) > 1:  # Ensure there are at least two elements after splitting
            if split_name[0] not in time_slots:
                time_slots[split_name[0]] = [split_name[1]]
            else:
                time_slots[split_name[0]].append(split_name[1])
            if split_name[1] not in time_suffix:
                time_suffix.append(split_name[1])
        else:
            if split_name[0] not in time_slots:
                time_slots[split_name[0]] = ['']
            
    time_suffix.sort()

    return layers

# Set the URL for the GET request
#Describe coverage


def describe_coverage(coverage,api=arome):
    print('Describe coverage', coverage)
    url = api['url'] + api['describe'] + '&coverageID=' + coverage
    # Add headers, including the API key
    headers = {
        'accept': '*/*',
        'apikey': api['API_key']
    }

    # Send the GET request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the XML from the response
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()

        ET.indent(root, space="  ", level=0)

        # Convert the tree to a string
        pretty_xml = ET.tostring(root, 'utf-8').decode('utf-8')

        # Define your namespaces with prefixes as they appear in the XML
        namespaces = {
            'ns0': 'http://www.opengis.net/wcs/2.0',
            'ns2': 'http://www.opengis.net/gml/3.2',
            'ns3': 'http://www.opengis.net/gml/3.3/rgrid',
            'ns4': 'http://www.opengis.net/gmlcov/1.0',
            'ns5': 'http://www.opengis.net/swe/2.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',        # Add other namespaces if necessary
        }

        start_time = root.findall('.//ns2:beginPosition', namespaces=namespaces)[0].text
        end_time = root.findall('.//ns2:endPosition', namespaces=namespaces)[0].text
        general_grid_axes = root.findall('.//ns3:GeneralGridAxis', namespaces)
        coefficients_element = None
        for axis in general_grid_axes:
            # Check if this axis is for time
            grid_axes_spanned = axis.find('ns3:gridAxesSpanned', namespaces)
            if grid_axes_spanned is not None and grid_axes_spanned.text == "time":
                # Extracting coefficients for the time axis
                coefficients = axis.find('ns3:coefficients', namespaces)
                if coefficients is not None and coefficients.text:
                    coefficients_element = coefficients.text

        if coefficients_element is not None:
            coefficients = list(map(int, coefficients_element.split()))
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return start_time,end_time, coefficients
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None,None, None

lat_sub = (45,48)
long_sub =(-5,-1)

def get_coverage(coverage, time , subset='height(10)', format_answer = 'application/wmo-grib',file_name= 'data.grib' , lat_sub = (45,48),long_sub =(-5,-1),api=arome):
    print('Getting coverage', coverage, time)

    if subset !=None:
        url = api['url'] + api['coverage'] + '&coverageid=' + coverage +  '&subset=time(' + time.strftime('%Y-%m-%dT%H:%M:%SZ') + ')&subset=' + subset +'&subset=lat' + str(lat_sub) +'&subset=long'+ str(long_sub) +'&format=' + format_answer
    else:
        url = api['url'] + api['coverage'] + '&coverageid=' + coverage +  '&subset=time(' + time.strftime('%Y-%m-%dT%H:%M:%SZ') + ')&subset=lat' + str(lat_sub) +'&subset=long'+ str(long_sub) +'&format=' + format_answer

    headers = {
        'accept': '*/*',
        'apikey': api['API_key']
    }

    # Send the GET request
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Save the content to a file
        if format_answer == 'application/wmo-grib':
            with open(file_name, 'wb') as file:
                file.write(response.content)
            print(f"The data has been saved to {file_name}.")



            
        else:
            with open(file_name,'wb') as file:
                file.write(response.content)
            print(f"The data has been saved to {file_name}.")
            img = Image.open(io.BytesIO(response.content))
            plt.imshow(img)
            plt.axis('off')  # Optional: Remove axes for clarity
            plt.show()
        return True
    else:
        print(f"Failed to retrieve data: HTTP status code {response.status_code}")
        print(response.text)
        return False

def list_grib_variables(file_name):
    # Open the GRIB file
    ds = xr.open_dataset(file_name, engine='cfgrib')
    variable_names = list(ds.data_vars)
    return variable_names


def display_grib(variable_name, time, grib, cmap='coolwarm', range_color=None, display=False, save_fig=True, file_name='image.jpg',
                 corner1=None, corner2=None):  # Add subset bounds as optional arguments
    if corner1 is not None and corner2 is not None:
        min_lat = (min(corner1[0],corner2[0])+360) % 360            
        min_lon = (min(corner1[1],corner2[1])+360) % 360
        max_lat = (max(corner1[0],corner2[0])+360) % 360
        max_lon = (max(corner1[1],corner2[1]) +360) % 360
    else:
        min_lat = None            
        min_lon = None
        max_lat = None
        max_lon = None 
    print(min_lat,max_lat, min_lon, max_lon)    
    print(50*'-')
    print(f'Display grib variable name {variable_name} for time {time}')
    idx = np.where(grib['actual time'].values <= np.datetime64(time))[0][-1]

    # Extract the value
    value = grib['actual time'].values[idx]
    variable = grib.sel({"actual time": value}, method='nearest')[variable_name]
    print(variable.latitude.min().values,variable.latitude.max().values,variable.longitude.min().values,variable.longitude.max().values)
    # If subset bounds are provided, filter the data
    if min_lat is not None and min_lon is not None and max_lat is not None and max_lon is not None:
        variable = variable.sel(latitude=slice(min_lat, max_lat), longitude=slice(min_lon, max_lon))
    # Define the projection
    projection = ccrs.PlateCarree()

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': projection})

    # Plot the data
    if range_color is None:
        variable.plot(ax=ax, transform=ccrs.PlateCarree(), x='longitude', y='latitude', cmap=cmap)
    else:
        variable.plot(ax=ax, transform=ccrs.PlateCarree(), x='longitude', y='latitude', cmap=cmap, vmin=range_color[0], vmax=range_color[1])

    # Add features with Cartopy
    ax.coastlines(resolution='10m')  # Add coastlines
    ax.gridlines(draw_labels=True)  # Add grid lines and labels

    value_datetime = pd.to_datetime(value)  # Convert to datetime.datetime object
    formatted_date = value_datetime.strftime('%d/%m %H:%MZ')
    plt.title(variable_name + ' ' + formatted_date)

    # Define buoys
    bouees = {
    'Treho':(47.557967,-3.009533),
    'Roche Révision':(47.543883,-2.989317),
    'Men Er Roué':(47.53755,-3.10095),
    'Buisson de Méaban':(47.527633,-2.974933),
    'Méaban':(47.512883,-2.937033),
    'Bugalet':(47.52075,-3.091033),
    'Quiberon Nord':(47.49415,-3.043),
    'Quiberon Sud':(47.467333,-3.03905),
    'Rond C':(47.520167,-3.041417)}

    # Optionally, filter buoys based on the provided subset bounds
    if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
        bouees = {label: (lat, lon) for label, (lat, lon) in bouees.items() if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon}

    latitudes, longitudes = zip(*bouees.values()) if bouees else ([], [])

    # Plotting
    if bouees:
        plt.scatter(longitudes, latitudes, transform=ccrs.PlateCarree())  # Note the order: x (longitudes), then y (latitudes)

        # Optionally, add labels for each point
        for label, (lat, lon) in bouees.items():
            ax.text(lon, lat, label, transform=ccrs.PlateCarree())

    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

    # Apply tight layout
    plt.tight_layout()

    if save_fig:
        fig.savefig(file_name, dpi=200)
    if display:
        plt.show()
    else:
        plt.close()


def plot_values(values, display = False, save_fig= True, file_name = 'image.jpg'):
    fig, ax = plt.subplots(figsize=(14, 10))

    plt.plot(values)
    if save_fig:
        fig.savefig(file_name, dpi=200)
    if display:
        plt.show()
    else:
        plt.close()


def get_value_grib_pos(variable_name,lat,long,grib):
    selected_values = grib.sel(
    {"latitude": lat, "longitude": long},
    method="nearest"  # This finds the nearest available data point if the exact match isn't found
    )[variable_name].values
    selected_times = grib.sel(
    {"latitude": lat, "longitude": long},
    method="nearest"  # This finds the nearest available data point if the exact match isn't found
    )['actual time'].values
    
    return pd.Series(data=selected_values, index=pd.to_datetime(selected_times, utc=True))




   


def value_grib_pos(information,lat,long,grib):
    coverages = list_data_variable()
    variable_name = coverages[information]['Variable']
    variable = grib[variable_name]
    
    value = variable.sel(latitude=lat, longitude=long, method='nearest').values
    return value.item()





def list_stations():
    station_list = { 'Vannes-Meucon':{'lat':47.722000,'lon':-2.727000,'code':'56137001'},
                'Naizin':{'lat':48.005333,'lon':-2.816500,'code':'56144001'},
                'Pontivy':{'lat':48.055667,'lon':-2.916667,'code':'56151001'},
                'Pleucadeuc':{'lat':47.765500,'lon':-2.387167,'code':'56159001'},
                'Ploerdut':{'lat':48.090667,'lon':-3.308833,'code':'56163001'},
                'Ploermel':{'lat':47.950833,'lon':-2.397500,'code':'56165003'},
                'Plouay':{'lat':47.916167,'lon':-3.344500,'code':'56166005'},
                'Lorient Lann Bihoue':{'lat':47.762833,'lon':-3.435667,'code':'56185001'},
                'Quiberon':{'lat':47.479833,'lon':-3.099000,'code':'56186003'},
                'Sarzeau':{'lat':47.510667,'lon':-2.796000,'code':'56240003'},
                'Vannes-Sene':{'lat':47.604500,'lon':-2.714167,'code':'56243001'}}
    return station_list


def convert_to_readable_format(data):
    # Mapping of original keys to more descriptive names
    key_mapping = {
        'lat': 'Latitude',
        'lon': 'Longitude',
        'geo_id_insee': 'Geographic ID (INSEE)',
        'reference_time': 'Reference Time (UTC)',
        'insert_time': 'Insert Time (UTC)',
        'validity_time': 'Validity Time (UTC)',
        't': 'Temperature',
        'td': 'Dew Point',
        'u': 'Relative Humidity',
        'dd': 'Wind Direction',
        'ff': 'Wind Speed',
        'dxi10': 'Gust Direction',
        'fxi10': 'Gust Speed',
        'rr_per': 'Precipitation (mm)',
        't_10': 'Temperature at 10cm Depth',
        't_20': 'Temperature at 20cm Depth',
        't_50': 'Temperature at 50cm Depth',
        't_100': 'Temperature at 100cm Depth',
        'vv': 'Visibility',
        'etat_sol': 'State of the Ground',
        'sss': 'Snow Depth',
        'insolh': 'Sunshine Duration',
        'ray_glo01': 'Global Radiation',
        'pres': 'Atmospheric Pressure (Pa)',
        'pmer': 'Sea-Level Atmospheric Pressure (Pa)'
    }

    # Convert the data using the mapping
    readable_data = {key_mapping.get(k, k): v for k, v in data.items()}

    for temp in ['Temperature', 'Dew Point','Temperature at 10cm Depth','Temperature at 20cm Depth','Temperature at 50cm Depth','Temperature at 100cm Depth']:
        if not(readable_data[temp] is None):
            readable_data[temp]=readable_data[temp]-273.15
    if not(readable_data['Wind Speed'] is None):
        readable_data['Wind Speed']=readable_data['Wind Speed']*3.6/1.852
    if not(readable_data['Gust Speed'] is None):
        readable_data['Gust Speed']=readable_data['Gust Speed']*3.6/1.852
    # Return or print the converted data
    return readable_data



def get_observation(station_name  = 'Quiberon', api = observation):
    stations = list_stations()
    station = stations[station_name]['code']

    url = api['url'] + '?id_station=' + station + '&format=json'
    
    # Add headers, including the API key
    headers = {
        'accept': '*/*',
        'apikey': api['API_key']
    }

    # Send the GET request
    try:
        # Send the GET request
        response = requests.get(url, headers=headers)
        
        # Check if the response was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            if len(data)>0:
                json_data = convert_to_readable_format(data[0])
                return json_data
            else:
                print(f'No data for {station_name}')
                return None
        else:
            print(f"Error: Unable to fetch data for {station_name}. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"An HTTP error occurred: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def plot_stations(list_display=['Quiberon', 'Sarzeau', 'Vannes-Sene']):
    all_stations = list_stations()  # Assuming this returns detailed info including wind speed and direction
    if list_display == None:
        selected_stations = all_stations
    else:
        selected_stations = {name: all_stations[name] for name in list_display if name in all_stations}

    projection = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': projection})

    for name, station in selected_stations.items():
        lat = station['lat']
        lon = station['lon']
        observation = get_observation(name)
        if not(observation is None):
            wind_speed = observation['Wind Speed']  # Assuming wind speed is in knots
            wind_dir = observation['Wind Direction']  # Assuming wind direction is in degrees from north
            gust_speed = observation['Gust Speed']  # Assuming wind speed is in knots
            gust_dir = observation['Gust Direction']  # Assuming wind direction is in degrees from north
            if gust_speed !=None:
                # Convert wind direction to radians and calculate U and V components
                if not(wind_dir is None):
                    gust_dir_rad = math.radians(gust_dir+180)
                    u = gust_speed * math.sin(gust_dir_rad)
                    v = gust_speed * math.cos(gust_dir_rad)

                    # Plot the wind vector using a quiver plot
                    ax.quiver(lon, lat, u, v, transform=ccrs.PlateCarree(), color='grey', scale=100)
            if wind_speed !=None:
                # Convert wind direction to radians and calculate U and V components
                if not(wind_dir is None):
                    wind_dir_rad = math.radians(wind_dir+180)
                    u = wind_speed * math.sin(wind_dir_rad)
                    v = wind_speed * math.cos(wind_dir_rad)

                    # Plot the wind vector using a quiver plot
                    ax.quiver(lon, lat, u, v, transform=ccrs.PlateCarree(), color='blue', scale=100)

                # Optionally, add the station name as text next to the marker
            ax.scatter(lon, lat, transform=ccrs.PlateCarree(), color='red')
            ax.text(lon + 0.02, lat + 0.02, name, transform=ccrs.PlateCarree(), fontsize=9)

    # Add features with Cartopy
    ax.coastlines()  # Add coastlines
    ax.gridlines(draw_labels=True)  # Add grid lines and labels
    plt.title('Weather Station Locations and Wind Direction/Speed')
    plt.show()


def get_data(information,capa,time_serie=None, time_slot = None, api = arome):
    print('Get data:', information)

    coverages = api['field']()  #list_data_variable()
    coverage = coverages[information]['Coverage name']
    variable = coverages[information]['Variable']
    height = coverages[information]['Height cluster']
    suffix =coverages[information]['Suffix']
    now = datetime.now(timezone.utc)
    if time_serie == None:
        time_serie = find_closest_time_series(information,now,capa, api)
    file_name= None
    if not(time_serie is None):
        coverage_time = coverage + '___'+ time_serie
        start,end, coefficients = describe_coverage(coverage_time, api = api)
        if time_slot==None:
            time_slot=find_closest_time_slot(information,now,capa)
            print(f'No time slot provided, taking {time_slot}')
        file_name = 'data_' + information + str(datetime.strptime(time_serie.replace(".", ":"), "%Y-%m-%dT%H:%M:%SZ")) + '_' + time_slot.strftime('%Y-%m-%dT%H:%M:%SZ') + '.grib'
        file_name=file_name.replace(':', '-')
        if height:
            data_received = get_coverage(coverage_time, time_slot,subset='height(10)',file_name = file_name, api = api)
        else:
            data_received = get_coverage(coverage_time, time_slot,subset=None,file_name = file_name, api = api)
    if data_received:
        return file_name
    else:
        return None





def get_time_series(information,capa, api = arome):
    print('Get time series:', information)
    coverages = api['field']()  #list_data_variable()
    coverage = coverages[information]['Coverage name']
    df = pd.DataFrame(capa[coverage])
    
    # Ensure 'Time stamp' is in datetime format
    df['Time stamp'] = pd.to_datetime(df['Time stamp'])
    return df


def find_closest_time_slot(information,time,capa,api = arome):
    print('Find closest time slot:', information)
    time_slots = get_available_time(information,capa, api)
    
    # Initialize a variable to keep track of the minimum difference
    min_diff = None
    closest_slot = None
    
    # Iterate through each time slot
    for slot in time_slots:
        # Calculate the absolute difference between the current slot and the given time
        diff = time - slot
        
        # If this is the first iteration or we found a closer time slot
        if min_diff is None or (diff < min_diff and diff>timedelta(seconds=0)):
            min_diff = diff
            closest_slot = slot
        if closest_slot ==None:
            closest_slot = time_slots[0]
    # Return the closest time slot

    return closest_slot


def find_time_slots(information,time,capa,nb_slot=1,api = arome):
    times_slots = get_available_time(information,capa,api=api)
    if times_slots is not None:
        print(f'Find time slots: {information} - { len(times_slots) } slots found')
    else:
        print(f'Find time slots: {information} - None found')
        return []
    time_slots = sorted(times_slots)
    i=0
    if nb_slot ==None:
        nb_slot = len(time_slots)
    next_slots=[]
    while i<len(time_slots)-1 and len(next_slots)<nb_slot:
        if time_slots[i+1]>time:
            next_slots.append(time_slots[i])
        i +=1
    if len(next_slots)<nb_slot and time_slots[i]>time:
        next_slots.append(time_slots[i])
        
    return next_slots


def find_closest_time_series(information, time, capa, api = arome):
    print('Find closest time series:', information)
    coverages = api['field']()  #list_data_variable()
    suffix =coverages[information]['Suffix']
    df = get_time_series(information,capa,api)
    
    # Filter the DataFrame for the given suffix and times up to the specified time
    filtered_df = df[(df['Suffix'] == suffix) & (df['Time stamp'] <= time)]
    
    # Find the entry with the closest time stamp that is less than or equal to the given time
    if not filtered_df.empty:
        closest_entry = filtered_df.loc[filtered_df['Time stamp'].idxmax()]
        closest_lower_time_serie = closest_entry['Time serie']
    else:
        closest_lower_time_serie = None
    
    return closest_lower_time_serie


def get_available_time(information,capa,time_serie=None, api = arome):
    print('Get available time:', information)
    coverages = api['field']()  
    coverage = coverages[information]['Coverage name']
    variable = coverages[information]['Variable']
    height = coverages[information]['Height cluster']
    suffix =coverages[information]['Suffix']
    if time_serie == None:
        now = datetime.now(timezone.utc)
        time_serie = find_closest_time_series(information,now,capa, api = api)
    file_name= None
    if not(time_serie is None):
        coverage_time = coverage + '___'+ time_serie
        start,end, coefficients = describe_coverage(coverage_time, api = api)
        available_time = []
        if coefficients is not None:
            for coefficient in coefficients:
                available_time.append(start +timedelta(seconds=coefficient))
            return available_time
    return None






def build_unique_grib(dimension, time, nb_slot, capa, api = arome):
    print(50*'-')
    print('Unique grib:', dimension)
    print(50*'-')

    time_serie = find_closest_time_series(dimension, time, capa,api = api)
    time_slots = find_time_slots(dimension, time, capa, nb_slot=nb_slot, api = api)
    print(time_slots)
    nb_components=0
    try:
        print(f'Time: {time_slots[0]}')
        file_name = get_data(dimension, capa, time_slot=time_slots[0], api = api)
        if file_name is not None:
            grib_files = [file_name]
            unified_grib = xr.open_dataset(file_name, engine='cfgrib')
            print('Dimension:',dimension)
            print('Variable:',unified_grib.data_vars)
    ### What does step do??
            if api['name']== 'Arome':
                unified_grib = unified_grib.assign_coords({"actual time": unified_grib['time'] + unified_grib['step']})
            elif api['name']=='Arome_PI':
                unified_grib = unified_grib.assign_coords({"actual time": unified_grib['time'] })
            else:
                print('Unknwow API')
            nb_components +=1
        else:
            print(f'Problem getting data for {dimension} and time {time_slots[0]}')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, 0
    for time_slot in time_slots[1:]:
        sleep(1*speed_limit)
        print(f'Time: {time_slot}')
        try:
            file_name = get_data(dimension, capa, time_slot=time_slot, api = api)
            if file_name is not None:
                grib = xr.open_dataset(file_name, engine='cfgrib')
                if api['name']== 'Arome':
                    grib = grib.assign_coords({"actual time": grib['time'] + grib['step']})
                elif api['name']=='Arome_PI':
                    grib = grib.assign_coords({"actual time": grib['time'] })
                else:
                    print('Unknwow API')
                unified_grib = xr.concat([unified_grib, grib], dim='actual time')
                nb_components +=1
            else:
                print(f'Problem getting data for {dimension} and time {time_slot}')
        except Exception as e:
            print(f"An error occurred: {e}")

    return unified_grib, nb_components

def build_full_grib(data_to_get ,time, nb_slot,capa, api = arome):
    print(50*'-')
    print('Full grib')
    print(50*'-')
          
    gribs = []
    data_collected = {}
    for dimension in data_to_get:
        print(50*'_')
        print(f'Dimension: {dimension}')
        print(time)
        print(50*'-')

        new_grib,count=build_unique_grib(dimension,time,nb_slot,capa, api)
        data_collected[dimension]= { 'received': count,  'expected': nb_slot , 'ingested':False , 'aligned':False}
        if new_grib !=None:
            gribs.append(new_grib)
        
    full_grib = gribs[0]
    data_collected[data_to_get[0]]['ingested']=True
    for i in range(1,len(gribs)):
        sleep(2*speed_limit)
        try:
            print(f'Merging grib {i}')
            full_grib = xr.merge([full_grib, gribs[i]])
            data_collected[data_to_get[i]]['ingested']=True
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Grib:",gribs[i])
    list_variable = api['field']()  #list_data_variable()
    # Rename grib variable
    for dimension in data_to_get:
        try:
            variable_name = list_variable[dimension]['Variable']
            full_grib = full_grib.rename({variable_name: dimension})
            data_collected[dimension]['aligned']=True
        except Exception as e:
            print(f"An error occurred while renaming variable: {e}")
            print(f'Dimension: {dimension}')
            print(f'Variable name: {list_variable[dimension]["Variable"]}')
    return full_grib, data_collected

def enrich_grib(full_grib, api = arome):
    try:
        full_grib['Wind Speed'] = np.sqrt(full_grib['X wind']**2 + full_grib['Y wind']**2)*3.6/1.852
        full_grib['Wind Direction'] = np.arctan2(-full_grib['Y wind'], -full_grib['X wind']) * (180 / np.pi)
        full_grib['Wind Direction'] = (full_grib['Wind Direction'] + 360) % 360  # Normalize direction to 0-360 degrees
        full_grib['Rotation']=full_grib['Wind Direction'].diff(dim='actual time')
        full_grib['Evol']=full_grib['Wind Speed'].diff(dim='actual time')
        full_grib['Gust Speed'] = np.sqrt(full_grib['X gust']**2 + full_grib['Y gust']**2)*3.6/1.852
        full_grib['Gust Direction'] = np.arctan2(-full_grib['Y gust'], -full_grib['X gust']) * (180 / np.pi)
        full_grib['Gust Direction'] = (full_grib['Gust Direction'] + 360) % 360  # Normalize direction to 0-360 degrees
        angle_diff=(full_grib['Gust Direction']-full_grib['Wind Direction'] + 180)%360-180
        angle_diff = xr.where(angle_diff>180,angle_diff-360,angle_diff)
        angle_diff = xr.where(angle_diff<-180,angle_diff+360,angle_diff)
        
        full_grib['Adonne'] = angle_diff
        full_grib['Rise'] = full_grib['Gust Speed']-full_grib['Wind Speed']

        print('Wind and gust speed and direction information added')
    except Exception as e:
        print(f"An error occurred while adding variable: {e}")

    if api == arome:
        full_grib = full_grib.drop_vars(['step','time','valid_time'])
    elif api == arome_PI:
        full_grib = full_grib.drop_vars(['time'])
    
    return full_grib


        

def show_rotation(dimension ,specific_time, full_grib):
    full_grib['Rotation']=full_grib[dimension].diff(dim='actual time')
    display_grib('Rotation',specific_time, full_grib,'RdYlGn')
    


if False:
    obs = get_observation()

    plot_stations(None)



selected_API = arome


if True:
    capa = get_capabilities(selected_API)
#    data_range = ['Adiabatic TWP 27315', 'Adiabatic TWP 27415', 'Adiabatic TWP 27465', 'Brightness', 'Convective energy', 'Grele', 'Total water precipitation', 'Wind speed', 'Wind speed max', 'Wind speed gust', 'Graupel', 'Hail', 'Relative humidity', 'Mocon', 'Low cloud', 'Total snow', 'Total precipitation', 'Solid precipitation', 'Severe precipitation type', 'Precipitation type 15', 'Pressure', 'Reflectivity', 'Total precipitation rate', 'Dew point', 'Temperature ground', 'Temperature', 'X wind', 'X gust', 'Visibility mini precipitation', 'Visibility mini', 'Y wind', 'Y gust', 'Wetb temperature']
    data_range = ['X wind','Y wind','X gust','Y gust']
    full_grib, data_collected =build_full_grib(data_range,datetime.now(timezone.utc),4,capa, api = selected_API)
    full_grib = enrich_grib(full_grib, selected_API)
    print(data_collected)

    if selected_API == arome_PI:
        full_grib.to_netcdf('full_grib2.nc')
        print('Grib file saved')
    elif selected_API == arome:
        full_grib.to_netcdf('full_grib.nc')
        print('Grib file saved')

else:
    if selected_API == arome_PI:
        full_grib = xr.open_dataset('full_grib2.nc')    
    elif selected_API == arome: 
        full_grib = xr.open_dataset('full_grib.nc')    


specific_time =  datetime.now(timezone.utc).replace(tzinfo=None) 

one_hour_time =  (datetime.now(timezone.utc)+timedelta(hours = 1)).replace(tzinfo=None) 
print(specific_time)

specific_lat = 47.557967  # Example latitude
specific_lon = -3.009533  # Example longitude

# Main drawing
display_grib('Wind Speed',specific_time, full_grib, display = True, save_fig= True, file_name = 'Wind speed.jpg')
display_grib('Wind Speed',specific_time, full_grib, 'jet', display = False, save_fig= True, file_name = 'Wind speed scaled.jpg',range_color = (0,40))
display_grib('Wind Speed',one_hour_time, full_grib, display = False, save_fig= True, file_name = 'Wind speed 1h.jpg')
display_grib('Wind Direction',specific_time, full_grib, 'RdYlGn', display = False, save_fig= True, file_name = 'Wind Direction.jpg')
display_grib('Wind Direction',one_hour_time, full_grib, 'RdYlGn', display = False, save_fig= True, file_name = 'Wind Direction 1h.jpg')
display_grib('Rotation',one_hour_time, full_grib,'RdYlGn', display = False, save_fig= True, file_name = 'Rotation.jpg',range_color = (-20,20))
display_grib('Evol',one_hour_time, full_grib, display = False, save_fig= True, file_name = 'Evol.jpg',range_color = (-10,10))
display_grib('Adonne',specific_time, full_grib,'RdYlGn', display = False, save_fig= True, file_name = 'Adonne.jpg')
# Rond C
if False:
    c1= (47.56,-3.1)
    c2= (47.47, -2.97)
    display_grib('Wind Speed',specific_time, full_grib, display = False, save_fig= True, file_name = 'Wind speed Z.jpg', corner1=c1,corner2=c2)
    display_grib('Wind Speed',specific_time, full_grib, 'jet', display = False, save_fig= True, file_name = 'Wind speed scaled Z.jpg',range_color = (0,40), corner1=c1,corner2=c2)
    display_grib('Wind Speed',one_hour_time, full_grib, display = False, save_fig= True, file_name = 'Wind speed 1h Z.jpg', corner1=c1,corner2=c2)
    display_grib('Wind Direction',specific_time, full_grib, 'RdYlGn', display = False, save_fig= True, file_name = 'Wind Direction Z.jpg', corner1=c1,corner2=c2)
    display_grib('Wind Direction',one_hour_time, full_grib, 'RdYlGn', display = False, save_fig= True, file_name = 'Wind Direction 1h Z.jpg', corner1=c1,corner2=c2)
    display_grib('Rotation',one_hour_time, full_grib,'RdYlGn', display = False, save_fig= True, file_name = 'Rotation Z.jpg',range_color = (-20,20), corner1=c1,corner2=c2)
    display_grib('Evol',one_hour_time, full_grib, display = False, save_fig= True, file_name = 'Evol Z.jpg',range_color = (-10,10), corner1=c1,corner2=c2)
    display_grib('Adonne',specific_time, full_grib,'RdYlGn', display = False, save_fig= True, file_name = 'Adonne Z.jpg', corner1=c1,corner2=c2)


values = get_value_grib_pos('Wind Speed',47.557967,-3.009533,full_grib)
plot_values(values, display = False, save_fig= True, file_name = 'Wind speed evol.jpg')


# Get the current directory
current_directory = os.getcwd()

# Loop through each file in the current directory
for filename in os.listdir(current_directory):
    # Check if the file is a GRIB file
    if filename.endswith(".grib") or filename.endswith(".grib2") or filename.endswith(".idx"):
        # Construct the full path to the file
        file_path = os.path.join(current_directory, filename)
        # Remove the file
        os.remove(file_path)
        print(f"Removed {file_path}")
