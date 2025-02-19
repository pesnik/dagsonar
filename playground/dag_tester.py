import pendulum
from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor

default_args = {
    "owner": "mr.hasan",
    "email": ["tester@pesnik.com"],
    "email_on_failure": False,
    "email_on_retry": False,
}


@dag(
    default_args=default_args,
    schedule=None,
    start_date=pendulum.today("Asia/Dhaka").add(days=0),
    tags=["TEST"],
    on_failure_callback=lambda x: print("Failed"),
    on_success_callback=lambda x: print("Success"),
    params={
        "date_value": pendulum.today("Asia/Dhaka").add(days=0).strftime("%Y-%m-%d")
    },
    max_active_runs=1,
    catchup=False,
)
def dag_tester():
    @task
    def start():
        print("Job Started @10")

    task_start = start()

    task_sensor = FileSensor(
        task_id="file_sensor",
        filepath=FILE_PATH,
        poke_interval=60,
        timeout=600,
        sql="SELECT 1;",
    )

    @task.bash
    def cmd_task(message):
        return f"echo {message}"

    @task.bash
    def cmd_task_sh(message):
        return (
            f"/Users/r_hasan/Development/dagsonar/playground/greeting_bot.sh {message}"
        )

    message = "Hello World"
    task_cmd = cmd_task(message=message)

    task_bash_op = BashOperator(
        task_id="bash_op",
        bash_command="/Users/r_hasan/Development/dagsonar/playground/greeting_bot.sh ",
    )

    @task
    def end():
        print(END_MESSAGE)
        caller()
        print("Job Completed")

    chain(
        task_start,
        task_sensor,
        task_cmd,
        cmd_task_sh("Cluster hop, on the top"),
        task_bash_op,
        end(),
    )
    # task_start >> task_sensor >> task_cmd >> end()


END_MESSAGE = "End of DAG 1"
FILE_PATH = "/usr/local/airflow/dags/initiator"


def caller():
    print("Has been called!")


dag_tester()
