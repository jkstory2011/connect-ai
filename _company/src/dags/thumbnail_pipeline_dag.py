"""
Thumbnail Pipeline DAG
Author: 코다리
Description:
    Airflow DAG to orchestrate thumbnail processing pipeline.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator

# default args
default_args = {
    'owner': 'coder',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        dag_id='thumbnail_pipeline',
        default_args=default_args,
        schedule_interval='@hourly',
        start_date=datetime(2026, 6, 1),
        catchup=False,
) as dag:

    # Step 1: Collect metadata
    collect_task = DockerOperator(
        task_id='collect_metadata',
        image='coder/thumbnail-worker:latest',
        api_version='auto',
        auto_remove=True,
        command='python /app/tasks/collect.py',
    )

    # Step 2: Preprocess images
    preprocess_task = DockerOperator(
        task_id='preprocess_images',
        image='coder/thumbnail-worker:latest',
        api_version='auto',
        auto_remove=True,
        command='python /app/tasks/preprocess.py',
    )

    # Step 3: Generate thumbnails
    generate_task = DockerOperator(
        task_id='generate_thumbnails',
        image='coder/thumbnail-worker:latest',
        api_version='auto',
        auto_remove=True,
        command='python /app/tasks/generate.py',
    )

    # Step 4: Quality check
    quality_task = DockerOperator(
        task_id='quality_check',
        image='coder/thumbnail-worker:latest',
        api_version='auto',
        auto_remove=True,
        command='python /app/tasks/quality.py',
    )

    # Step 5: Store results
    store_task = DockerOperator(
        task_id='store_results',
        image='coder/thumbnail-worker:latest',
        api_version='auto',
        auto_remove=True,
        command='python /app/tasks/store.py',
    )

    # Step 6: Notify/monitor
    notify_task = DockerOperator(
        task_id='notify',
        image='coder/thumbnail-worker:latest',
        api_version='auto',
        auto_remove=True,
        command='python /app/tasks/notify.py',
    )

    # Define dependencies
    (collect_task >> preprocess_task >> generate_task >>
     quality_task >> store_task >> notify_task)