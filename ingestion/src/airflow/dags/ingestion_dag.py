from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_run import CloudRunJobStartOperator
from airflow.utils.dates import days_ago
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'daily_ingestion',
    default_args=default_args,
    description='Run ingestion service daily at 06:00',
    schedule_interval='0 6 * * *',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    start = DummyOperator(
        task_id='start',
    )

    run_ingestion = CloudRunJobStartOperator(
        task_id='run_ingestion',
        location='europe-north1',
        project_id='team-god',
        job_id='ingestion-service',
        api_version='v1',
        body={
            'apiVersion': 'run.googleapis.com/v1',
            'kind': 'Job',
            'metadata': {
                'name': 'ingestion-job',
                'namespace': 'default',
            },
            'spec': {
                'template': {
                    'spec': {
                        'containers': [
                            {
                                'image': 'gcr.io/team-god/ingestion',
                                'args': [
                                    'python', 'ingestion.py'
                                ],
                            }
                        ],
                        'restartPolicy': 'Never',
                    }
                }
            }
        }
    )

    start >> run_ingestion
