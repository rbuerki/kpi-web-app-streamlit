import logging
import logging.config
import psutil
import subprocess
import sys
import time
from pathlib import Path

LOGGING_CONFIG = (Path(__file__).parent / "logging.conf").absolute()
logging.config.fileConfig(fname=LOGGING_CONFIG, disable_existing_loggers=False)
logger = logging.getLogger("checkLogger")

CMDLINE_PART = "streamlit.exe"


def check_process_from_server(cmdline_part: str) -> bool:
    """Check if a python process is running that was launched with
    a certain command line string and return a respective bool.
    """
    try:
        for pid in psutil.pids():
            p = psutil.Process(pid)
            if (
                p.name() == "python.exe"
                and len(p.cmdline()) > 1
                and cmdline_part in p.cmdline()[1]
            ):
                logger.info("All good. Streamlit process is running.")
                return True

        logger.warning("Streamlit process is not running. Will call launch script!")
        return False

    except Exception as e:
        logger.error(f"Encountered some problems on the Streamlit Server: {e}")
        return False


def main():
    """Run the check function and depending on the result run
    `app_launch.bat` to relaunch the app. This module is scheduled
     to run daily at 06.55 AM in the Windows Task Scheduler on
     the Server. It is started by `app_check.bat`.
     """
    check_result = check_process_from_server(cmdline_part=CMDLINE_PART)
    if check_result is False:
        logger.info("Launching KPI-App ...")
        try:
            subprocess.call([r"C:\Projects\kpi_app\app_launch.bat"])
        except Exception as e:
            logging.error(e)
        finally:
            logger.info("Exiting checker ...")
            time.sleep(2)
            sys.exit()
    else:
        logger.info("Exiting checker ...")
        time.sleep(2)
        sys.exit()


if __name__ == "__main__":
    main()


# For request checks from local machine
# URL_DEV = "http://localhost:8501/"
# URL_PROD = "http://172.30.0.22:8501/"


# def check_status_from_local_machine(url: str = URL_PROD):
#     """Check if you get an active status code for the passed
#     URL. If not call `app_launch` module to relaunch the app.

#     This was my first attempt. But unfortunately the port cannot
#     be accessed from the server environment, so it never returned
#     a positive code in production. But it still works from my
#     local machine to check if the server app is running if I
#     pass `URL_PROD` as argument. (`URL_DEV` checks the app if it
#     is run from the local machine.)
#
#     Irony: The upper code does not work from my local machine.
#     Because we are not allowed run bat scripts.
#     """
#     try:
#         request = requests.get(url)
#         if request.status_code == 200:
#             print("All good. Web site exists.")
#         else:
#             print("Web site does not exist.")
#             # app_launch.launch_app()
#     except Exception as e:
#         print(f"Web site does not exist: {e}")
#         # app_launch.launch_app()
