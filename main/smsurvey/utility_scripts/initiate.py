import subprocess

subprocess.call(
    ["java", "-Djava.library.path=./DynamoDBLocal_lib", "-jar", "/dynamodb/DynamoDBLocal.jar", "-dbPath", "/dynamodb",
     "-sharedDb", "-port", "1234"])