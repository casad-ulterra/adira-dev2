#  from ADIRA imports
import streamlit as st
import streamlit_analytics

from pathlib import Path
from enum import Enum
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pip
from PIL import Image
import openpyxl
import plotly.express as px
import lasio
import pymongo
import os
from io import IOBase
import traceback

#  LASSE imports

from load_css import local_css
# import lasio
import missingno as mno
import yagmail
#  Azure blob setup
from azure.storage.blob import BlobServiceClient

# from st_oauth import st_oauth
# # https://medium.com/streamlit/oauth-component-for-streamlit-e05f00874fbc
# st.markdown("## This (and above) is always seen")
# id = st_oauth('myoauth', 'Click to login via OAuth')
# # id = st_oauth(‘myoauth’)
# st.markdown("## This (and below) is only seen after authentication")
    
    
BACKGROUND_COLOR = 'white'
COLOR = 'black'

# https://discuss.streamlit.io/t/how-to-reduce-the-top-blank-area-height-of-streamlit-app/18057
def set_page_container_style(
        max_width: int = 1100, max_width_100_percent: bool = False,
        padding_top: int = 0.1, padding_right: int = 0.1, padding_left: int = 0.1, padding_bottom: int = 10,
        color: str = COLOR, background_color: str = BACKGROUND_COLOR,
    ):
        if max_width_100_percent:
            max_width_str = f'max-width: 100%;'
        else:
            max_width_str = f'max-width: {max_width}px;'
        st.markdown(
            f'''
            <style>
                .reportview-container .sidebar-content {{
                    padding-top: {padding_top}rem;
                }}
                .appview-container .main .block-container{{
                    padding-top: {padding_top}rem;    
                }}
                .reportview-container .main .block-container {{
                    {max_width_str}
                    padding-top: {padding_top}rem;
                    padding-right: {padding_right}rem;
                    padding-left: {padding_left}rem;
                    padding-bottom: {padding_bottom}rem;
                }}
                .reportview-container .main {{
                    color: {color};
                    background-color: {background_color};
                }}
            </style>
            ''',
            unsafe_allow_html=True,
        )
        
# version control
# appver = "Version 8.1.01-C"

# set interface and framework
image = Image.open('adira-logo-name.png') 
image2 = Image.open('Ulterra_teal_250px.png')
im_icon = Image.open('adira-logo-32px.png') 
page_title = 'ADIRA'

# https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config
st.set_page_config(layout='wide', page_title="ADIRA", page_icon=im_icon, menu_items={
        f'Get Help': 'mailto:ccasad@ulterra.com?subject=ADIRA, Help&body=Hey Chris, I need some help in Adira.',
        'Report a bug': 'mailto:ccasad@ulterra.com?subject=ADIRA, Bug&body=Hey Chris, I found a bug in Adira.',
        'About': "# This is a header. This is an *extremely* cool app!"} )

    
st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Local Imports
import home
import edr
import edrleg
import rsa
import proposal
import proposalmenu
import missingdata

#  Hide default streamlit styling
hide_st_style = """
                <style>
                footer {visibility:hidden;}
                </style>
                """

st.markdown(hide_st_style, unsafe_allow_html=True)

pip.main(['install', 'openpyxl'])

from io import StringIO

local_css("style.css")

# version control
appver = "Version 8.1.07-C"

# set interface and framework
image = Image.open('adira-logo-name.png') # adira-logo1.png')
image2 = Image.open('Ulterra_teal_250px.png')
page_icon = Image.open('adira-logo-32px.png') 
page_title = 'ADIRA'
layout = 'wide' # was centered


# yag = yagmail.SMTP()
yag = yagmail.SMTP(st.secrets['yagmailusername'], st.secrets['yagmailpassword'])

# st.secrets['blobname']
# st.secrets['blobkey']
# st.secrets['container']
connection_string = 'DefaultEndpointsProtocol=https;AccountName=' + st.secrets['blobname'] + ';AccountKey=' + st.secrets['blobkey'] + ';EndpointSuffix=core.windows.net'

blob_service = BlobServiceClient.from_connection_string(connection_string)

def blob_upload(df, df_name):
    blob_client = blob_service.get_blob_client(container=st.secrets['container'], blob=df_name)
    
    try:
        output = df.to_csv(index=False, encoding="utf-8")
        dflength = output.memory_usage(index=True).sum() # os.path.getsize(output.name)
    except Exception as e:
        print(e)
        st.error(f"error blob df-to-csv: {e}")
    
    try:
        blob_exists = blob_client.exists()
        if not blob_exists:
            blob_client.upload_blob(output, overwrite=False)
            status = 'Loaded'
        else:            
            status = 'Exists'
            # Check blob size
            # block_blob_service = BlockBlobService(account_name='accoutName', account_key='accountKey')
            bloblength = blob_client.get_blob_properties().size
            status = f'Exists {dflength}:{bloblength}'
        # , blob_type="BlockBlob")
    except Exception as e:
        print(e)
        st.error(f"error blob upload: {e}")

    return status 


def blob_upload_file(file, df_name):
    blob_client = blob_service.get_blob_client(container=st.secrets['container'], blob=df_name)
    
    output = file
    dflength = 0
    status = 'None'
    
    # try:
    #     dflength = os.path.getsize(df_name)
    # except Exception as e:
    #     print(e)
    #     st.error(f"error blob filelength: {e} //// {traceback.print_exc()} //// {traceback.format_exc()}")
        
    # if isinstance(file, pd.DataFrame):
    #     try:
    #         output = file.to_csv(index=False, encoding="utf-8")
    #         dflength = output.memory_usage(index=True).sum() # os.path.getsize(output.name)
    #     except Exception as e:
    #         print(e)
    #         st.error(f"error blob df-to-csv: {e} //// {traceback.print_exc()} //// {traceback.format_exc()}")
    
    try:            
        blob_exists = blob_client.exists()
        if not blob_exists:
            bytes_data = file.getvalue()
            blob_client.upload_blob(bytes_data, overwrite=False)
            # with open(file=file, mode="rb") as data:
            #     blob_client.upload_blob(name=df_name,data=bytes_data, overwrite=False)
            status = 'Loaded'
        else:            
            status = 'Exists'
            # Check blob size
            # block_blob_service = BlockBlobService(account_name='accoutName', account_key='accountKey')
            # bloblength = blob_client.get_blob_properties().size
            # status = f'Exists {dflength}:{bloblength}'
        # , blob_type="BlockBlob")
    except Exception as e:
        print(e)
        st.error(f"error blob upload: {e} //// {traceback.print_exc()} //// {traceback.format_exc()}")

    return status 

with streamlit_analytics.track(unsafe_password="adira8"):

    st.set_option('deprecation.showfileUploaderEncoding', False)

    @st.cache_data
    def load_rsa_data(uploaded_rsa_file):
        if uploaded_rsa_file is not None:
            #  Read .las
            try:
                bytes_data = uploaded_rsa_file.read()
                str_io = StringIO(bytes_data.decode('Windows-1252'))
                las_file = lasio.read(str_io)
                well_data = las_file.df()
                well_data['DEPTH'] = well_data.index
                
                # cmc Add formula based column data
                
                well_data = umagic(well_data)
                
                # well_data['SH'] = np.where(well_data['GR'] > 140, 100, np.where(well_data['GR'] < 40, 0, (well_data['GR'] - 40 / 100)))
                # well_data['SS'] = (100 - well_data['SH']) 
                # well_data['DTS'] = (well_data['DTS'].fillna(0))  
                # well_data['CUCS'] = (2,670,000 * ((well_data["DTS"]  - 58) ** -1.36))

                
            except UnicodeDecodeError as e:
                print(e)
                # st.error(f"error loading log.las: {e}")
                # # Read .csv
                # try:
                #     df = pd.read_csv(uploaded_edr_file)
                # except UnicodeDecodeError as e:
                #     print(e)
                
                # # Read xlsx (excel)
                # try:
                #     df = pd.read_excel(uploaded_edr_file, engine= 'openpyxl')
                # except UnicodeDecodeError as e:
                #     print(e)
            
        else:
            las_file = None
            well_data = None

        return las_file, well_data


    # @st.cache_data
    def umagic(well_data):
        
        # class Hdr(str, Enum):
        #     diff_pressure = 'Differential Pressure (psi)'
        #     hole_depth = 'Hole Depth (feet)'
        #     rop = 'Rate Of Penetration (ft_per_hr)'
        #     crop = 'Rate Of Penetration (ft_per_hr)'
        #     rpm = 'Rotary RPM (RPM)'
        #     wob = 'Weight on Bit (klbs)'
        #     dt = 'DateTime'
        #     dtn = 'DateTimeNormalized'
        #     dte = 'DateTimeElapsed'
        #     gr ='Gamma Ray'
        #     dtc = 'DTC'
        #     dts = 'DTS'
        
        mnemonic_name_map = {
            'DEPT': 'DEPTH',
            'DEPTH': 'DEPTH',
            'XDEPT': 'DEPTH',
            'Bit Size': 'BIT SIZE',
            'BitSize': 'BIT SIZE',
            'Bit Size (inches)': 'BIT SIZE',
            'BITSIZE': 'BIT SIZE',
            'MW': 'MW',
            'Mudweight': 'MW',
            'XMW': 'MW',
            'PE': 'PE',
            'PEF': 'PE',
            'PEFA': 'PE',
            'PhotoElectric': 'PE',
            'XPE': 'PE',
            'XPEF': 'PE',
            'XPEFA': 'PE',
            'CN': 'NPHI',
            'FCNL': 'NPHI',
            'NPHI': 'NPHI',
            'NPRI': 'NPHI',
            'NPOR': 'NPHI',
            'NEUT': 'NPHI',
            'Nuetron Porosity': 'NPHI',
            'NuetroNPHIosity': 'NPHI',
            'NEUTRON_SPLICE': 'NPHI',
            'XCN': 'NPHI',
            'XFCNL': 'NPHI',
            'XNPHI': 'NPHI',
            'XNPRI': 'NPHI',
            'XNPOR': 'NPHI',
            'XNuetron Porosity': 'NPHI',
            'XNuetroNPHIosity': 'NPHI',
            'DEN': 'RHOB',
            'DENS': 'RHOB',
            'DENS_ED': 'RHOB',
            'RHO': 'RHOB',
            'RHOB': 'RHOB',
            'RHOB_PROCESSING': 'RHOB',
            'ZDEN': 'RHOB',
            'XDEN': 'RHOB',
            'XDENS': 'RHOB',
            'XRHO': 'RHOB',
            'XRHOB': 'RHOB',
            'XZDEN': 'RHOB',
            'AC': 'DTC',
            'ACC': 'DTC',
            'DT': 'DTC',
            'DTC': 'DTC',
            'DTCO': 'DTC',
            'P_DT': 'DTC',
            'PSON': 'DTC',
            'SON': 'DTC',
            'SonicP': 'DTC',
            'XDT': 'DTC',
            'XDTC': 'DTC',
            'DTS': 'DTS',
            'DTSM': 'DTS',
            'S_DT': 'DTS',
            'SDTS': 'DTS',
            'SonicS': 'DTS',
            'XDTS': 'DTS',
            'XDTSM': 'DTS',
            'XS_DT': 'DTS',
            'XSDTS': 'DTS',
            'XSonicS': 'DTS',
            'SP': 'SP',
            'SP_SLICE': 'SP',
            'Spontaneous Potential': 'SP', 
            'SpontaneousPotential': 'SP',  
            'SonicPorosity': 'SPOR',   
            'Sonic Porosity': 'SPOR',             
            'SPHI': 'SPOR',      
            'GR': 'GR',
            'GR_SPLICE': 'GR',
            'CGR': 'GR',
            'GRD': 'GR',
            'Gamma': 'GR',
            'GammaRay': 'GR',
            'GAMMARAY': 'GR',
            'GRAM': 'GR',
            'XGR':'GR',
            'XCGR': 'GR',
            'XGRD': 'GR',
            'XGamma': 'GR',
            'XGammaRay': 'GR',
            'XGAMMARAY': 'GR'
        }
        
        
        if well_data is not None:
            #  Read .las
            # st.write('test 1')
            # for curve in well_data.curves:
            #     st.write(curve.mnemonic + ": " + str(curve.data))
            
            # Check for empty columns and drop them            
            nan_value = float("NaN")
            #  Replace empty with NaN
            well_data.replace("", nan_value, inplace=True)   
            # Drop Cols with NaN         
            well_data.dropna(how='all', axis=1, inplace=True)
            
            # Rename cols to common mnemonics
            well_data.rename(columns=mnemonic_name_map, inplace=True)
            
            # Check for duplicates            
            if not len(well_data.columns) == len(set(well_data.columns)):                
                # dbmsg.progress(16, 'Miracle 1: Clean Duplicates')
                # well_data.T.drop_duplicates().T
                well_data.loc[:,~well_data.columns.duplicated()]
                
            # Prefixchaf = well_data.columns.str.contains('GR | CGR | GRD | GammaRay | GAMMARAY', case=False)
            # st.write(Prefixchaf)
            
            # Clean common mnemonic prefix
            # for curve in   
            # for curve in enumerate(well_data.columns):
            #     # st.write(f"<b>Curve:</b> {curve.mnemonic}, <b>Units: </b>{curve.unit}, <b>Description:</b> {curve.descr}", unsafe_allow_html=True)
            #     st.write(f"   {curve.mnemonic} ({curve.unit}): {curve.descr}", unsafe_allow_html=True)
            #     # curve.mnemonic = curve.mnemonic.str.lstrip('x')
            #     # st.write(f"   {curve.mnemonic} ({curve.unit}): {curve.descr}", unsafe_allow_html=True)
            
            
            try:
                # Build Channels
                well_data['SC'] = (0)
                well_data['SSC'] = (0)
                well_data['SSg'] = (0)
                well_data['SCg'] = (0) 
                well_data['SH'] = (0)
                well_data['SS'] = (0)
                well_data['SI'] = (0)
                well_data['LS'] = (0)           
                well_data['DO'] = (0)
                well_data['AN'] = (0)
                well_data['SL'] = (0)
                well_data['CO'] = (0)
                well_data['DTSc'] = (0)
                well_data['CUCS'] = (0)
                
                if set(['DTS']).issubset(well_data.columns):
                    pass
                else:
                    well_data['DTS'] = (0)
                    
                if set(['SPOR2']).issubset(well_data.columns):
                    pass
                else:
                    well_data['SPOR2'] = (0)
                                
                well_data['CUCS2'] = (0)
                well_data['pMineral'] = (0)
                
            except UnicodeDecodeError as e:
                print(e)            
                st.info(e)
                
            try:
                # Got Lith
                GammaRayMin = 40
                GammaRayMax = 140
                SH_Ratio = 1.725
                SS_Ratio = 1.6
                LS_Ratio =  2.1
                DO_Ratio = 1.8
                AN_Ratio =  2.45
                SL_Ratio = 2.15
                CO_Ratio = 1.76
                RC_Mu = 0.21
                PDC_Mu = 0.84
                deltaTmatrix = 0
                
                def lithology(args):
                    GR, PE, RHOB, NPHI, DTC, DTS = args
                    
                    if GR is not None:
                        retSH = np.where(GR >= GammaRayMax, 1, np.where(GR <= GammaRayMin, 0, (GR - GammaRayMin)/(GammaRayMax - GammaRayMin)))                        
                    # elif SpontaneousPotential is not None:
                    #     SpontaneousPotentialMin = Min([SpontaneousPotential])
                    #     SpontaneousPotentialMax = Max([SpontaneousPotential])
                    #     retSH = ([SpontaneousPotential] - SpontaneousPotentialMin)/(SpontaneousPotentialMax - SpontaneousPotentialMin)  
                    
                    retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,0,0,0,0
                    retDTS = 0
                    retSPOR = 0
                    pMinerals = 1 - retSH
                    retSS,retSI,retLS,retDO,retAN,retSL,retCO = pMinerals,0,0,0,0,0,0
                    
                    # Non-shale checks done by lithology
                    # First by Coal…
                    if PE is not None:
                        if PE < 0.5:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,0,0,0,pMinerals

                    if RHOB is not None and RHOB < 1.5:
                        retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,0,0,0,pMinerals
                                
                    # … then by Salt
                    if PE > 4.4 and RHOB <= 2.05 and RHOB is not None:
                        retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,0,0,pMinerals,0

                    if RHOB is not None and DTC is not None:
                        if RHOB <= 2.05 and RHOB > 1.7 and  DTC < 75:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,0,0,pMinerals,0

                    if RHOB is not None: 
                        if RHOB < 1.9:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,0,0,pMinerals,0
                            
                    # … then by Anyhdrite
                    if RHOB > 2.87:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,0,pMinerals,0,0

                    if PE is not None and RHOB is not None:
                        if  PE > 4.5 and RHOB >= 2.85:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,0,pMinerals,0,0

                    # … then by Dolomite
                    if DTC is not None:
                        if  DTC < 47:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,pMinerals,0,0,0
                    
                    PEDO = (RHOB - 1.4 * PE + 1.54) / 1.72
                    PELS = (RHOB  - 0.67 * PE + 0.7) / 1.204    
                    # !!(not divided by 1.202 as  in code)
                    PESS = (RHOB  - 2 * PE + 1) / 2.236
                    
                    RHODO = (RHOB  + 1.8 * NPHI  - 2.91) / 2.06
                    RHOLS = (RHOB  + 1.73 * NPHI  - 2.72) / 2
                    RHOSS = (RHOB  + 1.76 * NPHI  - 2.62) / 2.023
                    
                    RHODO2 = (RHOB  + 0.01274 * DTC  - 3.42)
                    	
                    if RHOB <= 2.71:
                        RHOLS2 = (RHOB  + 0.012 * DTC  - 3.28)
                    if RHOB <= 2.65:
                        RHOSS2 = (RHOB  + 0.01218 * DTC  - 3.32)

                    if PE is not None and RHOB is not None:
                        if (PEDO >= -0.1) and (PEDO <= 0.1) and (RHOB >= 1.9):
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,pMinerals,0,0,0
                    if NPHI is not None and RHOB is not None:
                        if (RHODO >= -0.02) and (RHODO <= 0.02):
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,pMinerals,0,0,0
                    if DTC is not None and RHOB is not None:
                        if (RHODO2 >= -0.02) and (RHODO2 <= 0.02):
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,pMinerals,0,0,0
                    if RHOB > 2.71:
                        retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,0,pMinerals,0,0,0
                         
                    # … then by Limestone
                    if PE is not None and RHOB is not None:
                        if (PELS <= 0) and (RHOB >= 1.9):
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,pMinerals,0,0,0,0

                    if PE is not None and RHOB is not None:
                        if (PEDO <= 0) and (PELS >0) and (PEDO/(PEDO - PELS) > 0.5) and (RHOB >= 1.9):
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,pMinerals,0,0,0,0

                    if NPHI is not None and RHOB is not None:
                        if (RHOLS >= -0.02) and (RHOLS <= 0.02):
                            # Note: not currently in code
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,pMinerals,0,0,0,0

                    if DTC is not None and RHOB is not None and RHOB <= 2.71:
                        if RHOLS2 <= 0.01:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,pMinerals,0,0,0,0

                    if RHOB > 2.65:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,pMinerals,0,0,0,0

                    if DTC is not None and DTC < 55:
                            retSS,retSI,retLS,retDO,retAN,retSL,retCO = 0,0,pMinerals,0,0,0,0
                    
                    # Else:
                    #     Leave  (retSS = pMinerals, retLS = 0, retDO = 0, retAN = 0, retSL = 0, retCO = 0)  


                    # # 2) SonicS calculation
                    if DTS is None:
                        # ( see requirement 3)
                        retDTS = (retSH * SH_Ratio + retSS * SS_Ratio + retLS * LS_Ratio + retDO * DO_Ratio + retAN * AN_Ratio + retSL * SL_Ratio + retCO * CO_Ratio ) * DTC                         
                    elif DTS == 0:
                        # ( see requirement 3)
                        retDTS = (retSH * SH_Ratio + retSS * SS_Ratio + retLS * LS_Ratio + retDO * DO_Ratio + retAN * AN_Ratio + retSL * SL_Ratio + retCO * CO_Ratio ) * DTC 
                    else:
                        retDTS = DTS
                                               
                    # # 3) UCS calculation
                    retCUCS = (2670000 * ((retDTS-58) ** -1.36))
                    
                    # # 4) FrictionAngle calculation
                    # CIFA = np.asin((304878/DTC-1000)/(304878/DTC+1000))*180/np.pi

                    # 5) CCS calculation
                    # if  MudWeight is not None:
                    #     CCCS = CUCS + (MudWeight * Depth *.052) * (1+SIN(CIFA)/(1-SIN(CIFA))

                    # # 6) WeightOnBit correction
                    # if WeightOnBit < 200:
                    #     # means WOB is probably in klbs instead of lbs
                    #     WeightOnBit = WeightOnBit *1000

                    # 7) Torque calculation
                    # if BitTorque is not None:
                    #         Torque = BitTorque
                    # if BitTorque is None:
                    #         Torque = SlideCoeff * BitSize * WeightOnBit / 36
                    # if SlideCoeff is None:
                    #         Torque = PDC_Mu * BitSize * WeightOnBit / 36

                    # 8) Mechanical Specific Energy Calculation
                    # if [WeightOnBit] is not None and RateOfPenetration is not None and RPM is not None and BitSize is not None:
                    #     CMSE = 4 * WeightOnBit / (np.pi * BitSize * BitSize)  +  480 * RPM * Torque / (RateOfPenetration * BitSize * BitSize)

                    # 9) Drilling Efficiency Calculation
                        # [CEFF] = [CUCS] / [CMSE] * 100
                    
                    # Calculate Sonic Porosity
                    deltaTmatrix = ((retSH * 100) + (retSS *  55.5)+ (retLS * 47.5)+ (retDO * 43.5) + (retAN * 50) + (retSL * 67)) 
                    retSPOR = 5/8 * ((retDTS - deltaTmatrix) / retDTS)
                    
                    return retSH, retSS, retSI, retLS, retDO, retAN, retSL, retCO, retDTS, retSPOR, retCUCS, pMinerals
                

                # Run calc based on available data
                #  pd.Series(['A', 'B']).isin(df.columns).all()
                # clear nulls
                well_data[well_data == -999.25] = np.nan
                
                if set(['GR']).issubset(well_data.columns):                    
                    # Clean negative values
                    well_data[well_data['GR'] < 0] = np.nan
                    
                    if set(['RHOB']).issubset(well_data.columns): 
                        well_data[well_data['RHOB'] < 0] = np.nan
                    else:                        
                        well_data['RHOB'] = np.nan                      
                    if set(['NPHI']).issubset(well_data.columns):  
                        well_data[well_data['NPHI'] < 0] = np.nan
                    else:                        
                        well_data['NPHI'] = np.nan                        
                    if set(['PE']).issubset(well_data.columns):                        
                        # Clean negative values
                        well_data[well_data['PE'] < 0] = np.nan
                    else:                        
                        well_data['PE'] = np.nan
                        
                    # well_data['GR'].where(well_data['GR'] < 0, None)
                    
                    # if set(['RHOB','NPHI', 'PE']).issubset(well_data.columns):                        
                    #     # Clean negative values
                    #     well_data['RHOB'].where(well_data['RHOB'] < 0, None)
                    #     well_data['NPHI'].where(well_data['NPHI'] < 0, None)
                    #     well_data['PE'].where(well_data['PE'] < 0, None)
                    # else:                        
                    #     well_data['RHOB'] = np.nan
                    #     well_data['NPHI'] = np.nan
                    #     well_data['PE'] = np.nan

                    well_data['DTS2']= (0)
                    well_data['SPOR2']= (0)
                    well_data['CUCS2']= (0)
                    well_data['pMineral']= (0)
                    
                    well_data['SH'],well_data['SS'],well_data['SI'],well_data['LS'],well_data['DO'],well_data['AN'],well_data['SL'],well_data['CO'],well_data['DTS2'],well_data['SPOR2'],well_data['CUCS2'],well_data['pMineral'] = well_data[['GR','PE','RHOB','NPHI','DTC','DTS']].apply(lithology, axis=1, result_type='expand').transpose().values
                    # well_data['SH','SS','SI','LS','DO','AN','SL','CO','DTS2','SPOR2','CUCS2','pMineral'] = well_data[['GR','PE','RHOB','NPHI','DTC','DTS']].apply(lithology, axis=1, result_type='expand').transpose().values
                    
                    # Convert decimal to %
                    well_data['SH'] = well_data['SH'] * 100
                    well_data['SS'] = well_data['SS'] * 100
                    well_data['SI'] = well_data['SI'] * 100
                    well_data['LS'] = well_data['LS'] * 100           
                    well_data['DO'] = well_data['DO'] * 100
                    well_data['AN'] = well_data['AN'] * 100
                    well_data['SL'] = well_data['SL'] * 100
                    well_data['CO'] = well_data['CO'] * 100
                    
                    
                    if set(['DTS']).issubset(well_data.columns):                        
                        pass
                    else:                        
                        well_data['DTS'] = well_data['DTS2'] 
                    
                    #     cg = 1
                    #     # Gooch's Model
                    #     if cg == 0:
                    #         # Silica-Calcite Determination
                    #         well_data['SC'] = (((1 - well_data['NPHI']) * 2.65) + (well_data['NPHI'] * 1.2)) 
                            
                    #         # Sandstone Siltstone Clay (SSC) Calculation
                    #         well_data['SSC'] = (( well_data['RHOB'] - 1.05) / (1 -  well_data['NPHI'] ))
                    #         # SS Gradient  
                    #         well_data['SSg'] = np.where(well_data['SSC'] <= 2.1, ((well_data['SSC']  - 1.2) / 0.9), 0)
                    #         well_data['SCg'] = np.where(well_data['SSC'] > 2.1, ((well_data['SSC']  - 2.1) / 0.9), 0)     
                            
                    #         # Determined by RHOB < SC, then SSC calc, else LS calc
                    #         # well_data['SS'] = (1 - well_data['SSg'])
                    #         well_data['SH'] = np.where((well_data['RHOB'] < well_data['SC']), (1 - well_data['SCg']), np.where((well_data['GR'] >= 40), ((well_data['GR'] - 40) / 100), 0)) 
                    #         well_data['SS'] = np.where((well_data['RHOB'] < well_data['SC']), (1 - well_data['SSg']), 0) 
                    #         # well_data['SI'] = (well_data['SSg'] + (1 - well_data['SCg']))
                    #         well_data['SI'] = np.where((well_data['RHOB'] < well_data['SC']), (well_data['SSg'] + (1 - well_data['SCg'])), 0) 
                    #         # well_data['SI'] = np.where((well_data['RHOB'] > well_data['SC']), 0, ((1 - (well_data['SH'] + well_data['SS'])))) 

                    #         # Limestone Calculations                
                    #         # add LS conditions to all of these
                    #         # np.where((well_data['RHOB'] < well_data['SC']), , 0)                
                    #         # You need to combine all the SH maths into 1 mega SH math. Good luck future me. 
                    #         well_data['CO'] = np.where((well_data['RHOB'] < well_data['SC']), 0, np.where((well_data['PE'] < 0.5), 1, np.where( (well_data['RHOB'] < 1.5), 1, 0)))
                    #         well_data['SL'] = np.where((well_data['RHOB'] < well_data['SC']), 0, np.where((well_data['CO'] == 1), 0, np.where((well_data['RHOB'] < 1.9), 1, np.where((well_data['RHOB'] <= 2.05) & (well_data['RHOB'] > 1.7) & (well_data['DTC'] < 75), 1, np.where((well_data['PE'] > 4.4) & (well_data['RHOB'] <= 2.2), 1, 0))))) 
                    #         well_data['AN'] = np.where((well_data['RHOB'] < well_data['SC']), 0, np.where((well_data['CO'] == 1) | (well_data['SL'] == 1), 0, np.where((well_data['PE'] > 4.5) & (well_data['RHOB'] >= 2.85), 1, np.where((well_data['RHOB'] > 2.87), 1, 0)))) 
                    #         well_data['DO'] = np.where((well_data['RHOB'] < well_data['SC']), 0, np.where((well_data['CO'] == 1) | (well_data['SL'] == 1) | (well_data['AN'] == 1), 0, np.where((well_data['RHOB'] > 2.8), np.where((well_data['RHOB'] < 2.9), (1 - well_data['SH']), np.where(well_data['PE'] > 2.9, np.where(well_data['PE'] < 3.1, np.where(well_data['RHOB'] > 1.9, (1 - well_data['SH']), np.where(well_data['DTC'] < 47, (1 - well_data['SH']), 0)), np.where(well_data['DTC'] < 47, (1 - well_data['SH']), 0)) , np.where(well_data['DTC'] < 47, (1 - well_data['SH']), 0))), np.where(well_data['PE'] > 2.9, np.where(well_data['PE'] < 3.1, np.where(well_data['RHOB'] > 1.9, (1 - well_data['SH']), np.where(well_data['DTC'] < 47, (1 - well_data['SH']), 0)), np.where(well_data['DTC'] < 47, (1 - well_data['SH']), 0)) , np.where(well_data['DTC'] < 47, (1 - well_data['SH']), 0))))) 
                    #         well_data['LS'] = np.where((well_data['RHOB'] < well_data['SC']), 0, np.where((well_data['CO'] == 1) | (well_data['SL'] == 1) | (well_data['AN'] == 1) | (well_data['DO'] > 0), 0, (1 - well_data['SH']))) 
                    #         # well_data['LS'] = np.where((well_data['RHOB'] <= well_data['SC']), np.where((well_data['RHOB'] > well_data['SC']), 1 - well_data['SH'], 0), 0)
                            
                            
                    #         # well_data['DTSc'] = ( ((well_data['SH'] * 1.725) + (well_data['SI'] * 1.66) + (well_data['SS'] * 1.6) + (well_data['LS'] * 2.1) + (well_data['DO'] * 1.8) + (well_data['AN'] * 2.45) + (well_data['SL'] * 2.15) + (well_data['CO'] * 1.76)) * well_data['DTC'] )       

                    #         well_data['SH'] = well_data['SH'] * 100
                    #         well_data['SS'] = well_data['SS'] * 100
                    #         well_data['SI'] = well_data['SI'] * 100
                    #         well_data['LS'] = well_data['LS'] * 100           
                    #         well_data['DO'] = well_data['DO'] * 100
                    #         well_data['AN'] = well_data['AN'] * 100
                    #         well_data['SL'] = well_data['SL'] * 100
                    #         well_data['CO'] = well_data['CO'] * 100
                            
                    #     elif cg == 1:                            
                    #         well_data['SH'], well_data['SS'],well_data['SI'], well_data['LS'],well_data['DO'],well_data['AN'],well_data['SL'],well_data['CO'],well_data['DTS2'],well_data['SPOR2'],well_data['CUCS2'],well_data['pMineral'] = well_data[['GR','PE','RHOB','NPHI','DTC']].apply(lithology, axis=1, result_type='expand').transpose().values
                    #         # Convert decimal to %
                    #         well_data['SH'] = well_data['SH'] * 100
                    #         well_data['SS'] = well_data['SS'] * 100
                    #         well_data['SI'] = well_data['SI'] * 100
                    #         well_data['LS'] = well_data['LS'] * 100           
                    #         well_data['DO'] = well_data['DO'] * 100
                    #         well_data['AN'] = well_data['AN'] * 100
                    #         well_data['SL'] = well_data['SL'] * 100
                    #         well_data['CO'] = well_data['CO'] * 100
                            
                            
                    #     elif cg == 2:    
                    #         # # https://github.com/luthfigeo/Facies-Percentage
                    #         # #Function to determine lithology based on several conditions
                    #         well_data['DO'] = np.where((well_data['GR'] <=55) & (well_data['RHOB'] >= 2.71),1, 0)
                    #         well_data['LS'] = np.where((well_data['GR'] <=55) & (well_data['RHOB'] >= 2.65),1, 0)
                    #         well_data['SS'] = np.where((well_data['GR'] <=55) & (well_data['RHOB'] > 1.8),1, 0)
                    #         well_data['CO'] = np.where((well_data['GR'] <=55) & (well_data['RHOB'] < 1.8),1, 0)
                    #         well_data['SI'] = np.where((well_data['GR'] > 55) & (well_data['GR'] <=80),1, 0)
                    #         well_data['SH'] = np.where((well_data['GR'] >=80),1, 0)
                            
                            
                    #         # np.set_printoptions(threshold=sys.maxsize)
                    #         # pd.set_option('display.max_rows', None)
                    #         # pd.set_option('display.max_columns', None)
                    #         # pd.set_option('display.width', None)

                    #         # #Function to add your lasfile and embed the tops of intervals
                    #         # #source_dir = directory of your data
                    #         # #lasfile = LAS file name
                    #         # #topsfile = Tops data file name
                    #         # def InputWell(source_dir,lasfile, topsfile):
                    #         #     #Import your LAS file and convert it to a dataframe
                    #         #     l = lasio.read(f"{source_dir}/{lasfile}")
                    #         #     data = l.df()
                    #         #     data = data.replace('-999.00000',np.nan)
                    #         #     data.index.names = ['DEPT']
                    #         #     well = l.well.WELL.value    #This contain your well name
                    #         #     data['WELL'] = well         #This contain your log data

                    #         #     #Import your tops of interval
                    #         #     tops = pd.read_csv(f"{source_dir}/{topsfile}", sep='\t')
                    #         #     tops_unit = tops['ROCK UNIT'].unique()    #This contain list of interval, adjust the column name to suit yours
                                
                    #         #     #Assign interval name to each point in your log data
                    #         #     data_well = pd.DataFrame()
                    #         #     for i in range(len(tops_unit)):
                    #         #         top = tops.iloc[i]['DEPTH']
                    #         #         if i < len(tops_unit)-1:
                    #         #         bottom = tops.iloc[i+1]['DEPTH']
                    #         #         else:
                    #         #         bottom = int(round(data.tail(1).index.item()))
                    #         #         data_interval = data.iloc[top:bottom, :]
                    #         #         data_interval['INTERVAL'] = tops.iloc[i]['ROCK UNIT']
                    #         #         data_well = data_well.append(data_interval)
                    #         #     data = data_well

                    #         #     return well,data

                    #         # #data = your log data
                    #         # #gr = column number of GR log in your data
                    #         # #rhob = column number of RHOB log in your data
                    #         # def DetermineLithology (data, gr, rhob):
                    #         #     GR = data.iloc[:,gr]
                    #         #     RHOB = data.iloc[:,rhob]

                    #         #     #each condition refer to its lithology in following order, adjust to your specifications
                    #         #     conditions = [
                    #         #         (GR <=55) & (RHOB >= 2.71),
                    #         #         (GR <=55) & (RHOB >= 2.65),
                    #         #         (GR <=55) & (RHOB > 1.8),
                    #         #         (GR <=55) & (RHOB < 1.8),
                    #         #         (GR <=80),
                    #         #         (GR >=80)]
                    #         #     lithology = ['Dolomite', 'Limestone', 'Sandstone', 'Coal', 'Siltstone', 'Shale']
                    #         #     data['LITHOLOGY'] = np.select(conditions, lithology, default='Undefined')
                    #         #     return data

                    #         # #Function to calculate facies percentage for multiwell
                    #         # #data = your log data which already contain well name, interval name, and lithology each as a column
                    #         # def CalculatePercentage(data):
                    #         #     data_well = pd.DataFrame()
                    #         #     data_interval = pd.DataFrame()
                    #         #     F_well = pd.DataFrame()
                    #         #     Facies = pd.DataFrame()

                    #         #     for i in range(len(well)):
                    #         #         data_well=data.where(data['WELL']==well[i]).dropna()
                    #         #         interval = data_well['INTERVAL'].unique()
                    #         #         for j in range (len(interval)):
                    #         #         data_interval=data_well.where(data_well['INTERVAL']==interval[j]).dropna()
                    #         #         F_percent = data_interval['LITHOLOGY'].value_counts(normalize=True) * 100
                    #         #         F_percent = F_percent.sort_index()
                    #         #         F_percent['INTERVAL'] = interval[j]
                    #         #         F_percent= pd.DataFrame(F_percent).transpose()
                    #         #         F_well = F_well.append(F_percent)
                    #         #         F_well['WELL'] = well[i]
                    #         #         F_well = F_well.set_index('WELL')
                    #         #         Facies = Facies.append(F_well)
                    #         #         F_well = pd.DataFrame()
                                
                    #         #     Facies = Facies.reset_index()
                    #         #     Facies = Facies.fillna(0)
                    #         #     return Facies

                    #         # #Function to calculate facies percentage for single well
                    #         # #well = your well name
                    #         # #data = your log data which already contain well name, interval name, and lithology each as a column
                    #         # def CalculatePercentageSingleWell(well, data):
                    #         #     data_well = pd.DataFrame()
                    #         #     data_interval = pd.DataFrame()
                    #         #     F_well = pd.DataFrame()
                    #         #     Facies = pd.DataFrame()
                    #         #     tops_unit = data['INTERVAL'].unique()

                    #         #     for i in range (len(tops_unit)):
                    #         #         data_interval=data.where(data['INTERVAL']==tops_unit[i]).dropna()
                    #         #         F_percent = data_interval['LITHOLOGY'].value_counts(normalize=True) * 100
                    #         #         F_percent = F_percent.sort_index()
                    #         #         F_percent['INTERVAL'] = tops_unit[i]
                    #         #         F_percent= pd.DataFrame(F_percent).transpose()
                    #         #         F_well = F_well.append(F_percent)
                    #         #     F_well['WELL'] = well
                    #         #     Facies = Facies.append(F_well)
                    #         #     F_well = pd.DataFrame()
                                
                    #         #     Facies = Facies.reset_index()
                    #         #     Facies = Facies.fillna(0)
                    #         #     return Facies

                    #         # #Function to display a horizontal barchart of your calculated facies percentage
                    #         # def PlotBarChart(well):
                    #         #     facies_well = Facies#.where(Facies['WELL']==well)
                    #         #     interval = facies_well['INTERVAL'].unique()
                            
                    #         #     facies_well.plot.barh(stacked=True)
                    #         #     plt.yticks(range(len(interval)), interval)
                    #         #     plt.gca().invert_yaxis()
                    #         #     plt.ylabel("Formation")
                    #         #     plt.xlabel("Facies Percentage")
                    #         #     plt.title(well)
                    #         #     plt.legend(bbox_to_anchor=(1.1, 1.05))
                                
                    #         #     well, data = InputWell(source_dir,lasfile,topsfile)
                    #         #     data = DetermineLithology(data,1,7)
                    #         #     Facies = CalculatePercentageSingleWell(well, data)
                    #         #     Facies.to_csv(outfile)
                    #         #     PlotBarChart('Walakpa-1')

                    #     else:
                                                        
                    #         well_data['SH'] = np.where((well_data['GR'] > 40), ((well_data['GR'] - 40) / 100), 0) * 100
                    #         well_data['SS'] = (1 - well_data['SH']) * 100
                    #         well_data['SI'] = 0 * 100
                    #         well_data['LS'] = np.where((well_data['DTC'] < 55), (1 - well_data['SH']), 
                    #                                     np.where((well_data['RHOB'] > 2.65), (1 - well_data['SH']), 
                    #                                     np.where((well_data['RHOB'] > 2.65), (1 - well_data['SH']), 0))) * 100
                                                        
                    #                             # ([RHOLS2] <=0, 1 - [C%SH]), 
                    #                             # (([RHOLS2] >= -.04) && ([RHOLS2] <= 0.04), 1 - [C%SH]), 
                    #                             # ([PEDO] <= 0) && ([PELS] >0) && ([PEDO] / ([PEDO] - [PELS]) > .5) && ([BulkDensity] >= 1.9)
                    #                             # ([PELS] <= 0) && ([BulkDensity] >= 1.9)
                                                
                    #         well_data['DO'] = np.where((well_data['RHOB'] > 2.71), (1 - well_data['SH']), 
                    #                                     np.where((well_data['DTC'] < 47), (1 - well_data['SH']), 0)) * 100
                                                                        
                    #                             # ([RHODO2] >= -.02) && ([RHODO2] <= 0.02)
                    #                             # ([RHODO] >= -.01) && ([RHODO] <= .01)
                    #                             # ([PEDO] >= -.1) && ([PEDO] <= .1) && ([BulkDensity] >= 1.9)
                                                
                                                
                    #         well_data['AN'] = np.where(((well_data['PE'] > 4.5) & (well_data['RHOB'] > 2.71)), 1, 
                    #                                     np.where((well_data['RHOB'] > 2.87), 1, 0)) * 100
                                                                                            
                    #         well_data['SL'] = np.where((well_data['RHOB'] < 1.9), 1, 
                    #                                     np.where(((well_data['RHOB'] > 1.7) & (well_data['RHOB'] <= 2.05) & (well_data['DTC'] < 75)), 1, 
                    #                                     np.where(((well_data['PE'] > 4.4) & (well_data['RHOB'] <= 2.05)), 1, 0))) * 100
                                                
                    #         well_data['CO'] = np.where((well_data['RHOB'] < 1.5), 1, 
                    #                                     np.where((well_data['PE'] >= -0.1) & (well_data['PE'] <= 0.1) & (well_data['RHOB'] >= 1.9), 0.0002, 
                    #                                     np.where((well_data['PE'] < 0.5), 1, 0))) * 100          
                            
                    # else:
                    #     # Simple SH/SS Calc
                    #     # well_data['SH'] = np.where(well_data['GR'] > 140, 100, np.where(well_data['GR'] < 40, 0, ((well_data['GR'] - 40) / 100)))
                    #     well_data['SH'] = np.where(well_data['GR'] > 140, 100, np.where(well_data['GR'] < 40, 0, ((well_data['GR'] - 40))))
                    #     well_data['SS'] = (100 - well_data['SH']) 
                        
                    #     well_data['SC'] = (0)
                    #     well_data['SSC'] = (0)
                    #     well_data['LS'] = (0)
                    #     well_data['SI'] = (0)
                    #     well_data['SSg'] = (0)
                    #     well_data['SCg'] = (0)            
                    #     well_data['DO'] = (0)
                    #     well_data['AN'] = (0)
                    #     well_data['SL'] = (0)
                    #     well_data['CO'] = (0)
                    #     well_data['DTSc'] = (0)         
                        
                    #     # well_data['DTSc'] = ( ((well_data['SH'] * 1.725) + (well_data['SS'] * 1.6)) * well_data['DTC'] )              
                
            except UnicodeDecodeError as e:
                print(e)       
                st.info(e)
                
            try:
                # Calc DTS and mend to any existing 
                well_data['DTSc'] = ((((well_data['SH'] * 1.725) + (well_data['SI'] * 1.66) + (well_data['SS'] * 1.6) + (well_data['LS'] * 2.1) + (well_data['DO'] * 1.8) + (well_data['AN'] * 2.45) + (well_data['SL'] * 2.15) + (well_data['CO'] * 1.76)) / 100) * well_data['DTC'] )                     
                well_data['DTS3'] = np.where( (well_data['DTS'] > 0 ), well_data['DTS'], well_data['DTSc'] )
                # well_data['DTS3'] = np.where( (~np.isnan(well_data['DTS'])), well_data['DTS'], well_data['DTSc'] )                
                # gotSonicS = (retSH * SH_Ratio + retSS * SS_Ratio + retLS * LS_Ratio + retDO * DO_Ratio + retAN * AN_Ratio + retSL * SL_Ratio + retCO * CO_Ratio )  * DTC 
                
                # Ultimate Compressive Strength Calc
                # well_data['CUCS'] = (2,670,000 * pow(well_data['DTS']  - 58, -1.36))
                well_data['CUCS'] = (2670000 * ((well_data['DTS3'] - 58) ** -1.36))
                
                # Calculate Sonic Porosity
                well_data['SPOR'] = 5/8 * ((well_data['DTSc'] - 55.5) / well_data['DTSc'])
                # # FIX**** Update this formula with rock specific values for 55.5.  That is only for sandstone. Should be run in line with lithology calcs
                # Calculate Abrasion
                well_data['Abrasion0'] = well_data['CUCS'] * well_data['SPOR']
                well_data['Abrasion'] = ((0.9*(well_data['SS']/100))*well_data['CUCS'])+((0.1*(1-(well_data['SS']/100)))*well_data['CUCS'])
                well_data['Abrasion2'] = well_data['CUCS'] * well_data['SPOR2']
                well_data['Total Abrasion'] = well_data['Abrasion'].cumsum()
                
                # Calculate Impact
                well_data['Impact'] = np.where(well_data['CUCS'].diff(periods=1) > 0, well_data['CUCS'].diff(periods=1), 0)
                # well_data['Total Impact'] = well_data['Impact'].cumsum()
                impact_thres = 1000
                well_data['Total Impact'] = well_data['Impact'].where(well_data['Impact'] >= impact_thres, 0).cumsum()
                
            except UnicodeDecodeError as e:
                print(e)       
                st.info(e)
                
            try:            
                if set(['MW','CIFA']).issubset(well_data.columns):
                    # Present Columns:
                    # [MudWeight]
                    # [CIFA]
                    well_data['CCCS'] = ( well_data['CUCS'] + (well_data['MW'] * well_data['DEPT'] * 0.052) * (1 + np.sin( well_data['CIFA'] * (np.pi / 180) )) / (1 - np.sin (well_data['CIFA'] * (np.pi / 180) )) )
            
            except UnicodeDecodeError as e:
                print(e)       
                st.info(e)
            
            return well_data

    @st.cache_data
    def load_edr_data(uploaded_edr_file):
        if uploaded_edr_file is not None:
            df_edr = pd.DataFrame
            # Read .csv
            try:
                df_edr = pd.read_csv(uploaded_edr_file)
            except UnicodeDecodeError as e:
                print(e)
                # st.error(f"error loading log.las: {e}")
            
            # Read xlsx (excel)
            try:
                df_edr = pd.read_excel(uploaded_edr_file, engine= 'openpyxl')
            except UnicodeDecodeError as e:
                print(e)
                # st.error(f"error loading log.las: {e}")
                

    #TODO
    def missing_data():
        st.title('Missing Data')
        missing_data = well_data.copy()
        missing = px.area(well_data, x='DEPTH', y='DT')
        st.plotly_chart(missing)

    # Sidebar Options & File Uplaod
    # las_file=None
    # st.sidebar.write('# ULTERRA')
    # st.sidebar.write('To begin using the app, load your LAS file using the file upload option below.')

    # uploadedrsafile = st.sidebar.file_uploader(' ', type=['.las', 'csv', 'xlsx'])
    # las_file, well_data = load_rsa_data(uploadedrsafile)

    # # uploadededrfile = st.sidebar.file_uploader(' ', type=['csv', 'xlsx'], accept_multiple_files=True)
    # uploadededrfile = st.sidebar.file_uploader(' ', type=['csv', 'xlsx'])
    # edr_file = load_rsa_data(uploadededrfile)

    # if las_file:
    #     st.sidebar.success('File Uploaded Successfully')
    #     st.sidebar.write(f'<b>Well Name</b>: {las_file.well.WELL.value}',unsafe_allow_html=True)


    # # Sidebar Navigation
    # st.sidebar.title('Navigation')

    # options = st.sidebar.radio('Select a page:', 
    #     ['Home', 'EDR', 'EDR-Legacy', 'RSA'])

    # if options == 'Home':
    #     home.home()
    # elif options == 'EDR':
    #     edr.umagic(edr_file)
    # elif options == 'EDR-Legacy':
    #     edrleg.edrleg()
    # elif options == 'RSA':    
    #     rsa.header(las_file)
    #     rsa.raw_data(las_file, well_data)
    #     rsa.plot(las_file, well_data)
    #     missingdata.missing(las_file, well_data)
        
    las_file=None
    df_edr=None

    # Sidebar content display
    st.sidebar.image(image)
    # st.sidebar.caption('Provided by ULTERRA, ' + appver) # Version 7.1.02-C')
    st.sidebar.subheader('To begin, select a category below.')

    # st.sidebar.write('# ULTERRA')
    # st.sidebar.write('To begin using the app, load your LAS file using the file upload option below.')
    # Sidebar Navigation
    # st.sidebar.title('Navigation')

    # options = st.sidebar.radio('Select a page:',['Home', 'EDR (under construction)', 'EDR (Legacy)', 'RSA'])
    options = st.sidebar.radio('Select a page:',['Home', 'EDR', 'RSA', 'Proposals','Bit Menu'])

    if options == 'Home':
        home.home()
    elif options == 'EDR (under construction)':
        # uploadededrfile = st.sidebar.file_uploader(' ', type=['csv', 'xlsx'], accept_multiple_files=True)
        uploadededrfile = st.sidebar.file_uploader('Upload CSV or Excel File here', type=['csv', 'xlsx'])
        df_edr = load_edr_data(uploadededrfile)
        if df_edr:
            st.sidebar.success('File Uploaded Successfully')
            # st.sidebar.write(f'<b>Well Name</b>: {df_edr.well.WELL.value}',unsafe_allow_html=True)
        else:
            st.sidebar.write('Or use this example data set.')
            stsbcol1, stsbcol2, stsbcol3 = st.sidebar.columns((1,3,1))
            if st.sidebar.button('View Demo Data'):
                # uploadededrfile = pd.read_csv("data/WellDemo 24-23.csv")
                df_edr = pd.read_csv("data/WellDemo 24-23.csv")
                st.sidebar.write(f'<b>File Name</b>: {df_edr.name}',unsafe_allow_html=True)
        edr.umagic(df_edr)
    elif options == 'EDR':
        edrleg.edrleg()
    elif options == 'RSA':        
        dbmsg = st.sidebar.empty()
        uploadedrsafile = st.sidebar.file_uploader(' ', type=['.las', 'csv',])
        try:
            las_file, well_data = load_rsa_data(uploadedrsafile)
        except UnicodeDecodeError as e:
            # print(e)
            st.info(f"error load_rsa_data: {e}")
        if las_file:            
            with st.spinner('Loading data...'):
                    # dbstatus = blob_upload(well_data, uploadedrsafile.name)
                    dbstatus = blob_upload_file(uploadedrsafile, uploadedrsafile.name)
                    dbmsg.info(dbstatus)
                
            # st.sidebar.write(f"{st.secrets('container')} Uploaded.")
            st.sidebar.success('File Uploaded Successfully')
            st.sidebar.write(f'<b>Well Name</b>: {las_file.well.WELL.value}',unsafe_allow_html=True)
        else:
            st.sidebar.write('Or use this example data set.')
            stsbcol1, stsbcol2, stsbcol3 = st.sidebar.columns((1,3,1))
            if stsbcol2.button('View Demo Data'):                      
                las_file = lasio.read('data/rsa_demo.las')
                well_data = las_file.df()
                well_data['DEPTH'] = well_data.index
                #  add magic
                # well_data["SH"] = np.where(well_data["GR"] > 140, 100, np.where(well_data["GR"] < 40, 0, (well_data["GR"] - 40 / 100)))
                # well_data["SS"] = (100 - well_data["SH"]) 
                well_data = umagic(well_data)
                st.sidebar.write(f'<b>Well Name</b>: {las_file.well.WELL.value}',unsafe_allow_html=True)
                
        rsa.header(las_file)
        rsa.plot(las_file, well_data)
        rsa.raw_data(las_file, well_data)
        missingdata.missing(las_file, well_data)
    
    elif options == 'Proposals':
        proposal.proposalmaker()
        
    elif options == 'Bit Menu':
        proposalmenu.proposalmaker()
        
    st.sidebar.caption(appver + ' published by Chris Casad')


# def lith_calcs():
#     ESTIMATES SHALE %
#     Present Columns:     [SpontaneousPotential]
#     Absent Columns:     [GammaRay]

#     Calculate
#     Condition:true
#     Affected Column:  [C%SH]
#     Affected Column Expression:  ([SpontaneousPotential] - [SpontaneousPotentialMin])/([SpontaneousPotentialMax] - [SpontaneousPotentialMin])

#     Present Columns:
#     [GammaRay]

#     Calculate
#     Condition:[GammaRay] >= [GammaRayMax]
#     Affected Column:  [C%SH]
#     Affected Column Expression:  1


#     Calculate
#     Condition:[GammaRay] <= [GammaRayMin]
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0


#     Calculate
#     Condition:[GammaRay] < [GammaRayMax] && [GammaRay] > [GammaRayMin]
#     Affected Column:  [C%SH]
#     Affected Column Expression:  ([GammaRay] - [GammaRayMin])/([GammaRayMax] - [GammaRayMin])
    
# NeutroNPHIosity
#     Present Columns:
#     [NeutroNPHIosity]

#     Calculate
#     Condition:[NeutroNPHIosity] > 1
#     Affected Column:  [NeutroNPHIosity]
#     Affected Column Expression:  [NeutroNPHIosity] /100

# Estimated Percentages
#     Present Columns:
#     [SonicP]

#     Calculate
#     Condition:[SonicP] < 55
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     Absent Columns:
#     [SonicP]

#     Calculate
#     Condition:[BulkDensity] > 2.65
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [SonicP]
#     Absent Columns:
#     [PhotoElectric]
#     [NeutroNPHIosity]

#     Calculate
#     Condition:[RHOLS2] <=0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [SonicP]
#     Absent Columns:
#     [PhotoElectric]
#     [NeutroNPHIosity]

#     Calculate
#     Condition:([RHOLS2] >= -.04) && ([RHOLS2] <= 0.04)
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [PhotoElectric]

#     Calculate
#     Condition:([PEDO] <= 0) && ([PELS] >0) && ([PEDO] / ([PEDO] - [PELS]) > .5) && ([BulkDensity] >= 1.9)
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  (1 - [C%SH])
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [PhotoElectric]

#     Calculate
#     Condition:([PELS] <= 0) && ([BulkDensity] >= 1.9)
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]

#     Calculate
#     Condition:[BulkDensity] > 2.71 
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [SonicP]
#     Absent Columns:
#     [PhotoElectric]
#     [NeutroNPHIosity]

#     Calculate
#     Condition:([RHODO2] >= -.02) && ([RHODO2] <= 0.02)
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [NeutroNPHIosity]
#     Absent Columns:
#     [PhotoElectric]

#     Calculate
#     Condition:([RHODO] >= -.01) && ([RHODO] <= .01)
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [PhotoElectric]

#     Calculate
#     Condition:([PEDO] >= -.1) && ([PEDO] <= .1) && ([BulkDensity] >= 1.9)
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  (1 - [C%SH])
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0.0002

#     Present Columns:
#     [SonicP]

#     Calculate
#     Condition:[SonicP] < 47
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [PhotoElectric]

#     Calculate
#     Condition:([PhotoElectric] > 4.5) && ([BulkDensity] >= 2.85)
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  1
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]

#     Calculate
#     Condition:[BulkDensity] > 2.87 
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  1
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]

#     Calculate
#     Condition:[BulkDensity] < 1.9 
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  1
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [SonicP]

#     Calculate
#     Condition:([BulkDensity] <= 2.05) && ([BulkDensity] > 1.7) && ([SonicP] < 75)
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  1
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]
#     [PhotoElectric]

#     Calculate
#     Condition:([PhotoElectric] > 4.4) && ([BulkDensity] <= 2.05)
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  1
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Present Columns:
#     [BulkDensity]

#     Calculate
#     Condition:[BulkDensity] < 1.5 
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  1

#     Present Columns:
#     [PhotoElectric]

#     Calculate
#     Condition:[PhotoElectric] < 0.5 
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  1


#     Calculate
#     Condition:true
#     Affected Column:  [C%SS]
#     Affected Column Expression:  1 - [C%SH]
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0

#     Absent Columns:
#     [SpontaneousPotential]
#     [GammaRay]

#     Calculate
#     Condition:true
#     Affected Column:  [C%SH]
#     Affected Column Expression:  0
#     Affected Column:  [C%SS]
#     Affected Column Expression:  0
#     Affected Column:  [C%LS]
#     Affected Column Expression:  0
#     Affected Column:  [C%DO]
#     Affected Column Expression:  0
#     Affected Column:  [C%AN]
#     Affected Column Expression:  0
#     Affected Column:  [C%SL]
#     Affected Column Expression:  0
#     Affected Column:  [C%CO]
#     Affected Column Expression:  0
