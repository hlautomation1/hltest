import os
import shutil
import psutil
import psycopg2
import requests
import json
import re
import logging
import subprocess
import shutil

from datetime import datetime
from requests.auth import HTTPBasicAuth
from getapikey import get_api_key


class Platform():

    def __init__(self, css_database, css_user, css_password, css_host, css_port, console_restURL, console_user,
                 console_password, console_api_key, warnDays, msinfra_ticket_no, url, jira_user_name, jira_password):
        self.css_database = css_database
        self.css_user = css_user
        self.css_password = css_password
        self.css_host = css_host
        self.css_port = int(css_port)

        self.console_restURL = console_restURL
        self.console_user = console_user
        self.console_password = console_password
        self.console_api_key = console_api_key
        self.warnDays = int(warnDays)

        self.msinfra_ticket_no = msinfra_ticket_no
        self.url = url
        self.jira_user_name = jira_user_name
        self.jira_password = jira_password

        # this function updates AIP Console for Username and Password inside Platform_Health_Check_Settings.json file.

    def update_console_username_and_password(self, json_file):

        try:
            method = "get"
            url = f"{self.console_restURL}api/"
            auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')

            rsp = requests.request(method, url, auth=auth)
            # print(rsp.status_code)
            if rsp.status_code == 401:
                auth = HTTPBasicAuth('cast', 'cast')
                rsp_2 = requests.request(method, url, auth=auth)
                if rsp_2.status_code == 200:
                    with open(json_file, "r") as a_file:
                        json_object = json.load(a_file)
                    json_object["console"]["user"] = 'cast'
                    json_object["console"]["password"] = 'cast'
                    self.console_user = 'cast'
                    self.console_password = 'cast'
                    with open(json_file, "w") as a_file:
                        json.dump(json_object, a_file)

                    print(
                        f"updated the AIP Console for Username as cast and Password as cast inside Platform_Health_Check_Settings.json file.")
                    logging.error(
                        f"updated the AIP Console for Username as cast and Password as cast inside Platform_Health_Check_Settings.json file.")

        except Exception as e:
            print(
                'some exception has occured! while executing update_console_username_and_password() function.\n Please resolve them or contact developers.')
            logging.error(
                'some exception has occured! while executing update_console_username_and_password() function.\n Please resolve them or contact developers.')
            print(e)
            logging.error(e)

    # this function updates the CSS port number inside Platform_Health_Check_Settings.json file.
    def update_css_details(self, json_file, host_name):

        try:
            method = "get"
            url = f"{self.console_restURL}api/settings/measurement-settings"
            auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')
            headers = {"X-API-KEY": self.console_api_key}

            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                data = json.loads(rsp.text)
                port_no = data["database"]["port"]
                host_name = data["database"]["host"]
                # print(port_no)

                with open(json_file, "r") as a_file:
                    json_object = json.load(a_file)
                json_object["css"]["port"] = port_no
                json_object["css"]["host"] = host_name
                self.css_host = host_name
                self.css_port = port_no

                with open(json_file, "w") as a_file:
                    json.dump(json_object, a_file)

                    print(
                        f"updated the CSS port number as {port_no} and hostname as {host_name} inside Platform_Health_Check_Settings.json file.")
                    logging.info(
                        f"updated the CSS port number as {port_no} and hostname as {host_name} inside Platform_Health_Check_Settings.json file.")

            else:
                port_no = 2282

                with open(json_file, "r") as a_file:
                    json_object = json.load(a_file)
                json_object["css"]["port"] = port_no
                json_object["css"]["host"] = host_name
                self.css_host = host_name
                self.css_port = port_no

                with open(json_file, "w") as a_file:
                    json.dump(json_object, a_file)

                    print(
                        f"updated the CSS port number as {port_no} and hostname as {host_name} inside Platform_Health_Check_Settings.json file.")
                    logging.info(
                        f"updated the CSS port number as {port_no} and hostname as {host_name} inside Platform_Health_Check_Settings.json file.")


        except Exception as e:
            print(
                'some exception has occured! while executing update_css_details() function.\n Please resolve them or contact developers.')
            logging.error(
                'some exception has occured! while executing update_css_details() function.\n Please resolve them or contact developers.')
            print(e)
            logging.error(e)

    def get_applications_from_console(self):
        method = "get"
        url = f"{self.console_restURL}api/applications"
        auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')
        headers = {"X-API-KEY": self.console_api_key}
        logging.info(f' fetching App details {url}')

        try:
            # fetching the Application list and details.
            rsp = requests.request(method, url, auth=auth, headers=headers)
            logging.info(f'App details response {rsp}')

            if rsp.status_code == 200:
                apps = json.loads(rsp.text)
                apps_dict = {}
                for app in apps['applications']:
                    app_name = app["name"]
                    app_guid = app["guid"]
                    apps_dict[app_name] = app_guid
                return apps_dict
        except Exception as e:
            logging.error(
                "get_applications_from_console() :- some exception has occured while getting applications from console! \n Please resolve them or contact developers")
            print(
                'get_applications_from_console() :- some exception has occured while getting applications from console! \n Please resolve them or contact developers')
            logging.error(e)
            print(e)

    def get_the_license_from_the_console(self):
        method = "get"
        url = f"{self.console_restURL}api/settings/license"

        auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')
        headers = {"X-API-KEY": self.console_api_key}

        try:
            # fetching the Application list and details.
            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                data = json.loads(rsp.text)
                if data["license"]:
                    return data["license"]
                else:
                    return 0
        except Exception as e:
            logging.error(
                "get_the_license_from_the_console() :- some exception has occured while getting application license from the console! \n Please resolve them or contact developers")
            print(
                'get_the_license_from_the_console() :- some exception has occured while getting application license from the console! \n Please resolve them or contact developers')
            logging.error(e)
            print(e)

    def get_local_schema(self, guid):
        url = f"{self.console_restURL}api/aic/applications/{guid}"
        auth = HTTPBasicAuth(f'{self.console_user}', f'{self.console_password}')
        headers = {"X-API-KEY": self.console_api_key}

        try:
            # fetching the app schemas.
            rsp = requests.get(url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                data = json.loads(rsp.text)

                for i in range(len(data["schemas"])):
                    if data["schemas"][i]["type"] == 'local':
                        return data["schemas"][i]["name"]

            else:
                print("Some error has occured! While fetching local schema.")
                print(rsp.text)

        except Exception as e:
            print(
                'some exception has occured! While fetching local schema.\n Please resolve them or contact developers')
            print(e)

    def update_application_license_key(self, app_local_schema, console_license_key):

        try:
            # Establish a connection to the PostgreSQL server
            connection = psycopg2.connect(
                host=self.css_host,
                port=self.css_port,
                dbname=self.css_database,
                user=self.css_user,
                password=self.css_password
            )
            connection.autocommit = True
            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()
            # if '.' in application_name:
            #     application_name = application_name.replace('.','_')
            # if '-' in application_name:
            #     application_name = application_name.replace('-','_')
            # Execute a simple query to fetch the license key from css
            cursor.execute(f"select * from {app_local_schema}.sys_licenses")
            # Fetch the result
            result = cursor.fetchone()
            if result is None:
                cursor.execute(
                    f"INSERT INTO {app_local_schema}.sys_licenses (license_code, license_id) VALUES ('{console_license_key}', 0)")
            else:
                cursor.execute(f"UPDATE {app_local_schema}.sys_licenses SET license_code='{console_license_key}'")

            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            logging.error(
                "update_application_license_key() :- some exception has occured while updating application license in the CSS! \n Please resolve them or contact developers")
            print(
                'update_application_license_key() :- some exception has occured while updating application license in the CSS! \n Please resolve them or contact developers')
            logging.error(e)
            print(e)

    def check_postgres_status(self):
        try:
            # Establish a connection to the PostgreSQL server
            connection = psycopg2.connect(
                host=self.css_host,
                port=self.css_port,
                dbname=self.css_database,
                user=self.css_user,
                password=self.css_password
            )
            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()
            # Execute a simple query to fetch the current PostgreSQL version
            cursor.execute("SELECT version();")
            # Fetch the result
            result = cursor.fetchone()
            logging.info("check_postgres_status() :- OK - the database is up and accept connection.")
            # print("OK the database is up and accept connection.")
            # Close the cursor and connection
            cursor.close()
            connection.close()

            return "OK"
        except Exception as e:
            logging.info("check_postgres_status() :- KO - the database is not accepting connection).")
            logging.error("check_postgres_status() :- PostgreSQL connection failed:", e)
            # print("KO the database is not accepting connection.")
            # print("PostgreSQL connection failed:", e)
            return "KO - the database is not accepting connection"

    def calculate_remaining_days(self, date_string):
        # Get the current date
        current_date = datetime.now().date()

        # Parse the given date string
        given_date = datetime.strptime(date_string, "%Y-%m-%d").date()

        # Calculate the difference between the given date and the current date
        remaining_days = (given_date - current_date).days

        return remaining_days

    def check_the_licence_key_in_css(self, app_local_schema):
        try:
            # Establish a connection to the PostgreSQL server
            connection = psycopg2.connect(
                host=self.css_host,
                port=self.css_port,
                dbname=self.css_database,
                user=self.css_user,
                password=self.css_password
            )
            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()
            # if '.' in application_name:
            #     application_name = application_name.replace('.','_')
            # if '-' in application_name:
            #     application_name = application_name.replace('-','_')
            # Execute a simple query to fetch the license key from css
            cursor.execute(f"select * from {app_local_schema}.sys_licenses")
            # Fetch the result
            result = cursor.fetchone()
            if result is None:
                logging.info(
                    "check_the_licence_key_in_css() :- KO - at the date of the check the license key is not set.")
                # print('KO at the date of the check the license key has expired or is not set.')
                return 'KO - License key is not set'
            elif len(result[1]) > 0:
                # logging.info("Licence Key:"+ str(result[1]))
                # print("Licence Key:", result[1])

                expiry_date_pattern = '(\\d{8})'
                expiry_date = re.findall(expiry_date_pattern, result[1])
                if len(expiry_date) > 0:
                    date_string = expiry_date[0][:4] + '-' + expiry_date[0][4:6] + '-' + expiry_date[0][6:]
                    remaining_days = self.calculate_remaining_days(date_string)
                    if remaining_days <= 0:
                        logging.info(
                            "check_the_licence_key_in_css() :- KO - at the date of the check the license key has expired.")
                        return 'KO - License key has expired'
                    elif remaining_days < self.warnDays:
                        logging.info(
                            f'check_the_licence_key_in_css() :- WARN - the license key is about to expire in less than {remaining_days} calendar days.')
                        # print('OK the license is valid at the date of the check.')
                        # print(f'WARN the license key is about to expire in less than {remaining_days} calendar days.')
                        return f'WARN (expires in less than {remaining_days} days.)'
                    else:
                        logging.info(
                            "check_the_licence_key_in_css() :- OK - the license is valid at the date of the check.")
                        # print('OK the license is valid at the date of the check.')
                        return 'OK'

            # Close the cursor and connection
            cursor.close()
            connection.close()
        except Exception as e:
            logging.error(
                "check_the_licence_key_in_css() :- ERR - some error occurred that prevented to get the status -> " + str(
                    e))
            if app_local_schema is None:
                return 'KO - Application declared but no analysis run'
            # print("ERR some error occurred that prevented to get the status -> ",e)
            # print("PostgreSQL connection failed:", e)
            return 'ERR'

    def check_the_licence_key_in_console(self):

        method = "get"
        url = f"{self.console_restURL}api/settings/license"
        auth = HTTPBasicAuth(self.console_user, self.console_password)
        headers = {"X-API-KEY": self.console_api_key}

        try:
            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                licence_key_details = json.loads(rsp.text)

            if licence_key_details["license"] is None:
                logging.info(
                    'check_the_licence_key_in_console() :- KO - at the date of the check the license key is not set.')
                # print('KO at the date of the check the license key has expired or is not set.')
                return 'KO - License key is not set'
            elif len(licence_key_details["license"]) > 0:
                # logging.info("check_the_licence_key_in_console() :- Licence Key:" + str(licence_key_details["license"]))
                # print("Licence Key:", licence_key_details["license"])
                # logging.info("check_the_licence_key_in_console() :- Expiry Date:" + str(licence_key_details["expirationDate"]))
                # print("Expiry Date:", licence_key_details["expirationDate"])

                remaining_days = self.calculate_remaining_days(licence_key_details["expirationDate"])
                if remaining_days <= 0:
                    logging.info(
                        "check_the_licence_key_in_console() :- KO - at the date of the check the license key has expired.")
                    return 'KO - License key has expired'
                elif remaining_days < self.warnDays:
                    logging.info(
                        'check_the_licence_key_in_console() :- OK - the license is valid at the date of the check.')
                    # print('OK the license is valid at the date of the check.')
                    logging.info(
                        f'check_the_licence_key_in_console() :- WARN - the license key is about to expire in less than {remaining_days} calendar days.')
                    # print(f'WARN the license key is about to expire in less than {remaining_days} calendar days.')
                    return f'WARN - (expires in less than {remaining_days} days.)'
                else:
                    logging.info(
                        "check_the_licence_key_in_console() :- OK - the license is valid at the date of the check.")
                    # print('OK the license is valid at the date of the check.')
                    return 'OK'
        except Exception as e:
            logging.error(
                "check_the_licence_key_in_console() :- ERR - some error occurred that prevented to get the status -> " + str(
                    e))
            if str(e) == "cannot access local variable 'licence_key_details' where it is not associated with a value":
                return 'KO  Imaging Console Initial configuration is not done'
            # print("PostgreSQL connection failed:", e)
            return 'ERR'

    def check_diskspace(self):
        try:
            mount_point = '/'  # Root filesystem in Linux
            
            usage = psutil.disk_usage("/")

            used_gb = round(usage.used / (1024 ** 3), 2)
            free_gb = round(usage.free / (1024 ** 3), 2)
            used_percent = usage.percent
            free_percent = round(100 - used_percent, 2)
            
            if free_percent < 5:
                DiskSpace_status = (
                    f"KO - (Used={used_gb} GB, Free={free_gb} GB, Used={used_percent}%, Free={free_percent}%)"
                )

            elif free_percent < 10:
                DiskSpace_status = (
                    f"WARN - (Used={used_gb} GB, Free={free_gb} GB, Used={used_percent}%, Free={free_percent}%)"
                )

            else:
                DiskSpace_status = "OK({}GB Free And {}% Are Free)".format(free_gb,free_percent)
                logging.info(
                    "check_diskspace() :- OK  Enough disk space on {} mount, used {} and {} free ".format(mount_point,usage,free_gb)
                )

            return DiskSpace_status

        except Exception as e:
            logging.error(
                "check_diskspace() :- ERR  Exception occurred: {}".format(str(e))
            )
            return "ERR"

    def is_aip_console_version_2x(self):

        method = "get"
        url = f"{self.console_restURL}api/"
        auth = HTTPBasicAuth(self.console_user, self.console_password)
        headers = {"X-API-KEY": self.console_api_key}

        try:
            rsp = requests.request(method, url, auth=auth, headers=headers)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                res = json.loads(rsp.text)
                aip_console_version = res["apiVersion"]

                # Extract the major version using a regular expression
                match = re.match(r'^(\d+)\.\d+\.\d+', aip_console_version)

                if match:
                    major_version = int(match.group(1))
                    return major_version == 2
                return False

        except Exception as e:
            logging.error(
                "check_aip_console_version() :- ERR - some error occurred while checking aip console version -> " + str(
                    e))
            return False

    def check_HDED(self):
        try:
            def check_HDED_status(service_name):
                for service in psutil.win_service_iter():
                    service_name = service.name()
                    if service_name_substring.lower() in service_name.lower():
                        try:
                            status = psutil.win_service_get(service_name).status()
                            if status == 'running':
                                logging.info(f"check_HDED() :- OK  '{service_name}' service is running.")
                                return 'OK', service_name
                            else:
                                logging.error(f"check_HDED() :- KO - '{service_name}' service is not running.")
                                return 'KO', service_name
                        except Exception as e:
                            logging.error(f"check_HDED() :- ERR - 'hded' service was not found.")
                            return 'ERR', 'hded'

            def check_REST_Client_status(url):
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        logging.info(
                            f"check_REST_Client_status() :- OK - status code is '{response.status_code}' and '{url}' is working.")
                        return 'OK'
                    else:
                        logging.error(
                            f"check_REST_Client_status() :- KO - status code is '{response.status_code}' and '{url}' is not working.")
                        return 'KO'
                except Exception as e:
                    logging.error(
                        f"check_REST_Client_status() :- ERR - some exception has occured while executing this function: " + str(
                            e))
                    return 'ERR'

            if self.is_aip_console_version_2x():

                service_name_substring = "hded"
                HDED_service_status, service_name = check_HDED_status(service_name_substring)

                url = "http://localhost:8087/static/default.html"
                HDED_url_status = check_REST_Client_status(url)

                if HDED_service_status == 'OK' and HDED_url_status == 'OK':
                    return 'OK'
                elif HDED_service_status == 'KO':
                    return f"KO - '{service_name}' service is not running."
                elif HDED_service_status == 'ERR':
                    return f"ERR - '{service_name}' service was not found."
                elif HDED_url_status == 'KO':
                    return f"KO - '{url}' is not working."
                elif HDED_url_status == 'ERR':
                    return f"ERR - while accessing the url - '{url}'."

            else:
                return "N/A for AIP Console Version-1.X"

        except Exception as e:
            logging.error("check_HDED() :- some exception has occured while executing this function:" + str(e))
            return f"ERR - 'hded' service was not found.\n{e}"

    def create_html_table(self, data, platform, host_name, current_date_time, msinfra_ticket_no, exe_version):

        table_html = f"""
        <p><b>Platform:</b> {platform}</p>
        <p><b>Hostname:</b> {host_name}</p>
        <p><b>MSINFRA:</b> {msinfra_ticket_no}</p>
        <p><b>Generated on:</b> {current_date_time}</p>
        <p><b>Platform_Health_Check.exe:</b> {exe_version}</p>
        <br/>
        """

        header_row = data[0]

        # ==========================================
        # Get License Status
        # ==========================================
        license_status = ""
        for row in data[1:]:
            logging.info(row)
            license_status = row[3]

        # ==========================================
        # Infrastructure Status
        # ==========================================

        table_html += "<h3>Infrastructure Status</h3>"

        table_html += (
            "<table style='border:1px solid black; border-collapse:collapse;'>"
        )

        infra = data[1]

        infra_fields = [
            ("TEST","STATUS"),
            ("License Status", license_status),
            (header_row[1], infra[1]),   # CSS Status
            (header_row[4], infra[4]),   # DiskSpace
            (header_row[5], infra[5]),   # Dashboard Service
            (header_row[6], infra[6]),   # Imaging Service
            (header_row[7], infra[7]),   # IP
            (header_row[8], infra[8]),   # FQDN
            (header_row[9], infra[9]),   # AIP Console Version
            (header_row[10], infra[10]), # AIP Core Version
            (header_row[11], infra[11]), # MCP Imaging Version
            (header_row[12], infra[12]), # MCP Gatekeeper Version
            (header_row[13], infra[13]), # MCP Imaging Service
            (header_row[14], infra[14])  # MCP Gatekeeper Service
        ]

        for label, value in infra_fields:

            table_html += "<tr>"

            table_html += (
                f"<td style='border:1px solid black; font-weight:bold; padding:5px;'>"
                f"{label}"
                f"</td>"
            )

            if label == "TEST":
                table_html += (
                "<td style='border:1px solid black; padding:5px; font-weight:bold;'>"
                f"{value}"
                "</td>"
            )

            elif str(value).startswith("WARN"):
                table_html += (
                "<td style='border:1px solid black; padding:5px;'>"
                f"<span style='color:#FCD12A;'>{value[:4]}</span>"
                f"<span style='color:black;'>{value[4:]}</span>"
                "</td>"
            )

            elif str(value).startswith("KO") or str(value).startswith("ERR"):
                table_html += (
                    "<td style='border:1px solid black; color:red; padding:5px;'>"
                    f"{value}"
                    "</td>"
                )

            else:
                table_html += (
                    "<td style='border:1px solid black; padding:5px;'>"
                    f"{value}"
                    "</td>"
        )

        table_html += "</table><br/><br/>"

        # ==========================================
        # Application Details Table
        # ==========================================

        table_html += (
        "<table style='border:1px solid black; border-collapse:collapse;'>"
        )

        # Header
        table_html += "<tr>"
        for header in [header_row[0], header_row[2]]:
                table_html += (
                    f"<th style='border:1px solid black; font-weight:bold; padding:5px;'>"
                    f"{header}"
                    f"</th>"
                )
        table_html += "</tr>"

            # Rows
        for row in data[1:]:

            table_html += "<tr>"

            # Application Name (LEFT COLUMN - BOLD)
            table_html += (
                f"<td style='border:1px solid black; padding:5px; font-weight:bold;'>"
                f"{row[0]}"
                f"</td>"
            )

            # Status (RIGHT COLUMN - NORMAL)
            status = str(row[2])

            if status.startswith("WARN"):
                table_html += (
                    "<td style='border:1px solid black; text-align:center; padding:5px;'>"
                    f"<span style='color:#FCD12A;'>WARN</span>"
                    f"<span style='color:black;'>{status[4:]}</span>"
                    "</td>"
                )

            elif status.startswith("KO") or status.startswith("ERR"):
                table_html += (
                    "<td style='border:1px solid black; color:red; text-align:center; padding:5px;'>"
                    f"{status}"
                    "</td>"
                )

            else:
                table_html += (
                    "<td style='border:1px solid black; text-align:center; padding:5px;'>"
                    f"{status}"
                    "</td>"
                )

            table_html += "</tr>"

        table_html += "</table>"

        return table_html
    def add_ko_err_warn_date_and_html_url(self, jira_url, msinfra_ticket_no, data, jira_user_name, jira_password,
                                          shared_html_http_path):

        get_url = f"{jira_url}rest/api/2/issue/{msinfra_ticket_no}"
        url = f"{jira_url}rest/api/2/issue/{msinfra_ticket_no}"
        auth = HTTPBasicAuth(f'{jira_user_name}', f'{jira_password}')

        try:
            ko_date = None
            error_date = None
            warn_date = None

            for i in range(len(data)):
                for j in range(len(data[i])):
                    if i == 0 or j == 0:
                        pass
                    else:
                        current_datetime = datetime.now()  # Get the current time
                        iso8601_format = current_datetime.isoformat()
                        iso8601_format = iso8601_format[:-6] + '000+0000'

                        if 'KO' in data[i][j]:
                            ko_date = iso8601_format
                            # print(ko_date)
                        if 'ERR' in data[i][j]:
                            error_date = iso8601_format
                        if 'WARN' in data[i][j]:
                            warn_date = iso8601_format
                            # fetching the Application list and details.

            data = {"fields": {}}

            response = requests.get(get_url, auth=auth)

            if response.status_code == 200:
                fields = json.loads(response.text)

                report_url = fields['fields']['customfield_10161']
                if report_url is None:
                    data["fields"]["customfield_10161"] = str(shared_html_http_path)

                check_ko_date = fields['fields']['customfield_10140']
                if (ko_date is not None) and (check_ko_date is not None):
                    # Convert string to datetime object
                    ko_date_object = datetime.strptime(ko_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    # Convert string to datetime object
                    ko_date_object_2 = datetime.strptime(check_ko_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    ko_time_difference = ko_date_object - ko_date_object_2
                    ko_hours_difference = ko_time_difference.total_seconds() / 3600
                    # print(ko_hours_difference)
                    if (ko_hours_difference > 24):
                        data["fields"]["customfield_10140"] = str(ko_date)
                if (ko_date is not None) and (check_ko_date is None):
                    data["fields"]["customfield_10140"] = str(ko_date)
                if ko_date is None:
                    data["fields"]["customfield_10140"] = None

                check_err_date = fields['fields']['customfield_10139']
                if (error_date is not None) and (check_err_date is not None):
                    # Convert string to datetime object
                    err_date_object = datetime.strptime(error_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    # Convert string to datetime object
                    err_date_object_2 = datetime.strptime(check_err_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    err_time_difference = err_date_object - err_date_object_2
                    err_hours_difference = err_time_difference.total_seconds() / 3600
                    # print(err_hours_difference)
                    if (err_hours_difference > 24):
                        data["fields"]["customfield_10139"] = str(error_date)
                if (error_date is not None) and (check_err_date is None):
                    data["fields"]["customfield_10139"] = str(error_date)
                if error_date is None:
                    data["fields"]["customfield_10139"] = None

                check_warn_date = fields['fields']['customfield_10141']
                if (warn_date is not None) and (check_warn_date is not None):
                    # Convert string to datetime object
                    warn_date_object = datetime.strptime(warn_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    # Convert string to datetime object
                    warn_date_object_2 = datetime.strptime(check_warn_date, "%Y-%m-%dT%H:%M:%S.%f%z")
                    warn_time_difference = warn_date_object - warn_date_object_2
                    warn_hours_difference = warn_time_difference.total_seconds() / 3600
                    # print(warn_hours_difference)
                    if (warn_hours_difference > 24):
                        data["fields"]["customfield_10141"] = str(warn_date)
                if (warn_date is not None) and (check_warn_date is None):
                    data["fields"]["customfield_10141"] = str(warn_date)
                if warn_date is None:
                    data["fields"]["customfield_10141"] = None

                print(
                    f"Fetching the KO date, ERR Date, WARN Date and HTML Report URL from the ticket -> {msinfra_ticket_no}")
                logging.info(
                    f"Fetching the KO date, ERR Date, WARN Date and HTML Report URL from the ticket -> {msinfra_ticket_no}")
            else:
                print(f"some error has occured while fetching data from the ticket -> {msinfra_ticket_no}")
                logging.error(f"some error has occured while fetching data from the ticket -> {msinfra_ticket_no}")
                print(response.text)
                logging.error(response.text)

            # print(data)
            rsp = requests.put(url, auth=auth, json=data)
            # print(rsp.status_code)
            if rsp.status_code == 204:
                print(
                    f"KO date, ERR Date, WARN Date and HTML Report URL is updated for the ticket -> {msinfra_ticket_no}")
                logging.info(
                    f"KO date, ERR Date, WARN Date and HTML Report URL is updated for the ticket -> {msinfra_ticket_no}")
            else:
                print(
                    f"some error has occured while updating KO date, ERR Date, WARN Date and HTML Report URL to the ticket -> {msinfra_ticket_no}")
                logging.error(
                    f"some error has occured while updating KO date, ERR Date, WARN Date and HTML Report URL to the ticket -> {msinfra_ticket_no}")
                print(rsp.text)
                logging.error(rsp.text)

        except Exception as e:
            logging.error(
                "get_applications_from_console() :- some exception has occured while getting applications from console! \n Please resolve them or contact developers")
            print(
                'some exception has occured while getting applications from console! \n Please resolve them or contact developers')
            logging.error(e)
            print(e)

    # this function gets the MSINFRA Ticket Num for the VM and then update to Platform_Health_Check_Settings.json file.
    def update_msinfra_ticket_no(self, jira_url, jira_username, jira_password, host_name, json_file):

        try:
            VM_Dict = {}
            # initializing auth_type, start_date, end_date and url.
            auth = HTTPBasicAuth(jira_username, jira_password)

            url = f"{jira_url}rest/api/2/search/jql"
            data = {"fields": ["customfield_10142"],
                    "jql": "project = MSINFRA and status in ('VM in Use','ISSUE ON VM')", "maxResults": 1000}

            print(f'Fetching the MSINFRA Ticket Num to Update Platform_Health_Check_Settings.json file.')
            logging.info(f'Fetching the MSINFRA Ticket Num to Update Platform_Health_Check_Settings.json file.')

            # rsp = requests.request(method, url, payload, auth=auth)
            rsp = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, auth=auth)
            # print(rsp.status_code)
            if rsp.status_code == 200:
                res = json.loads(rsp.text)
                # print(type(res))
                # print(res)
                for ticket in res["issues"]:
                    if ticket["fields"]["customfield_10142"] is not None:
                        vm_name = ticket["fields"]["customfield_10142"].strip().lower()
                        msinfra_ticket_no = ticket["key"]
                        VM_Dict[vm_name] = msinfra_ticket_no
                if host_name in VM_Dict.keys():
                    with open(json_file, "r") as a_file:
                        json_object = json.load(a_file)
                    json_object["jira"]["msinfra_ticket_no"] = VM_Dict[host_name]
                    with open(json_file, "w") as a_file:
                        json.dump(json_object, a_file)

                    print(
                        f"Updated the MSINFRA Ticket Num {VM_Dict[host_name]} to Platform_Health_Check_Settings.json file..")
                    logging.error(
                        f"Updated the MSINFRA Ticket Num {VM_Dict[host_name]} to Platform_Health_Check_Settings.json file..")
                    return VM_Dict[host_name]

            else:
                print("Some error has occured while Fetching the MSINFRA Ticket Num from Jira.")
                logging.error("Some error has occured while Fetching the MSINFRA Ticket Num from Jira.")
                print(rsp.text)
                logging.error(rsp.text)

        except Exception as e:
            print(
                'some exception has occured! while Fetching the MSINFRA Ticket Num from Jira. \n Please resolve them or contact developers.')
            logging.error(
                'some exception has occured! while Fetching the MSINFRA Ticket Num from Jira. \n Please resolve them or contact developers.')
            print(e)
            logging.error(e)

    import subprocess
    import logging
    import shutil
    import subprocess

    def ensure_smbclient_installed(self):
        if shutil.which("smbclient"):
            print("? smbclient already installed")
            return True

        print("? smbclient not found. Installing...")

        try:
            # non-interactive install (NO password prompt)
            subprocess.run(
                "sudo -n apt update",
                shell=True,
                check=True
            )

            subprocess.run(
                "sudo -n apt install smbclient -y",
                shell=True,
                check=True
            )

            if not shutil.which("smbclient"):
                raise Exception("Installation failed or sudo permission denied")

            print("? smbclient installed successfully")
            return True

        except subprocess.CalledProcessError:
            raise Exception(
                "? sudo requires password OR no permission. "
                "Run manually: sudo apt install smbclient -y"
            )

    def copy_file_to_vm(self, local_path, remote_path, username, password):
        try:
            # Parse remote path
            unc_path = remote_path.replace("\\", "/")
            parts = unc_path.split("/")

            server = parts[2]
            share = parts[3]
            subfolder = "/".join(parts[4:]) if len(parts) > 4 else ""

            file_name = local_path.split("/")[-1]
            remote_file = f"{subfolder}/{file_name}" if subfolder else file_name

            cmd = [
                "smbclient",
                f"//{server}/{share}",
                f"-U{username}%{password}",
                "-c",
                f"put {local_path} {remote_file}"
            ]

            subprocess.run(cmd, check=True)

            print(f"File copied successfully to {remote_path}")

        except Exception as e:
            print(f"Error: {e}")
            raise

    def disconnect_from_share(self, remote_path):
        """
        No need to actually disconnect on Linux with smbclient.
        This is a placeholder for compatibility.
        """
        logging.info(f"No disconnect required for {remote_path} on Linux.")
        print(f"No disconnect required for {remote_path} on Linux.")

    # def copy_file_to_vm(self, local_path, remote_path, username, password):
    #     try:
    #         # Connect to the network share
    #         self.connect_to_share(remote_path, username, password)
    #
    #         # Copy the file to the remote VM
    #         shutil.copy(local_path, remote_path)
    #
    #         print(f"File copied successfully from {local_path} to {remote_path}")
    #         logging.info(f"File copied successfully from {local_path} to {remote_path}")
    #
    #     except FileNotFoundError:
    #         print(f"Error: The local file {local_path} does not exist.")
    #         logging.error(f"Error: The local file {local_path} does not exist.")
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         logging.error(f"Error: {e}")
    #     finally:
    #         # Disconnect from the network share after copying
    #         self.disconnect_from_share(remote_path)


if __name__ == "__main__":

    try:
        current_directory = os.getcwd()

        with open('/home/gaicuser/platform_health_check/Platform_Health_Check_Settings.json') as f:
            # returns JSON object as a dictionary
            data = json.load(f)

        html_file_path = data['html_file_path']
        css_database = data['css']['database']
        css_user = data['css']['user']
        css_password = data['css']['password']
        css_host = data['css']['host']
        css_port = data['css']['port']
        console_restURL = data['console']['restURL']
        console_user = data['console']['standalone_version']['user']
        console_password = data['console']['standalone_version']['password']
        console_api_key = data['console']['enterprise_version']['api_key']
        warnDays = data['warnDays']
        msinfra_ticket_no = data['jira']['msinfra_ticket_no']
        url = data['jira']['url']
        jira_user_name = 'v.kumar@castsoftware.com'
        jira_password = 'ATATT3xFfGF0pJrAJBFhlOj8u9CjP_DkSYVAbsI2ETj3rOhpKy-r5I9J92-L7QnpbPk4aCW-oDiwtvbLNuGu1sWzjZWx9-4i_FP9CME-PqQjL3HGlBX72TNOKSUYByXpdN4y1TNo6Tuqr5u0MLLiBJDM8vjGjt3Inm4XFOYsLj57nFUwjUTdKGI=BAD020D6'
        exe_version = 'Version-1.0.9.2'

        isExist = os.path.exists("/home/gaicuser/platform_health_check/Platform_Health_Check")
        if not isExist:
            os.makedirs("/home/gaicuser/platform_health_check/Platform_Health_Check")
            # print("The new directory is created!")

        logging.basicConfig(filename="/home/gaicuser/platform_health_check/Platform_Health_Check_Logs.txt",
                            level=logging.INFO, format="%(asctime)s %(message)s", filemode='w')

        # logging.info('-----------------------------------------------------------------------------------------------------------------------------------------------')

        platform_obj = Platform(css_database, css_user, css_password, css_host, css_port, console_restURL, console_user,
                                console_password, None, warnDays, msinfra_ticket_no, url, jira_user_name, jira_password)

        current_date_time = datetime.now()
        platform='Linux'
        cmd = "hostname"
        returned_value = subprocess.check_output(cmd, shell=True)  # returns the exit code in unix
        host_name = returned_value.decode("utf-8").strip().lower()
        
        msinfra_ticket_no = platform_obj.update_msinfra_ticket_no(url, jira_user_name, jira_password, host_name,
                                                                  '/home/gaicuser/platform_health_check/Platform_Health_Check_Settings.json')
        get_api_key(host_name)
        with open('/home/gaicuser/platform_health_check/apikey.txt') as f:
            # returns JSON object as a dictionary
            data = f.read().strip()

        platform_obj = Platform(css_database, css_user, css_password, css_host, css_port, console_restURL, console_user,
                                console_password, data, warnDays, msinfra_ticket_no, url, jira_user_name, jira_password)

        platform_obj.update_console_username_and_password(
            '/home/gaicuser/platform_health_check/Platform_Health_Check_Settings.json')

        platform_obj.update_css_details('/home/gaicuser/platform_health_check/Platform_Health_Check_Settings.json',
                                        host_name)

        table_data = [
            ["Application Name", "CSS Status: Test Connection", "License Key in CSS", "License Key in Console", "DiskSpace",
             "Engineering/Health Dashboard Service", "Imaging Service","IP","FQDN","Imaging Console Version","Aip Core Version","MCP Imaging Version","MCP Gatekeeper Version","MCP Imaging Service","MCP Gatekeeper Service"]]

        applications = platform_obj.get_applications_from_console()
        logging.info(f'App details {applications}')

        console_license_key = platform_obj.get_the_license_from_the_console()
        
        if applications:
            for application, app_guid in applications.items():

                app_local_schema = platform_obj.get_local_schema(app_guid)

                if console_license_key != 0:
                    platform_obj.update_application_license_key(app_local_schema, console_license_key)

                logging.info(
                    '-----------------------------------------------------------------------------------------')

                logging.info(f'checking platform health for {application}.....')
                # Call the function to check the CSS status
                edcmd = "docker inspect -f '{{.State.Status}}' dashboards"
                edreturned_value = subprocess.check_output(edcmd, shell=True)  # returns the exit code in unix
                ed = edreturned_value.decode("utf-8").strip().lower()
                ed="Running" if ed == "running" else ed
                CSS_Status = platform_obj.check_postgres_status()

                CSS_LK_status = platform_obj.check_the_licence_key_in_css(app_local_schema)

                Console_LK_status = platform_obj.check_the_licence_key_in_console()

                DiskSpace_status = platform_obj.check_diskspace()
                imcmd = "docker inspect -f '{{.State.Status}}' server"
                imreturned_value = subprocess.check_output(imcmd, shell=True)  # returns the exit code in unix
                im = imreturned_value.decode("utf-8").strip().lower()
                im="Running" if im == "running" else im
                HDED_status =ed
                ip_file = "stored_ip.txt"

# Get current IP
                ipcmd = "hostname -I | awk '{print $1}'"
                ipreturned_value = subprocess.check_output(ipcmd, shell=True)
                current_ip = ipreturned_value.decode("utf-8").strip()

                # Default message
                ip_status = ""

                if os.path.exists(ip_file):
                    with open(ip_file, "r") as f:
                        old_ip = f.read().strip()

                    if old_ip == current_ip:
                        ip_status = f"IP: {current_ip} (same as previous measure)"
                    else:
                        ip_status = (
                            f"IP changed. Previous IP: {old_ip}, "
                            f"Current IP: {current_ip}. Please check."
                        )

                        # Update the stored IP
                        with open(ip_file, "w") as f:
                            f.write(current_ip)
                else:
                    # First run - store the IP
                    with open(ip_file, "w") as f:
                        f.write(current_ip)

                    ip_status = f"IP: {current_ip}"
                Imaging_is_loaded = im
                fqdn="hostname -f"
                fqdn_returned_value = subprocess.check_output(fqdn, shell=True)
                fqdn = fqdn_returned_value.decode("utf-8").strip().lower()
                imconsoleversion="docker inspect -f '{{.Config.Image}}' server | cut -d: -f2"
                imconsoleversion = subprocess.check_output(imconsoleversion, shell=True)  # returns the exit code in unix
                imconsoleversion = imconsoleversion.decode("utf-8").strip().lower()
                aipcoreversion="docker inspect -f '{{.Config.Image}}' analysis-node | cut -d: -f2 | cut -d_ -f2 | sed 's/^core//'"
                aipcoreversion = subprocess.check_output(aipcoreversion, shell=True)
                aipcoreversion = aipcoreversion.decode("utf-8").strip().lower()
                  # returns the exit code in unix
                import subprocess


                try:
                    container_id = subprocess.check_output(
                        "docker ps -aqf 'name=^mcp-server$'",
                        shell=True
                    ).decode().strip()

                    if not container_id:
                        mcpimagingversion = "NA"
                    else:
                        cmd = "docker inspect -f '{{.Config.Image}}' mcp-server | cut -d: -f2"
                        mcpimagingversion = subprocess.check_output(
                            cmd,
                            shell=True
                        ).decode().strip().lower()

                except Exception:
                    mcpimagingversion = "NA"
                 # returns the exit code in unix
                try:
                    container_id = subprocess.check_output(
                        "docker ps -aqf 'name=^gatekeeper-mcp-server$'",
                        shell=True
                    ).decode().strip()

                    if not container_id:
                        mcpgatekeeperversion = "NA"
                    else:
                        cmd = "docker inspect -f '{{.Config.Image}}' gatekeeper-mcp-server | cut -d: -f2"
                        mcpgatekeeperversion = subprocess.check_output(
                            cmd,
                            shell=True
                        ).decode().strip().lower()

                except Exception:
                    mcpgatekeeperversion = "NA"
    
                try:
                    mcpimagingserviec="docker inspect -f '{{.State.Status}}' mcp-server"
                    mcpimagingserviec = subprocess.check_output(mcpimagingserviec, shell=True)
                    mcpimagingserviec = mcpimagingserviec.decode("utf-8").strip().lower()
                    mcpimagingserviec="Running" if mcpimagingserviec == "running" else mcpimagingserviec
                except subprocess.CalledProcessError:
                    mcpimagingserviec = "NA"
                    # returns the exit code in unix
                try:
                    mcpgatekeeperservice="docker inspect -f '{{.State.Status}}' gatekeeper-mcp-server"
                    mcpgatekeeperservice = subprocess.check_output(mcpgatekeeperservice, shell=True)
                    mcpgatekeeperservice = mcpgatekeeperservice.decode("utf-8").strip().lower()
                    mcpgatekeeperservice="Running" if mcpgatekeeperservice == "running" else mcpgatekeeperservice
                except subprocess.CalledProcessError:
                    mcpgatekeeperservice = "NA"
                table_data.append(
                    [application, CSS_Status, CSS_LK_status, Console_LK_status, DiskSpace_status, HDED_status,
                     Imaging_is_loaded,ip_status,fqdn,imconsoleversion,aipcoreversion,mcpimagingversion,mcpgatekeeperversion,mcpimagingserviec,mcpgatekeeperservice])
# "Imaging Console Version","Aip Core Version","MCP Imaging Version","MCP Gatekeeper Version","MCP Imaging Service","MCP Gatekeeper Service"
        else:
            logging.info(f'checking platform health.....')
            # Call the function to check the CSS status
            CSS_Status = platform_obj.check_postgres_status()

            Console_LK_status = platform_obj.check_the_licence_key_in_console()

            DiskSpace_status = platform_obj.check_diskspace()
            edcmd = "docker inspect -f '{{.State.Status}}' dashboards"
            edreturned_value = subprocess.check_output(edcmd, shell=True)  # returns the exit code in unix
            ed = edreturned_value.decode("utf-8").strip().lower()
            ed="Running" if ed == "running" else ed
            imcmd = "docker inspect -f '{{.State.Status}}' server"
            imreturned_value = subprocess.check_output(imcmd, shell=True)  # returns the exit code in unix
            im = imreturned_value.decode("utf-8").strip().lower()
            im="Running" if im == "running" else im
            HDED_status = ed

            Imaging_is_loaded = im
            ip_file = "stored_ip.txt"

# Get current IP
            ipcmd = "hostname -I | awk '{print $1}'"
            ipreturned_value = subprocess.check_output(ipcmd, shell=True)
            current_ip = ipreturned_value.decode("utf-8").strip()

            # Default message
            ip_status = ""

            if os.path.exists(ip_file):
                with open(ip_file, "r") as f:
                    old_ip = f.read().strip()

                if old_ip == current_ip:
                        ip_status = f"IP: {current_ip} (same as previous measure)"
                else:
                    ip_status = (
                        f"IP changed. Previous IP: {old_ip}, "
                        f"Current IP: {current_ip}. Please check."
                    )

                    # Update the stored IP
                    with open(ip_file, "w") as f:
                        f.write(current_ip)
            else:
                # First run - store the IP
                with open(ip_file, "w") as f:
                    f.write(current_ip)

                ip_status = f"IP: {current_ip}"
            fqdn="hostname -f"
            fqdn_returned_value = subprocess.check_output(fqdn, shell=True)
            fqdn = fqdn_returned_value.decode("utf-8").strip().lower()
            imconsoleversion="docker inspect -f '{{.Config.Image}}' server | cut -d: -f2"
            imconsoleversion = subprocess.check_output(imconsoleversion, shell=True)  # returns the exit code in unix
            imconsoleversion = imconsoleversion.decode("utf-8").strip().lower()
            aipcoreversion="docker inspect -f '{{.Config.Image}}' analysis-node | cut -d: -f2 | cut -d_ -f2 | sed 's/^core//'"
            aipcoreversion = subprocess.check_output(aipcoreversion, shell=True)
            aipcoreversion = aipcoreversion.decode("utf-8").strip().lower()
                # returns the exit code in unix
            import subprocess


            try:
                container_id = subprocess.check_output(
                    "docker ps -aqf 'name=^mcp-server$'",
                    shell=True
                ).decode().strip()

                if not container_id:
                    mcpimagingversion = "NA"
                else:
                    cmd = "docker inspect -f '{{.Config.Image}}' mcp-server | cut -d: -f2"
                    mcpimagingversion = subprocess.check_output(
                        cmd,
                        shell=True
                    ).decode().strip().lower()

            except Exception:
                mcpimagingversion = "NA"
                # returns the exit code in unix
            try:
                container_id = subprocess.check_output(
                    "docker ps -aqf 'name=^gatekeeper-mcp-server$'",
                    shell=True
                ).decode().strip()

                if not container_id:
                    mcpgatekeeperversion = "NA"
                else:
                    cmd = "docker inspect -f '{{.Config.Image}}' gatekeeper-mcp-server | cut -d: -f2"
                    mcpgatekeeperversion = subprocess.check_output(
                        cmd,
                        shell=True
                    ).decode().strip().lower()

            except Exception:
                mcpgatekeeperversion = "NA"

            try:
                mcpimagingserviec="docker inspect -f '{{.State.Status}}' mcp-server"
                mcpimagingserviec = subprocess.check_output(mcpimagingserviec, shell=True)
                mcpimagingserviec = mcpimagingserviec.decode("utf-8").strip().lower()
                mcpimagingserviec="Running" if mcpimagingserviec == "running" else mcpimagingserviec
            except subprocess.CalledProcessError:
                mcpimagingserviec = "NA"
                # returns the exit code in unix
            try:
                mcpgatekeeperservice="docker inspect -f '{{.State.Status}}' gatekeeper-mcp-server"
                mcpgatekeeperservice = subprocess.check_output(mcpgatekeeperservice, shell=True)
                mcpgatekeeperservice = mcpgatekeeperservice.decode("utf-8").strip().lower()
                mcpgatekeeperservice="Running" if mcpgatekeeperservice == "running" else mcpgatekeeperservice
            except subprocess.CalledProcessError:
                mcpgatekeeperservice = "NA"

            table_data.append(
                ['N/A', CSS_Status, 'N/A', Console_LK_status, DiskSpace_status, HDED_status, Imaging_is_loaded,ip_status,fqdn,imconsoleversion,aipcoreversion,mcpimagingversion,mcpgatekeeperversion,mcpimagingserviec,mcpgatekeeperservice])

        logging.info('-----------------------------------------------------------------------------------------')

        # Generate HTML table
        html_table = platform_obj.create_html_table(table_data, platform,host_name, current_date_time, msinfra_ticket_no,
                                                    exe_version)

        # Write HTML to a file
        local_html_path = f'/home/gaicuser/platform_health_check/{msinfra_ticket_no}.html'
        with open(local_html_path, "w") as file:
            file.write(html_table)

        print(f"{msinfra_ticket_no}.html is created and saved at location -> {local_html_path}")
        logging.info(f"{msinfra_ticket_no}.html is created and saved at location -> {local_html_path}")

        shared_html_http_path = html_file_path + str(msinfra_ticket_no) + '.html'
        
        platform_obj.add_ko_err_warn_date_and_html_url(url, msinfra_ticket_no, table_data, jira_user_name, jira_password, shared_html_http_path)
        
        remote_path = r"\\gaicreport.corp.castsoftware.com\wwwgaicreport"
        username = "gaicreportwriter"
        password = "PineApple23!!"

        platform_obj.copy_file_to_vm(local_html_path, remote_path, username, password)

        print(f"Copied {msinfra_ticket_no}.html from {local_html_path} to {remote_path}.")
        logging.info(f"Copied {msinfra_ticket_no}.html from {local_html_path} to {remote_path}.")

    except Exception as e:
        print(
            'some exception has occured! while executing __main__ function.\n Please resolve them or contact developers.')
        logging.error(
            'some exception has occured! while executing __main__ function.\n Please resolve them or contact developers.')
        print(e)
        logging.error(e)