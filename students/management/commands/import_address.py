from django.core.management.base import BaseCommand
import pandas as pd
from students.models import Province, Amphoe, Tambon

class Command(BaseCommand):
    help = "Import address data from an Excel file"

    def handle(self, *args, **kwargs):
        file_path = 'database.xlsx'  # Update with the actual path to your Excel file

        # Read the Excel file
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            # Convert zipcode to string and remove .0 if present
            zipcode = str(row['zipcode']).split('.')[0]

            province, _ = Province.objects.get_or_create(name=row['province'])
            amphoe, _ = Amphoe.objects.get_or_create(name=row['amphoe'], province=province)
            Tambon.objects.get_or_create(name=row['district'], amphoe=amphoe, zipcode=zipcode)

        self.stdout.write(self.style.SUCCESS("Data successfully uploaded."))
