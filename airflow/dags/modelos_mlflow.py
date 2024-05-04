from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import mlflow
import mlflow.sklearn

default_args = {
    'owner': 'user',
    'start_date': datetime(2024, 3, 28),
    'retries': 10,
    'retry_delay': timedelta(seconds=5),
}


dag = DAG(
    'train_models_with_mlflow_A',
    default_args=default_args,
    description='Train machine learning models and track with MLflow',
    schedule_interval='@weekly',
    catchup=False
)



def fetch_data():
    hook = PostgresHook(postgres_conn_id='postgres_test_conn', schema='airflow')
    df = hook.get_pandas_df("SELECT * FROM test_table")
    # Convertir todas las columnas a numérico, manejar errores y rellenar NaNs
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.fillna(0, inplace=True)
    return df


def train_model(model, model_name):
    df = fetch_data()
    X = df.drop('cover_type', axis=1)
    y = df['cover_type']
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    with mlflow.start_run():
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        mlflow.log_metric("accuracy", score)
        mlflow.sklearn.log_model(model, "model_name", registered_model_name=model_name)

 



def train_random_forest():
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    train_model(model, "Random_Forest")

def train_gradient_boosting():
    model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    train_model(model, "Gradient_Boosting")

def train_logistic_regression():
    model = LogisticRegression()
    train_model(model, "Logistic_Regression")

with dag:
    task_fetch_data = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data
    )

    task_train_rf = PythonOperator(
        task_id='train_random_forest',
        python_callable=train_random_forest
    )

    task_train_gb = PythonOperator(
        task_id='train_gradient_boosting',
        python_callable=train_gradient_boosting
    )

    task_train_lr = PythonOperator(
        task_id='train_logistic_regression',
        python_callable=train_logistic_regression
    )


    task_fetch_data >> [task_train_rf, task_train_gb, task_train_lr]