import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
import os

print("Load gesture_data.csv...")

if not os.path.exists('gesture_data.csv'):
    print("ERROR: gesture_data.csv tidak ditemukan!")
    exit()

df = pd.read_csv('gesture_data.csv')

print(f"Jumlah Data per Kelas:\n{df['label'].value_counts().sort_index()}")

X = df.drop('label', axis=1).values
y = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = tf.keras.models.Sequential([
    tf.keras.layers.Input(shape=(42,)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(5, activation='softmax') 
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

print("Mulai Training...")
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

model.save('gesture_model.h5')
print("Model 'gesture_model.h5' siap digunakan.")