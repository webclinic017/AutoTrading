import os, glob, sys, inspect

modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
all_packages = [os.path.basename(f)[:-3] for f in modules if not f.endswith("risk_management_controller.py") and not f.endswith("general_functions.py")]

