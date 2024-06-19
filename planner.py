from datetime import datetime
import itertools
import json
import os
import csv


def format_schedule(course_json: dict):
    # Format raw JSON data to simple dictionary with only essential info
    title = course_json['Course']['Title']
    code =  f'{course_json["Course"]["SubjectCode"]}-{course_json["Course"]["Number"]}'
    sections = []
    for section in course_json['TermsAndSections'][0]['Sections']:
        if section['InstructorDetails']:
            instructor = section['InstructorDetails'][0]['FacultyName']
            method = section['InstructorDetails'][0]['InstructorMethod']
        else:
            instructor = ''
            method = ''
        section_id = section['Section']['SectionNameDisplay']
        campus = section['Section']['LocationCode']
        meetings = []
        for meeting in section['Section']['FormattedMeetingTimes']:
            meeting_details = {}
            meeting_details['course'] = code
            meeting_details['dayofweek'] = meeting['Days'][0] # from 1-5, means Monday to Friday
            meeting_details['start_time'] =  datetime.strptime(meeting['StartTime'], '%H:%M:%S').time()
            meeting_details['end_time'] = datetime.strptime(meeting['EndTime'], '%H:%M:%S').time()
            meeting_details['method'] = meeting['InstructionalMethodCode']
            meeting_details['room'] = meeting['RoomDisplay']
            meeting_details['instructor'] = instructor
            meeting_details['method'] = method
            meetings.append(meeting_details)
        sections.append(
            {
                'title': title,
                'code': code,
                'instructor': instructor,
                'method': method,
                'section_id': section_id,
                'campus': campus,
                'meetings': meetings
                }
            )

    return {
        'title': title,
        'code': code,
        'sections': sections
        }

def is_overlapping(start_time_1, end_time_1, start_time_2, end_time_2):
    result = False
    if start_time_2 <= start_time_1 < end_time_2:
        result = True
    if start_time_2 < end_time_1 <= end_time_2:
        result = True
    if start_time_1 <= start_time_2 < end_time_1:
        result = True
    if start_time_1 < start_time_1 <= end_time_1:
        result = True
    return result

def is_conflicting(plan):
    # Check if any course sections are conflicting
    plan_schedule = {
        1: [], # Monday
        2: [], # Tuesday
        3: [], # Wednesday
        4: [], # Thursday
        5: [], # Friday
        }
    is_conflicting = False
    for section in plan:
        for meeting in section['meetings']:
            for exist_meeting in plan_schedule[meeting['dayofweek']]:
                if is_overlapping(
                    exist_meeting['start_time'],
                    exist_meeting['end_time'],
                    meeting['start_time'],
                    meeting['end_time']
                    ):
                    is_conflicting = True
                    return is_conflicting # Skip the section if they conflict
        else:
            for meeting in section['meetings']:
                plan_schedule[meeting['dayofweek']].append(meeting)
    return is_conflicting


def create_plans(courses):
    valid_plans = []
    course_section_list = [course['sections'] for course in courses]
    all_plans = list(itertools.product(*course_section_list)) # All combination of course plan, including conflicting ones
    for plan in all_plans:
        if not is_conflicting(plan):
            valid_plans.append(plan)
    return valid_plans

def read_schedule_from_file():
    # Read all JSON schedules from the schedules folder
    course_jsons = []
    crouses = []
    for file in os.listdir('schedules'):
        if os.path.splitext(file)[1].upper() == '.JSON':
            with open(os.path.join('schedules', file)) as f:
                course_jsons.append(json.load(f)['SectionsRetrieved']) 
    for course_json in course_jsons:
        crouses.append(format_schedule(course_json))
    return crouses

def save_csv(plans):
    file_name = f'all_valid_plans_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.csv'
    with open(file_name, 'w', newline='') as c_f:
        writer = csv.writer(c_f)
        writer.writerow([f'{course["code"]}: {course["title"]}'for course in plans[0]])
        for plan in plans:
            writer.writerow([f'{course["section_id"]} by {course["instructor"]}' for course in plan])
    return file_name

def main():
    courses = read_schedule_from_file()
    if not courses:
        print('❌ No JSON files found in schedules folders. Bailing...')
        return
    print(f'💬 {len(courses)} courses found:')
    for course in courses:
        print(f'\t- {course["code"]}: {course["title"]}')

    valid_plans = create_plans(courses)
    if not valid_plans:
        print('❌ No valid plans found.')
        return
    print(f'✅ {len(valid_plans)} non-conflicting plans found.')
    file_name = save_csv(valid_plans)
    print(f'✅ {file_name} saved successfully.')
    
if __name__ == '__main__':
    main()