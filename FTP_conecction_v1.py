# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 11:42:16 2023

@author: nestor.gualsaqui

Description:
This code creates a connection between the local machine and FTP. The goal is to download a file located on the FTP.
This code is a compilation from Stackoverflow.

"""

import os
import ftplib
from credentials import FTP_access # importing dictionary with passwords in folder Credentials 
import logging
import sys


# log infos
log_perpetual = logging.getLogger("perpetual")
log_current = logging.getLogger("current")

# encripted connection
#------------------------------------------------------------------------------
# FTP connection
# \\FTP_example.local\Documents\data
#------------------------------------------------------------------------------
# credentials
# server = FTP_access.secrets_dict["documents_prod"]["host"]
# username = FTP_access.secrets_dict["documents_prod"]["user"]
# password = FTP_access.secrets_dict["documents_prod"]["password"]



# function for creating connection to FTP
# def connect2ftp(server: str, username: str, password: str) -> ftplib.FTP_TLS:
#     ftplib.FTP_TLS.ssl_version = ssl.PROTOCOL_TLSv1_2
#     global ftps
#     ftps = ftplib.FTP_TLS()
#     #ftps.set_debuglevel(2)
#     ftps.connect(host=server, port=21, timeout=20)
#     ftps.login(username, password)
#     ftps.set_pasv(True)
#     #enable explicit TLS
#     ftps.prot_p()
#     log_current.info("Connection to FTP-server established.")
#     return ftps

# unencripted connection
def connect2ftp(server: str, username: str, password: str) -> ftplib.FTP:
    global ftps

    try:
        ftps = ftplib.FTP(server)
        ftps.login(username, password)
        ftps.set_pasv(True)  # Set passive mode
        log_current.warning("Unencrypted connection to FTP-server established.")
        print('------------------------------------------>')
        return ftps
    except Exception as e:
        log_current.error("Error establishing unencrypted FTP connection: %s", str(e))
        raise  # Reraise the exception for higher-level handling



def get_monthly_report(ftps_conn: ftplib.FTP_TLS, data_source_dir: str, ftp_report_folder: str = "~/") -> \
        tuple[bool, os.path]:
    global entries_all, newest_file, target_file_final, monday_dateSpeerIT

    try:
        with ftps_conn:
            print('-------------------------------->')
            print('FTP connection established')
            print('-------------------------------->')
            # folder is already in Dokumente
            ftps.pwd()
                
            log_current.info("Connection to FTP-server established.")
            
            # File that we are looking for download
            target_file = 'target_file.csv'
            print('------------------------------------------------------->')
            print(f'Target file to download in FTP folder: {target_file}')
            print('getting all files list in main folder...')
            print('------------------------------------------------------->')
            entries_all= list(ftps.mlsd())
            entries = list(filter(lambda file: target_file in file, ftps_conn.mlsd()))
            
            log_current.info(f"Entries: {entries}")
            entries.sort(key=lambda entry: entry[1]['modify'], reverse=True)
            print(entries)
            newest_file = entries[0][0]
            
            log_current.info(f"Files on FTP-server matching description: {entries}")

            data_path = os.path.join(data_source_dir, newest_file)
            
            with open(data_path, 'wb') as file:
                ftps_conn.retrbinary('RETR ' + newest_file, file.write)
                log_current.info(f"File downloaded: '{newest_file}' to '{data_source_dir}'.")

            if (os.path.isfile(data_path) and os.path.getsize(data_path) == int(entries[0][1]["size"])):
                log_perpetual.info("Download successfull.")
                return True, data_path
            else:
                log_perpetual.warning("Download failed.")
                return False, None

    except ftplib.all_errors as e:
        log_perpetual.error(e)
        sys.exit(1)



def main():

    server = r"ftp.example"
    user = "example.interface.documents"
    password = FTP_access.secrets_dict["password"]
    report_folder = ""
    data_source_dir = os.getcwd()+'\\data\\downloads'

    # creating connection
    ftps_conn = connect2ftp(server, user, password)
    download_complete, weekly_file_path = get_monthly_report(ftps_conn, data_source_dir, report_folder)
    if download_complete:
        print('------------------------------------------------------->')
        print(f"Download successfully. File location: {weekly_file_path}")
        print('------------------------------------------------------->')

    else:
        print("Download not successful")


# if __name__ == "__main__":
#     main()



