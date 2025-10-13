from airflow.sdk import dag, task
from pendulum import datetime

@dag(
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
)
def my_dag():
    
    @task
    def a():
        #raise ValueError("This is a test error")
        return 1
    
    @task
    def b(x):
        return x + 1
    
    @task
    def  c():
        print("Hello")
    
    b(a()) >> c()   

my_dag()
