"""
File: main.py.py
Author: 한정석
Date: 2025. 10. 23.
Last Modified: 2025. 10. 23.
Description:
    - [실습] 

Notes:
    • 
"""
import os

from dotenv import load_dotenv
from supervisor.workflow import run_supervisor

load_dotenv()

if __name__ == "__main__":
    run_supervisor("Analyze EV industry market and finance trends in 2025.")