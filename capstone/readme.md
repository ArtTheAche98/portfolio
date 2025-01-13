# Medical Term Translator
This capstone project is a **Medical Term Translator** built with Django. The purpose of this project is to allow users to input medical terms, select a target language, and receive translations along with related definitions, audio pronunciations, and images, if available.
## File Structure
The directory structure for the project follows the specified CS50 guidelines:
``` plaintext
/web50/projects/2020/x/capstone/
├── README.md
├── manage.py
├── requirements.txt
├── app/
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
```
- **app/templates/**: contains HTML templates for the project.
- **app/static/**: contains CSS files like `styles.css` for consistent design.
- **views.py**: handles user input and interaction with backend logic.
- **forms.py**: defines forms for user input (e.g., search term).
- **urls.py**: manages routing for the project.

## Features
### 1. **Medical Term Translation**
- Users can enter a medical term and select a target language.
- Backend translates the term using requests to external APIs or translation engines.

### 2. **Definitions**
- The user is provided with related definitions for the entered medical term.

### 3. **Audio Pronunciation**
- The app provides an audio pronunciation feature for the medical term in the requested language.

### 4. **Image Display**
- Any related image for the term is fetched and displayed dynamically.

### 5. **CSS Styles**
- A responsive design with dynamic zoom for image elements.
- A spinner is used to indicate loading when a request is being processed.

## How to Run the Project
### Prerequisites
- Python 3.13 or higher
- Django (Installed via `pip`)
- Other dependencies listed in `requirements.txt`

### Installation and Setup
1. Clone this repository to your local machine:
``` bash
   git clone https://github.com/me50/USERNAME.git
   cd web50/projects/2020/x/capstone/
```
1. Install dependencies:
``` bash
   pip install -r requirements.txt
```
1. Apply migrations:
``` bash
   python manage.py makemigrations
   python manage.py migrate
```
1. Run the Django development server:
``` bash
   python manage.py runserver
```
1. Open your browser and navigate to `http://127.0.0.1:8000`.

## Example Usage
1. Open the application and enter a **medical term**, such as `hypertension`.
2. Select the desired **target language** from the dropdown.
3. Click the **Translate** button.
4. View the translation, medical definitions, audio pronunciation, and a related image.

## Technologies Used
- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript
- **API Requests**: Python `requests` library for external API integration
- **Styling Framework**: Custom CSS with classes for buttons, form components, and a responsive layout
- **Version Control**: Git and GitHub for repository management

## CSS Highlights
Key CSS features implemented:
- Spacing is ensured with `form-group mb-3` classes.
- Buttons styled using `btn btn-primary` for a sleek and consistent look.
- Images are dynamically zoomable using `onmouseenter` and `onmouseleave` JavaScript events.
- Basic responsive design for better usability.

## Challenges Faced
- Ensuring proper directory structure required for submission.
- Styling the frontend to align with responsive web practices.
- Understanding and managing Git branches effectively for isolated changes.

## Project Contribution
To contribute:
1. Fork this repository.
2. Make your changes in a new branch.
3. Submit a pull request for review.

If you have any questions or suggestions, feel free to reach out!
Enjoy using the **Medical Term Translator** 😊!
