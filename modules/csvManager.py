import csv
from datetime import datetime

class Csv:
    def __init__(self, parent): 
        self.pref = parent.pref
        self.file = parent.file
        self.tracker_file = self.file.track()
        self.planner_file = self.file.plan()
        self.tracker = Tracker(self)
        self.planner = Planner(self)

    def init_csv(self):
        self.tracker.initialize()
        self.planner.initialize()
    
    def read_file(self, file_path):
        data = []
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    data.append(row)
        except (FileNotFoundError, csv.Error):
            print(f"Error reading CSV file: {file_path}")
        return data

    def read_line(self, file_path, line_id, id_column=0):
        data = self.read_file(file_path)
        for row in data:
            if row[id_column] == line_id:
                return row
        return None

    def clear_file(self, file_path):
        try:
            with open(file_path, 'w', newline='') as csvfile:
                pass  # Just open and close to clear the file
        except csv.Error:
            print(f"Error clearing CSV file: {file_path}")

    def write_file(self, file_path, header, data=None):
        self.clear_file(file_path)
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                if data:
                    writer.writerows(data)
        except csv.Error:
            print(f"Error writing to CSV file: {file_path}")

    def append_line(self, file_path, row):
        try:
            with open(file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row)
        except csv.Error:
            print(f"Error appending to CSV file: {file_path}")

    def delete_line(self, file_path, line_id, id_column=0):
        data = self.read_file(file_path)
        new_data = [row for row in data if row[id_column] != line_id]
        header = data[0] if data else []
        self.write_file(file_path, header, new_data)

    def generate_date_range(self, start_date, end_date):
        from datetime import datetime, timedelta
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        date_list = []
        current_date = start
        while current_date <= end:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        return date_list

class Tracker: 
    def __init__(self, parent):
        self.csv = parent
        self.pref = parent.pref
        self.file = parent.file
        self.tracker_file = parent.file.track()

    def initialize(self):
        # Refresh tracker file path in case it has changed
        self.tracker_file = self.file.track()
        # Initialize tracker CSV file if it does not exist from project start to current date
        try:
            with open(self.tracker_file, 'r') as f:
                data = self.read()
                # Check if header needs to be updated
                if data:
                    header = data[0]
                    tracker_start = self.pref.get_setting("project_start_date")
                    tracker_end = datetime.now().strftime("%Y-%m-%d")
                    expected_dates = self.csv.generate_date_range(tracker_start, tracker_end)
                    existing_dates = header[2:]  
                    if existing_dates != expected_dates:
                        # Update header
                        new_header = ['ID', 'Name'] + expected_dates
                        new_data = []
                        for row in data[1:]:
                            new_row = row[:2]  
                            for date in expected_dates:
                                if date in header:
                                    date_index = header.index(date)
                                    new_row.append(row[date_index])
                                else:
                                    new_row.append('0')  
                            new_data.append(new_row)
                        self.csv.write_file(self.tracker_file, new_header, new_data)
        except (FileNotFoundError):
            with open(self.tracker_file, 'w', newline='') as csvfile:
                header = ['ID', 'Name']
                tracker_start = self.pref.get_setting("project_start_date")
                tracker_end = datetime.now().strftime("%Y-%m-%d")
                date_range = self.csv.generate_date_range(tracker_start, tracker_end)
                header.extend(date_range)
                self.csv.write_file(self.tracker_file, header)
        except (csv.Error):
            print("Error reading tracker CSV file.")

    def read(self):
        return self.csv.read_file(self.tracker_file)
    
    def read_task(self, task_id):
        return self.csv.read_line(self.tracker_file, task_id)

    def add_task(self, task_id, task_name):
        self.csv.append_line(self.tracker_file, [task_id, task_name])

    def delete_task(self, task_id):
        self.csv.delete_line(self.tracker_file, task_id)

    def edit_entry(self, task_id, date, new_value):
        data = self.read()
        header = data[0]
        if date in header:
            date_index = header.index(date)
            for row in data[1:]:
                if row[0] == task_id:
                    row[date_index] = new_value
                    break
            self.csv.write_file(self.tracker_file, header, data)
        else:
            print(f"Date {date} not found in tracker header.")

    def extend(self, new_start_date, new_end_date):
        data = self.read()
        header = data[0]
        existing_dates = set(header[2:])  
        new_dates = self.csv.generate_date_range(new_start_date, new_end_date)
        for date in new_dates:
            if date not in existing_dates:
                header.append(date)
                for row in data[1:]:
                    row.append('0')  
        self.csv.write_file(self.tracker_file, header, data)

    def crop(self, new_start_date, new_end_date):
        # Warning: this may delete data outside the new date range
        data = self.read()
        header = data[0]
        date_indices = [i for i, date in enumerate(header) if date >= new_start_date and date <= new_end_date]
        new_header = ['ID', 'Name'] + [header[i] for i in date_indices]
        new_data = [new_header]
        for row in data[1:]:
            new_row = [row[0], row[1]] + [row[i] for i in date_indices]
            new_data.append(new_row)
        self.csv.write_file(self.tracker_file, new_header, new_data)


class Planner:
    def __init__(self, parent):
        self.csv = parent
        self.pref = parent.pref
        self.file = parent.file
        self.planner_file = parent.file.plan()

    def initialize(self): 
        # Refresh planner file path in case it has changed
        self.planner_file = self.file.plan()
        # Initialize planner CSV file if it does not exist from project start to end date
        try:
            with open(self.planner_file, 'r') as f:
                data = self.read()
                # Checking / updating will be handled elsewhere as needed
        except (FileNotFoundError):
            with open(self.planner_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                header = ['ID', 'Name']
                planner_start = self.pref.get_setting("project_start_date")
                planner_end = self.pref.get_setting("project_end_date")
                date_range = self.csv.generate_date_range(planner_start, planner_end)
                header.extend(date_range)
                self.csv.write_file(self.planner_file, header)
        except (csv.Error): 
            print("Error reading planner CSV file.")

    def read(self):
        return self.csv.read_file(self.planner_file)
    
    def read_task(self, task_id):
        return self.csv.read_line(self.planner_file, task_id)

    def add_task(self, task_id, task_name):
        self.csv.append_line(self.planner_file, [task_id, task_name])

    def delete_task(self, task_id):
        self.csv.delete_line(self.planner_file, task_id)

    def edit_entry(self, task_id, date, new_value):
        data = self.read()
        header = data[0]
        if date in header:
            date_index = header.index(date)
            for row in data[1:]:
                if row[0] == task_id:
                    row[date_index] = new_value
                    break
            self.csv.write_file(self.planner_file, header, data)
        else:
            print(f"Date {date} not found in planner header.")

    def extend(self, new_start_date, new_end_date):
        data = self.read()
        header = data[0]
        existing_dates = set(header[2:])  
        new_dates = self.csv.generate_date_range(new_start_date, new_end_date)
        for date in new_dates:
            if date not in existing_dates:
                header.append(date)
                for row in data[1:]:
                    row.append('0')  
        self.csv.write_file(self.planner_file, header, data)

    def crop(self, new_start_date, new_end_date):
        # Warning: this may delete data outside the new date range
        data = self.read()
        header = data[0]
        date_indices = [i for i, date in enumerate(header) if date >= new_start_date and date <= new_end_date]
        new_header = ['ID', 'Name'] + [header[i] for i in date_indices]
        new_data = [new_header]
        for row in data[1:]:
            new_row = [row[0], row[1]] + [row[i] for i in date_indices]
            new_data.append(new_row)
        self.csv.write_file(self.planner_file, new_header, new_data)

'''
CSV data format: 

Tracker:
ID, Name, ProjectStartDate, Date, Date, ..., ProjectEndDate
taskID, taskName (for readability), work, work, work...

Planner:
ID, Name, ProjectStartDate, Date, Date, ..., ProjectEndDate
taskID, taskName (for readability), plannedWork, plannedWork, plannedWork...

'''