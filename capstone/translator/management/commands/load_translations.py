import pandas as pd
from django.core.management.base import BaseCommand
from translator.models import Translation


class Command(BaseCommand):
    help = "Load translations from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="The file path to the Excel file")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        # Read the Excel file into a DataFrame
        try:
            data = pd.read_excel(file_path)
        except Exception as e:
            self.stderr.write(f"Error reading the file: {e}")
            return

        # Validate columns
        required_columns = ['English', 'Georgian', 'Latin']
        if not all(column in data.columns for column in required_columns):
            self.stderr.write(f"Excel file must contain the following columns: {', '.join(required_columns)}")
            return

        # Process each row and save translations for each language pair
        translations = []
        for _, row in data.iterrows():
            english_text = row['English']
            georgian_text = row['Georgian']
            latin_text = row['Latin']

            # Add English -> Georgian
            translations.append(
                Translation(
                    source_language="en",
                    target_language="ka",
                    source_text=english_text,
                    translated_text=georgian_text
                )
            )

            # Add English -> Russian
            translations.append(
                Translation(
                    source_language="en",
                    target_language="lat",
                    source_text=english_text,
                    translated_text=latin_text
                )
            )


            translations.append(
                Translation(
                    source_language="ka",
                    target_language="lat",
                    source_text=georgian_text,
                    translated_text=latin_text
                )
            )
            translations.append(
                Translation(
                    source_language="lat",
                    target_language="ka",
                    source_text=latin_text,
                    translated_text=georgian_text
                )
            )
            translations.append(
                Translation(
                    source_language="lat",
                    target_language="en",
                    source_text=latin_text,
                    translated_text=english_text
                )
            )

        # Save all translations to the database
        Translation.objects.bulk_create(translations)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully loaded {len(translations)} translations into the database."))
