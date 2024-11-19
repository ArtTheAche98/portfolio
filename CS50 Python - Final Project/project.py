import pandas as pd # type: ignore
import sys
from difflib import get_close_matches

def main():
    latin_to_georgian, english_to_georgian = load_terms()

    combined_terms = {**latin_to_georgian, **english_to_georgian} #combining for easier access

#we either use sys.argv or ask for input
    if len(sys.argv) > 1:
        term = " ".join(sys.argv[1:]).strip()
    else:
        print("Welcome to the Medical Terminology Translator!")
        term = input("Enter a medical term in Latin or English to translate to Georgian:").strip().title()

#translation is using the variable 'combined terminology' as a dictionary
    translation = translate_terms(term, combined_terms)

    if translation:
        print(f"The Georgian translation for '{term}' is: {translation}")
    else:
        print(f"No exact match found for term '{term}'")
        suggestions = get_suggestions(term, combined_terms)
        if suggestions:
            print("Do you mean:")
            for  suggestion in suggestions:
                print(f"-  {suggestion}")
        else:
            print("No suggestions avaliable.")


def load_terms():
    try:
        data = pd.read_excel("terminology.xlsx", usecols=["Latin", "English", "Georgian"])
        latin_to_georgian = dict(zip(data["Latin"], data["Georgian"]))
        english_to_georgian = dict(zip(data["English"], data["Georgian"]))
        return latin_to_georgian, english_to_georgian
    except FileNotFoundError:
        print("Error: The file 'terminology.xlsx' was not found.(It is in the 'Project' repository.)")
        return {}, {}
    except ValueError as ve:
        print(f"Error: {ve}. Check the file.")
        return {}, {}
    except Exception as e:
        print(f"An unexpected error occured: {e}")
        return {}, {}

def translate_terms(term, combined_terms):
    return combined_terms.get(term, None)


def get_suggestions(term, combined_terms):
    term = term.title() #we use .title() for matching
    cutoff = 0.4 if len(term) <= 2 else 0.6
    return get_close_matches(term, combined_terms.keys(), n=3, cutoff=cutoff)

if __name__ == "__main__":
    main()