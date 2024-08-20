import streamlit as st
import pandas as pd
import joblib
import mysql.connector
from mysql.connector import Error
import os
import config

# Load the pkl files using absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
scaler_path = os.path.join(current_dir, 'scaler.pkl')
le_status_path = os.path.join(current_dir, 'le_status.pkl')
ohe_path = os.path.join(current_dir, 'ohe.pkl')
model_path = os.path.join(current_dir, 'final_model.pkl')
feature_order_path = os.path.join(current_dir, 'feature_order.pkl')

scaler = joblib.load(scaler_path)
le_status = joblib.load(le_status_path)
ohe = joblib.load(ohe_path)
modela = joblib.load(model_path)
feature_order = joblib.load(feature_order_path)

# MySQL connection function
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE
        )
        if connection.is_connected():
            st.write("Koneksi Berhasil")
    except Error as e:
        st.write(f"Error: '{e}'")
    return connection

def insert_prediction(connection, data):
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO prediction_history 
    (DURATIONS_PERPROJECT, TOTAL_PROJECT, STATUS, LAMA_KERJA, DIVISI, GOL, Predicted_LEVEL_KEAHLIAN, Revisian_LEVEL_KEAHLIAN)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, data)
    connection.commit()

# Streamlit UI
st.title("Prediksi Keahlian")

# Input form for new data
total_project = st.number_input('Projek yang Telah Diselesaikan [Jumlah]')
durations_perproject = st.number_input('Total Waktu yang Dibutuhkan [Semua Projek (jam)]')
status = st.selectbox('Status Kerja', le_status.classes_)
lama_kerja = st.number_input('Lama Kerja [Tahun]')
divisi = st.selectbox('Target Divisi', ohe.categories_[0])
gol = st.selectbox('Target Golongan', ohe.categories_[1])
revisian = st.selectbox('Level Keahlian yang Seharusnya', ['Pelaksana Madya', 'Pelaksana Pemula', 'Pelaksana Utama', 'Perekayasa Madya', 'Perekayasa Magang', 'Perekayasa Muda', 'Perekayasa Utama', 'Pimpinan Madya', 'Pimpinan Muda', 'Pimpinan Pemula', 'Pimpinan Utama'])

#Condition for button
if st.button('Prediksi'):
    # Preprocess the new input data
    new_data = pd.DataFrame({
        'DURATIONS_PERPROJECT': [durations_perproject],
        'TOTAL_PROJECT': [total_project],
        'STATUS': [status],
        'LAMA_KERJA': [lama_kerja],
        'DIVISI': [divisi],
        'GOL': [gol]
    })
    
    data_simpan = new_data.copy()
    
    # Transforming data
    new_data['STATUSenc'] = le_status.transform(new_data['STATUS'])
    encoded_features_new = ohe.transform(new_data[['DIVISI', 'GOL']])
    encoded_df_new = pd.DataFrame(encoded_features_new, columns=ohe.get_feature_names_out(['DIVISI', 'GOL']))
    new_data = pd.concat([new_data, encoded_df_new], axis=1)
    new_data[['DURATIONS_PERPROJECT', 'TOTAL_PROJECT', 'LAMA_KERJA']] = scaler.transform(new_data[['DURATIONS_PERPROJECT', 'TOTAL_PROJECT', 'LAMA_KERJA']])
    
    # Ensure the input data follows the correct order
    X_new = new_data.reindex(columns=feature_order)
    
    # Prediction
    prediction = modela.predict(X_new)
    st.write(f'Hasil Prediksi: {prediction[0]}')
    
    # Add the revisian column
    data_simpan['Predicted_LEVEL_KEAHLIAN'] = prediction[0]
    data_simpan['Revisian_LEVEL_KEAHLIAN'] = revisian
    
    # Save input and prediction to MySQL
    connection = create_connection()
    
    if connection is not None:
        # Data to be inserted
        data_tuple = tuple(data_simpan.values.flatten())
        insert_prediction(connection, data_tuple)
        st.write("Data Berhasil Disimpan")
        
        # Close connection
        connection.close()
    else:
        st.write("Gagal Simpan")
