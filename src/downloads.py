import base64
import datetime as dt
import os
from pathlib import Path
from typing import Tuple, Any

import pandas as pd


def get_download_path() -> str:
    """Return the default `downloads` folder path for a user on
    linux or windows.
    """
    if os.name == "nt":
        import winreg

        sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        downloads_guid = "{374DE290-123F-4565-9164-39C4925E467B}"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser("~"), "downloads")


def export_excel(data: pd.DataFrame, download_path: str) -> Tuple[Any, str]:
    """Export the actual `data` DataFrame to Excel using this solution:
    https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806/2
    """
    xlsx_name = f"kpi_export_{dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d-%H-%M-%S')}.xlsx"  # noqa: B950
    xlsx_path = Path(download_path, xlsx_name)
    xlsx = data.to_excel(xlsx_path, index=False)  # noqa: F841
    xlsx_data = open(xlsx_path, "rb").read()
    b64 = base64.b64encode(xlsx_data).decode("UTF-8")
    href = f'<a href="data:file/xlsx;base64,{b64}" download={xlsx_name}>Check your downloads folder, please.</a>'  # noqa: B950
    return b64, href
