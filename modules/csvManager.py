import csv

class Csv:
    def __init__(self, parent): 
        self.pref = parent.pref
        self.file = parent.file
        self.tracker_file = self.file.track()
        self.planner_file = self.file.plan()

    def initialize_tracker(self):
        try:
            with open(self.tracker_file, 'r') as f:
                self.read_tracker()    
        except (FileNotFoundError, csv.Error):
            with open(self.tracker_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                header = ['ID', 'Name']
                project_start = self.pref.get_project_start_date()
                project_end = self.pref.get_project_end_date()
                date_range = self.pref.generate_date_range(project_start, project_end)
                header.extend(date_range)
                writer.writerow(header)

    def initialize_planner(self): 
        pass

    def initialize_csv(self):
        self.initialize_tracker()
        self.initialize_planner()

    def initialize_file(self, file):
        if file == self.tracker_file:
            self.initialize_tracker()
        elif file == self.planner_file:
            self.initialize_planner()

    def read_tracker():
        return read(self.tracker_file)

    def read_planner():
        return read(self.planner_file)

    def read(self, file):
        data = []
        try:
            with open(file, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            self.initialize_file(file)   
        return data

    def read_task_tracker(self, task_id):
        data = self.read_tracker()
        for row in data:
            if row and row[0] == task_id:
                return row
        return None

    def read_task_planner(self, task_id):
        data = self.read_planner()
        for row in data:
            if row and row[0] == task_id:
                return row
        return None


'''
CSV data format: 

Tracker:
ID, Name, ProjectStartDate, Date, Date, ..., ProjectEndDate
taskID, taskName (for readability), work, work, work...

Planner:
ID, Name, ProjectStartDate, Date, Date, ..., ProjectEndDate
taskID, taskName (for readability), plannedWork, plannedWork, plannedWork...

'''