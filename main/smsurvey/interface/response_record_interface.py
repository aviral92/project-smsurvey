import argparse
import boto3
import csv
import botocore
import os
from tornado import process
from tornado.ioloop import IOLoop

from smsurvey.core.model.model import Model
from smsurvey.schedule import schedule_master
from smsurvey.interface import interfaces_master
from smsurvey import config
from smsurvey.core.services.instance_service import InstanceService

class ParticipantDetails():
    participantEnrollment = []

    @staticmethod
    def get_enrollment():
        ParticipantDetails.loaddata()

    @staticmethod
    def loaddata():
        load_data = LoadData()
        load_data.loaddata(ParticipantDetails.participantEnrollment)

class LoadData():
    def __init__(self):
        self.BUCKET_NAME = 'participants-record' # replace with your bucket name
        self.KEY = 'EnrollmentRecord.csv' # replace with your object key
        self.s3 = boto3.resource('s3')

    def downloaddata(self):
        try:
            self.s3.Bucket(self.BUCKET_NAME).download_file(self.KEY, 'EnrollmentRecord.csv')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

    def loaddata(self, dataStorage):
        self.downloaddata()
        with open(r'EnrollmentRecord.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(dataStorage)
        # Create an S3 client
        self.uploadfile()

    def uploadfile(self):
        s3 = boto3.client('s3')
        filename = 'EnrollmentRecord.csv'
        bucket_name = 'participants-record'
        # Uploads the given file using a managed uploader, which will split up large
        # files automatically and upload parts in parallel.
        s3.upload_file(filename, bucket_name, filename)

