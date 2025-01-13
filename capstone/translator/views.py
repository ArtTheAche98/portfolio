import os
import requests
from dotenv import load_dotenv
from django.shortcuts import render
from .forms import TranslateForm
from .models import Translation

load_dotenv()
API_KEY = os.getenv("MW_API_KEY")


def index(request):
    return render(request, "translator/index.html")


def fetch_image_url_from_wikimedia(term):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": term,
        "prop": "pageimages",
        "pithumbsize": 250,
        "format": "json"
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if "thumbnail" in page_data:
                    return page_data["thumbnail"]["source"]
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    return None


def fetch_medical_definition(term):
    """
    Queries the Merriam-Webster Medical Dictionary API for the term.
    """
    base_url = "https://www.dictionaryapi.com/api/v3/references/medical/json/"
    url = f"{base_url}{term}?key={API_KEY}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                definitions = data[0].get("shortdef", [])

                audio = None
                if "hwi" in data[0] and "prs" in data[0]["hwi"]:
                    # Get the first pronunciation audio
                    pronunciation = data[0]["hwi"]["prs"][0]
                    if "sound" in pronunciation and "audio" in pronunciation["sound"]:
                        audio_filename = pronunciation["sound"]["audio"]
                        first_letter = audio_filename[0]
                        audio = f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{first_letter}/{audio_filename}.mp3"

                return {"definitions": definitions, "audio": audio}
        else:
            print(f"Error: Received status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"An exception occurred: {e}")

    return {"definitions": ["No definition found."], "audio": None}


def translate_term(request):
    translation_result = None
    term_definitions = None
    term_audio = None
    image_url = None

    if request.method == "POST":
        form = TranslateForm(request.POST)
        if form.is_valid():
            term = form.cleaned_data["term"]
            target_language = form.cleaned_data["target_language"]

            translation = Translation.objects.filter(
                source_language="en",
                target_language=target_language,
                source_text__iexact=term,
            ).first()

            if translation:
                translation_result = translation.translated_text

            result = fetch_medical_definition(term)
            term_definitions = result.get("definitions", [])
            term_audio = result.get("audio")
            image_url = fetch_image_url_from_wikimedia(term)
    else:
        form = TranslateForm()

    return render(request, "translator/translate.html", {
        "form": form,
        "translation_result": translation_result,
        "term_definitions": term_definitions,
        "term_audio": term_audio,
        "image_url": image_url,
    })


from django.http import JsonResponse


def autocomplete_suggestions(request):
    """
    Returns a JSON response containing suggestions for the given term.
    """
    term = request.GET.get("term", "").lower()
    predefined_terms = ["heart", "brain", "lungs", "kidney", "liver"]

    # Filter terms starting with the input
    matching_terms = [t for t in predefined_terms if t.startswith(term)]

    return JsonResponse({"suggestions": matching_terms})

