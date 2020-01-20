import os, glob

modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
all_packages = [os.path.basename(f)[:-3] for f in modules if not f.endswith("news_reactor_controller.py") and not f.endswith("economic_data_collection.py")]

