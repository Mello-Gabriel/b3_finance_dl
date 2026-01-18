import boto3

cliente = boto3.client("glue")

response = cliente.start_job_run(JobName = "tech_challenge_job")
