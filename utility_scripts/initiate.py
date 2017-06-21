# java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
import subprocess

print("Launching dynamodb")

subprocess.call(
    ["java", "-Djava.library.path=./DynamoDBLocal_lib", "-jar", "/dynamodb/DynamoDBLocal.jar", "-dbPath", "/dynamodb",
     "-sharedDb", "-port", "8888"])

print("Running")
