import argparse
import boto3
import csv
import botocore
from smsurvey.core.services.task_service import TaskService
import pandas as pd


getallresponse = []

class DataManagement():
    dataStorage = []
    sendData = []
    @staticmethod
    def get_schedule():
        for participants in DataManagement.dataStorage[1]:
            for runtimes in DataManagement.dataStorage[3]:
                DataManagement.sendData = []
                DataManagement.sendData.append(DataManagement.dataStorage[0])
                DataManagement.sendData.append(participants)
                DataManagement.sendData.append(DataManagement.dataStorage[2])
                DataManagement.sendData.append(runtimes)
                DataManagement.sendData.append(DataManagement.dataStorage[4])
                DataManagement.sendData.append(DataManagement.dataStorage[5])
                DataManagement.sendData.append(DataManagement.dataStorage[6])
                DataManagement.sendData.append(DataManagement.dataStorage[7])
                DataManagement.sendData.append(DataManagement.dataStorage[8])
                DataManagement.loaddata()
        DataManagement.dataStorage = []
    @staticmethod
    def getSurveyid(survey_id):
        print(TaskService.get_tasks_by_survey_id(survey_id))

    @staticmethod
    def loaddata():
        load_data = LoadData1()
        load_data.loaddata(DataManagement.sendData)

class LoadData1():
    def __init__(self):
        self.BUCKET_NAME = 'participants-record' # replace with your bucket name
        self.KEY = 'ParticipantRecord.csv' # replace with your object key
        self.s3 = boto3.resource('s3')

    def downloaddata(self):
        try:
            self.s3.Bucket(self.BUCKET_NAME).download_file(self.KEY, 'ParticipantRecord.csv')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def concatresponse(self, participant_id,question_number,response, date_responded):
        self.downloaddata()
        dataset = pd.read_csv("ParticipantRecord.csv")
        for i in range(len(dataset)):
            if(dataset['participant_id'][i] == participant_id):
                if(date_responded in dataset['scheduledTime'][i]):
                    dataset.loc[i,question_number] = response
                    break
        dataset.to_csv("ParticipantRecord.csv")
        self.uploadfile()

    def loaddata(self, dataStorage):
        self.downloaddata()
        with open(r'ParticipantRecord.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(dataStorage)
        # Create an S3 client
        self.uploadfile()

    def uploadfile(self):
        s3 = boto3.client('s3')
        filename = 'ParticipantRecord.csv'
        bucket_name = 'participants-record'
        # Uploads the given file using a managed uploader, which will split up large
        # files automatically and upload parts in parallel.
        s3.upload_file(filename, bucket_name, filename)
        self.makepublic()

    def makepublic(self):
        bucket = self.s3.Bucket(self.BUCKET_NAME)
        object = bucket.Object(self.KEY)
        bucket.Acl().put(ACL='public-read')
        object.Acl().put(ACL='public-read')
