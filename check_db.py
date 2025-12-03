from app.core.db import db
from pprint import pprint

def check():
    print("=== Tasks ===")
    for task in db.tasks.find():
        pprint(task)
        
    print("\n=== Steps (Checkpoints) ===")
    for step in db.steps.find():
        print(f"Step: {step['step_name']} | Task: {step['task_id']}")
        # pprint(step['output_data']) # 数据太多可以注释掉

if __name__ == "__main__":
    check()