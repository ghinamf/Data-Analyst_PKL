#Connecting model to streamlit w/ app.py file

#Streamlit
import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

#Load the pkl
scaler = joblib.load('scaler.pkl')
le_status = joblib.load('le_status.pkl')
#le_lokasi = joblib.load('le_lokasi.pkl')
ohe = joblib.load('ohe.pkl')
modela = joblib.load('final_model.pkl')
feature_order = joblib.load('feature_order.pkl')

#Streamlit UI
st.title("Model Prediksi Level Keahlian")

# Input form for new data
durations_perproject = st.number_input('Kemampuan Waktu Pengerjaan Tiap Project [hour]')
total_project = st.number_input('Kemampuan Menyelesaikan Project [jumlah]')
status = st.selectbox('Status Kerja', le_status.classes_)
lama_kerja = st.number_input('Lama Kerja [year]')
divisi = st.selectbox('Divisi Impian', ohe.categories_[0])
gol = st.selectbox('Target Gol', ohe.categories_[1])

#Condition for button
if st.button('Prediksi'):
    # Preprocess the new input data
    new_data = pd.DataFrame({
        'DURATIONS_PERPROJECT': [durations_perproject],
        'TOTAL_PROJECT': [total_project],
        'STATUS': [status],
        'LAMA_KERJA': [lama_kerja],
        'DIVISI': [divisi],
        #'LOKASI': [lokasi],
        'GOL': [gol]
    })
    
    #Transforming data
    new_data['STATUSenc'] = le_status.transform(new_data['STATUS'])
    #new_data['LOKASIenc'] = le_lokasi.transform(new_data['LOKASI'])
    encoded_features_new = ohe.transform(new_data[['DIVISI', 'GOL']])
    encoded_df_new = pd.DataFrame(encoded_features_new, columns=ohe.get_feature_names_out(['DIVISI', 'GOL']))
    new_data = pd.concat([new_data, encoded_df_new], axis=1)
    new_data[['DURATIONS_PERPROJECT', 'TOTAL_PROJECT', 'LAMA_KERJA']] = scaler.transform(new_data[['DURATIONS_PERPROJECT', 'TOTAL_PROJECT', 'LAMA_KERJA']])
    
    #Unused columns
    #X_new = new_data.drop(columns=['STATUS', 'DIVISI', 'GOL'])
    #Ensure the input data follows the correct order
    X_new = new_data.reindex(columns=feature_order)

    
    #Prediction
    prediction = modela.predict(X_new)
    st.write(f'Hasil Prediksi: {prediction[0]}')

