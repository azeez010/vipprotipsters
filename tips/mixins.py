from django.db import models
from django.conf import settings
from typing import List, Optional
import csv, os

class BaseModelMixin(models.Model):
    date_added = models.DateField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CSV:
    @staticmethod
    def addCsv(file_name, folder, data: List):
        file_path = folder + file_name
        if not os.path.exists(file_path):
            os.system(f"mkdir {folder}")

        with open(file_path, "w", encoding="utf8") as file:
            if isinstance(data, list):
                for _data in data: 
                    csv.writer(file, lineterminator="\n").writerow(_data)
            else:
                csv.writer(file, lineterminator="\n").writerow(_data)

    @staticmethod
    def readCSV(folder, file_name: Optional[str]=None) -> List[str] or bool:
        file_path = folder + file_name
        assert file_name, "Filename: str is None"
        try:
            with open(file_path, encoding="utf8") as read_file_data:
                csv_list = list(csv.reader(read_file_data, delimiter=","))

                return csv_list

        except Exception as e:
            return False
    
    @staticmethod
    def readCSVHeader(file_name: Optional[str]=None) -> List[str] or bool:
        try:
            if not file_name:
                file_name = "storage/data.csv"

            with open(file_name, encoding="utf8") as read_file_data:
                header = list(csv.reader(read_file_data, delimiter=","))[0]

                return header

        except Exception as e:
            print(e)
            return False