from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication
from datetime import datetime

def paste_cwd_to_textbox(text_box):
    """
    Pastes the last content from the clipboard to the given text box.
    
    Args:
    text_box (QTextEdit): The text box to paste the clipboard content into.
    """
    clipboard = QApplication.clipboard()
    clipboard_text = clipboard.text()
    
    if clipboard_text:
        text_box.setText(clipboard_text)
    else:
        print("Clipboard is empty")

def process_cwd(cwd_text, capt_count, fo_count, stw_count):
    """
    Process the CWD text and convert it to the General Declaration format.
    
    Args:
    cwd_text (str): The CWD text to process.
    capt_count (int): Number of captains.
    fo_count (int): Number of first officers.
    stw_count (int): Number of stewards.
    
    Returns:
    str: The processed CWD text in General Declaration format.
    """
    lines = cwd_text.strip().split('\n')
    header = lines[0].split()
    tmp_list = header[0].split('/')
    flight_and_date = f"{tmp_list[0][4:]}/{datetime.strptime(tmp_list[1],'%d%b%y').strftime('%Y/%m/%d')}"
    flight_info = f"{flight_and_date} B____ {header[1]}--{header[2]}--{header[3]}"
    
    crew_list = []
    for line in lines[3:]:  # Skip header lines
        if line.strip():
            parts = line.split()
            name = f"{parts[1].replace('/', ' ')}"
            gender = parts[5]
            birth = datetime.strptime(parts[6], "%d%b%y").strftime("%Y/%m/%d")
            passport = parts[7]
            expiry = datetime.strptime(parts[8], "%y%m%d").strftime("%Y/%m/%d")
            nationality = parts[4]
            crew_list.append((name, gender, birth, passport, expiry, nationality))
    
    gd_text = f"CREW LIST\n{flight_info}\n"
    
    total_crew = len(crew_list)
    dhc_count = total_crew - (capt_count + fo_count + stw_count)
    
    for i, (name, gender, birth, passport, expiry, nationality) in enumerate(crew_list):
        if i < capt_count:
            title = "CAPT"
        elif i < capt_count + fo_count:
            title = "FO  "
        elif i < capt_count + fo_count + stw_count:
            title = "STW "
        else:
            title = "DHC "
        
        # Pad or truncate the name to ensure a fixed length of 29 characters
        formatted_name = f"{name:<30}"[:30]
        
        gd_text += f"{title} {formatted_name} {gender} {birth} {passport} {expiry} {nationality}\n"
    
    gd_text += f"TTL:{capt_count + fo_count}/{stw_count}/{dhc_count}"
    
    return gd_text