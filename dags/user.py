from airflow.sdk import asset

@asset(
    schedule="@daily",
    uri="https://randomuser.me/api/",
    tags=['api', 'user'],
    description="Fetches a random user from the API",
)
def user() -> None:
    print("Fetching user data")

@asset(
    schedule=user,
    tags=['api', 'user'],
    description="Returns user location",
)
def user_location() -> None:
    print("does nothing")
    