#!/usr/bin/env python3

import json
from datetime import datetime

with open('/home/meyers/Downloads/job_330588_events.txt.modified') as f:
    ds = json.load(f)

class TaskAction:
    def __init__(self, action, stdout_size, event_data_size):
        self.action = action
        self.stdout_size = stdout_size
        self.event_data_size = event_data_size

class TaskActionManager:
    def __init__(self, action_name):
        self.action = action_name
        self.actions = []
        self.call_count = 0
        self.stdout_size_avg = 0
        self.stdout_size_total = 0
        self.stdout_size_count = 0

        self.event_data_size_avg = 0
        self.event_data_size_total = 0
        self.event_data_size_count = 0

    def add(self, stdout_size, event_data_size):
        t = TaskAction(self.action, stdout_size, event_data_size)
        self.actions.append(t)
        self.call_count += 1
        self.stdout_size_total += stdout_size
        self.stdout_size_count += 1
        self.stdout_size_avg = float(self.stdout_size_total / self.stdout_size_count)

        self.event_data_size_total += event_data_size
        self.event_data_size_count += 1
        self.event_data_size_avg = float(self.event_data_size_total / self.event_data_size_count)

        return t

    def get_stdout_size_avg(self):
        return self.stdout_size_avg

    def get_event_data_size_avg(self):
        return self.event_data_size_avg

    def get_event_data_size_total(self):
        return self.event_data_size_total

class StatsManager:
    def __init__(self):
        self.task_actions = {}
        self.earliest_created = None
        self.earliest_modified = None
        self.latest_created = None
        self.latest_modified = None

    def add_task(self, t):
        k = t.get('event_data', {}).get('task_action', {})
        size_stdout = len(t.get('stdout', ''))
        event_data_size = len(json.dumps(t.get('event_data', '')))
        created = t['created']
        modified = t['modified']
        if not k:
            return None
        self.task_actions.setdefault(k, TaskActionManager(k))

        def capture(new, old, f):
            new = (datetime.strptime(new, "%Y-%m-%dT%H:%M:%S.%fZ") - datetime(1970, 1, 1)).total_seconds()
            return f(new, old or new)

        self.earliest_modified = capture(modified, self.earliest_modified, min)
        self.latest_modified = capture(modified, self.latest_modified, max)

        self.earliest_created = capture(created, self.earliest_created, min)
        self.latest_created = capture(created, self.latest_created, max)

        return self.task_actions[k].add(size_stdout, event_data_size)

    def output_task_action_stats(self):
        print("Event stdout data stats:\n")
        print("===============================================")
        for k in sorted(self.task_actions.keys(), key=lambda k: self.task_actions[k].get_stdout_size_avg(), reverse=True):
            v = self.task_actions[k]
            print(f"{k:20} {v.get_stdout_size_avg()}")
        print("")

        print("Event data stats:")
        print("===============================================")
        h = ["action", "size avg", "size total"]
        print(f"{h[0]:20} {h[1]:10} {h[2]:10}")
        for k in sorted(self.task_actions.keys(), key=lambda k: self.task_actions[k].get_event_data_size_total(), reverse=True):
            v = self.task_actions[k]
            print(f"{k:20} {int(v.get_event_data_size_avg()):10} {v.get_event_data_size_total():10}")
        print("")

        print("Event data aggregate stats:")
        print("===============================================")
        data_size_total = sum(x.get_event_data_size_total() for x in self.task_actions.values())
        print(f"Total data size: {data_size_total}")
        print(f"Best guess runtime of the playbook (in seconds): {self.latest_created - self.earliest_created}")
        print(f"Best guess on how far behind the event processor is (in seconds): {self.latest_modified - self.latest_created}")


smgr = StatsManager()
errors = 0
total = 0
for d in ds:
    res = smgr.add_task(d)
    if res is None:
        errors += 1
    total += 1

smgr.output_task_action_stats()

print("Error stats:")
print(f"{errors} errors vs. Total {total}")

