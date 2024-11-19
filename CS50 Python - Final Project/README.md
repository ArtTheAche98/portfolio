Project Title:
# Medical Terminology Translator for Georgian Students

### Video Demo: <https://youtu.be/j0mshhIC_-c?feature=shared>

________________________________________
#### Description:

This project aims to create a medical terminology translator tailored for Georgian students studying medicine. Inspired by the lack of accessible, modern Georgian-language resources in fields like anatomy, this Python program simplifies the learning process by translating medical terms from Latin or English into Georgian.
As a former medical student myself, I faced numerous challenges due to the limited availability of up-to-date Georgian-language resources. Most materials were translations from decades ago. With this translator, I hope to ease the burden for future students and provide a resource that allows them to quickly and accurately find translations for essential medical terms.
________________________________________
Features

1.	Input Translation: Users can enter medical terms in Latin or English, and the program translates these terms into Georgian.
2.	Accurate Results: The translator relies on a curated list of medical nomenclature that I adapted and verified during over 100 hours of previous work, ensuring high accuracy.
________________________________________
Project Files

•	`project.py`: Contains the main program logic. This includes:

o	`main()`: Initializes the program and handles user interaction.

o	`translate_terms(term, combined_terms)`: Accepts a term (in Latin or English) and returns the corresponding Georgian translation.

o	`load_terms()`: Loads the medical terms and their translations from a local file.

o	`get_suggestions(term, combined_terms)`: Provides alternative suggestions if a term is not found in the database, helping users find the closest matches.

•	`test_project.py`: Contains unit tests for the primary functions in project.py, ensuring functionality and accuracy:

o	`test_translate_term()`: Tests the accuracy of translations.

o	`test_load_terms()`: Verifies that the terms are loaded correctly from the file.

o	`test_get_suggestions()`: Confirms that suggestions for misspelled terms are accurate.

•	`requirements.txt`: Lists the libraries needed to run the program. (e.g., pytest, sys for difflib)

________________________________________
Installation and Usage

1.	Clone the repository:


`git clone https://github.com/ArtTheAche98/medical-terminology-translator.git`

2.	Install the required dependencies:

`pip install -r requirements.txt`

3.	Run the program:

`python project.py`

4.	Enter a term in Latin or English when prompted, and the program will display the Georgian translation.
________________________________________
Testing
To test the program, use pytest to run the unit tests in test_project.py:

`pytest test_project.py`
________________________________________
Challenges and Future Goals

During development, I debated between a simpler structure and a more complex program with potential for expansion. Given the lack of Georgian-language medical resources, I opted for a focused approach that prioritizes accuracy and usability. In the future, I hope to extend this project by creating an online database accessible to all Georgian medical students and expanding the range of supported terms.

