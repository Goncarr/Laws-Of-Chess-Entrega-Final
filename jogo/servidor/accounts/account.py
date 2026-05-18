from datetime import datetime
import json
import os

class Account:
    file_path = "accounts/accounts.json"

    def __init__(self):
        self._file_exists()

    #-------------------------JSON Functions-------------------------#

    def _file_exists(self):
        """
        Method that verifies if the file_path exists

        """
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                json.dump({}, file)


    def _load(self):
        """
        Method that gets the contents of the file_path
        :return: Returns the contents of the file_path
        """
        with open(self.file_path, "r") as file:
            return json.load(file)


    def _save(self, data):
        """
        Methods the overwrites the current file_path's content with data
        :param data: Data to be stored in the file through writing "w"
        """
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)


    def get_account(self, name):
        """
        Method that checks if a name of an account is in the file_path and, if it is,
        returns it
        :param name: Name to search through the file_path
        :return: Returns the account's name
        """
        accounts = self._load()

        if name not in accounts:
            return False

        return accounts[name]

    #---------------Non-implemented CRUD Functions---------------#
    def create_account(self, name):
        """
        This method verifies if the name already exists. If not, creates the account.
        """
        accounts = self._load()

        if name in accounts:
            return False

        accounts[name] = {
            "name": name,
            "wins": 0,
            "created_at": datetime.now().isoformat()
        }

        self._save(accounts)
        return True

    def update_account(self, old_name, new_name):
        """
        Method that replaces the old_name of an account with a new_name
        :param old_name: Original account name
        :param new_name: New account name
        :return: Returns True or False depending if the old_name was in the file or not
        """
        accounts = self._load()

        if old_name not in accounts:
            return False

        accounts[new_name] = accounts[old_name]
        accounts[new_name]["name"] = new_name
        del[accounts[old_name]]
        self._save(accounts)
        return True

    def delete_account(self, name):
        """
        Method that deletes the account which name = name (argument)
        :param name: Name to search through the file_path
        :return: Returns True or False depending on if it deleted the account or not
        """
        accounts = self._load()

        if name not in accounts:
            return False

        del accounts[name]
        self._save(accounts)
        return True

    def list_accounts(self):
        """
        Method that returns all the accounts in file_path
        :return: Returns all the accounts in file_path
        """
        accounts = self._load()
        return list(accounts.keys())

    def add_win(self, name):
        """
        This method adds a win to the account's win amount (TO BE DEVELOPED)
        :param name: Name of the winner of a match
        :return: Returns True or False depending if the account exists or not
        """
        accounts = self._load()

        if name not in accounts:
            return False

        accounts[name]["wins"] += 1
        self._save(accounts)
        return True

