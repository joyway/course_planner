# RRC Student Course Planner
A simple Python script to resolve conflicts and generate all possible course plans

# Requirement
- Python 3.6+

# Usage
## Grab course info from the RRC website
1. Download the project and unzip it to any location on your PC
1. Open My Progress page in RRC Student Planning website
2. Click on any of your courses that needs to be planned
3. Open your browser Developer Tools, switch to `Network` view
4. Click on "View Available Sections for XXXXX" on the webpage
5. Your Developer Tools should capture a request named "sections", click on it, then switch to `Response`
6. Copy everything in the "Response", then save it to a JSON file in the `schedules` folder, name it anything you want
7. Repeat from step 2 to 6, until all course for your next term are saved to the `schedules` folder

## Generate report
1. Run the python script `planner.py`
2. If everything goes well, a CSV file will be generated in the project folder, it contains all the valid, non-conflicting course plans
3. Open the CSV file in Excel or Numbers or any spreadsheet program, you can further filter the result
