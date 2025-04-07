# Mini-Proyecto: 
# Predecir resultados usando carreras pasadas

# Objetivo: Predecir la posicion final (top 3, top 10) usando datos de carreras anteriores

import os
import fastf1
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix, classification_report

# Enable FastF1 caching
cache_folder = 'cache_folder'
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

fastf1.Cache.enable_cache(cache_folder)

## PASO 1: Obtener datos de varias carreras

def get_race_data(year, round_name):
    try:
        session = fastf1.get_session(year, round_name, 'R')
        session.load()
        results = session.results
        results['Race'] = round_name
        results['Year'] = year
        return results
    except Exception as e:
        print(f"Error en {year} - {round_name}: {e}")
        return pd.DataFrame()
    
# Por ejemplo: recopilamos 5 carreras del 2023
carreras = ['Bahrain', 'Saudi Arabia', 'Australia', 'Azerbaijan', 'Miami']
df_all = pd.concat([get_race_data(2023, carrera) for carrera in carreras], ignore_index=True)

print(df_all[['DriverNumber', 'Abbreviation', 'Position', 'GridPosition', 'TeamName', 'Race']].head())

## PASO 2: Crear columnas para el modelo

df = df_all.copy()
df = df.dropna(subset=['Position']) # eliminamos DNFs

# Convertir a int
df['Position'] = df['Position'].astype(int)
df['GridPosition'] = df['GridPosition'].astype(int)

# Codificar equipos y pilotos
df['TeamCode'] = LabelEncoder().fit_transform(df['TeamName'])
df['DriverCode'] = LabelEncoder().fit_transform(df['Abbreviation'])

# Variable objetivo: top 3
df['Top3'] = df['Position'].apply(lambda x: 1 if x <= 3 else 0)

## PASO 3: Entrenar modelo simple

features = ['GridPosition', 'TeamCode', 'DriverCode']
X = df[features]
y = df['Top3']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

X_test = X_test.copy() # por si no lo era
X_test['Actual'] = y_test.values
X_test['Predicted'] = y_pred

# Combinamos con los datos originales para ver los nombres
X_full = df[features + ['Abbreviation', 'Position', 'Race']].copy()
X_merged = X_test.merge(X_full, left_index=True, right_index=True)

# Filtrar solo predicciones de Top 3
top3_preds = X_merged[X_merged['Predicted'] == 1]
print(top3_preds[['Abbreviation', 'Position', 'Actual', 'Predicted', 'Race']])

## Matriz de confusion

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(5,4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['No Top 3', 'Top 3'],
            yticklabels=['No Top 3', 'Top 3'])
plt.xlabel('Prediccion')
plt.ylabel('Real')
plt.title('Matriz de Confusion')
plt.show()

#Armar DataFrame con resultados
results_df = pd.DataFrame({
    'Real': y_test,
    'Prediccion':y_pred
})

results_df['Resultado'] = results_df.apply(
    lambda row: 'Acierto' if row['Real'] == row['Prediccion'] else 'Error', axis=1
)

# Contamos cada tipo
plt.figure(figsize=(6,4))
sns.countplot(data=results_df, x='Resultado', palette='Set2')
plt.title('Cantidad de aciertos vs errores')
plt.show()

## Predicciones correctas por carrera
X_test = X_test.copy()
X_test['Actual'] = y_test.values
X_test['Predicted'] = y_pred
X_test['Correcto'] = X_test['Actual'] == X_test['Predicted']

# Merge con info de la carrera
X_merged = X_test.merge(df[['Race']], left_index=True, right_index=True)

plt.figure(figsize=(10,5))
sns.countplot(data=X_merged, x='Race', hue='Correcto', palette='coolwarm')
plt.title('Predicciones correctas por carrera')
plt.xticks(rotation=45)
plt.show()