import requests
import boto3
import json
from django.conf import settings
from datetime import datetime

class OpenFDAService:
    def __init__(self):
        self.api_key = settings.OPENFDA_API_KEY
        self.base_url = 'https://api.fda.gov/drug/label.json'

    def check_interactions(self, drug_names):
        interactions = []
        try:
            for drug in drug_names:
                query = f'?search=drug_interactions:{drug}&api_key={self.api_key}'
                response = requests.get(self.base_url + query)
                response.raise_for_status()
                data = response.json()
                
                if 'results' in data:
                    for result in data['results']:
                        if 'drug_interactions' in result:
                            interactions.append({
                                'drug': drug,
                                'severity': self._determine_severity(result),
                                'description': result['drug_interactions'][0],
                                'timestamp': datetime.now()
                            })
            return interactions
        except requests.exceptions.RequestException as e:
            print(f"OpenFDA API Error: {str(e)}")
            return []

    def _determine_severity(self, result):
        text = ' '.join(result.get('drug_interactions', []))
        if any(word in text.lower() for word in ['severe', 'danger', 'fatal']):
            return 'HIGH'
        elif any(word in text.lower() for word in ['moderate', 'caution']):
            return 'MEDIUM'
        return 'LOW'

class WhatsAppService:
    def __init__(self):
        self.api_key = settings.WHATSAPP_API_KEY
        self.base_url = 'https://graph.facebook.com/v17.0/FROM_PHONE_NUMBER_ID/messages'

    def send_interaction_alert(self, patient, interactions):
        message = self._format_interaction_message(interactions)
        try:
            response = requests.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'messaging_product': 'whatsapp',
                    'to': patient.phone_number,
                    'type': 'text',
                    'text': {'body': message}
                }
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"WhatsApp API Error: {str(e)}")
            return False

    def _format_interaction_message(self, interactions):
        message = "⚠️ MEDICATION INTERACTION ALERT ⚠️\n\n"
        for interaction in interactions:
            message += f"- {interaction['drug']}: {interaction['description']}\n"
        return message

    def send_medication_reminder(self, patient, medication):
        message = f"Reminder: Time to take {medication.name} - {medication.dosage}"
        # Implementation for WhatsApp message sending
        pass

class PollyService:
    def __init__(self):
        self.client = boto3.client(
            'polly',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name='us-east-1'
        )

    def create_voice_alert(self, patient, interactions):
        try:
            text = self._format_voice_message(interactions)
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Joanna',
                Engine='neural'
            )
            
            if 'AudioStream' in response:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'patient_{patient.id}_alert_{timestamp}.mp3'
                with open(f'media/voice_alerts/{filename}', 'wb') as file:
                    file.write(response['AudioStream'].read())
                return filename
        except Exception as e:
            print(f"AWS Polly Error: {str(e)}")
            return None

    def _format_voice_message(self, interactions):
        message = "Attention. Important medication interaction alert. "
        for interaction in interactions:
            message += f"Your medication {interaction['drug']} has the following warning: {interaction['description']}. "
        return message
