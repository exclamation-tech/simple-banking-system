# Import Random & Import sqlite
import random
import sqlite3


class BankingSystem:
    def __init__(self, database):
        # Define DB Connections
        self.conn = sqlite3.connect(f"{database}.s3db")
        self.cur = self.conn.cursor()

        # Temporary variables for use in printing stuff
        self.card_number = None
        self.card_pin = None
        self.card_balance = None
        self.card_id = None

        # Functions
        self.db_init()
        self.print_menu()

    def reset_variables(self):
        self.card_number = None
        self.card_pin = None
        self.card_balance = None
        self.card_id = None

    def db_init(self):
        # Create table card if it doesn't already exist & then commit it
        self.cur.execute("""CREATE TABLE IF NOT EXISTS card(
            id INTEGER PRIMARY KEY,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
        );
        """)
        self.conn.commit()

    def print_menu(self):
        # Print menu
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")

        menu_input = input()  # Take Input

        # Do stuff with input
        if menu_input == "1":
            self.create_card()
        elif menu_input == "2":
            self.log_in()
        elif menu_input == "0":
            print("Bye!")
            exit()
        self.print_menu()

    def create_card(self):
        # Generate numbers
        self.card_number = generate_card_number()
        self.card_pin = generate_pin_number()
        self.card_balance = 0

        # Add numbers to database
        self.cur.execute("INSERT INTO card (number, pin) VALUES (?, ?);", (self.card_number, self.card_pin))
        self.conn.commit()

        # Print output
        print("Your card has been created")
        print("Your card number:")
        print(self.card_number)
        print("Your card PIN:")
        print(self.card_pin)

    def log_in(self):
        # Take input
        card_number = input("Enter your card number:")
        card_pin = input("Enter your PIN:")

        # Query DB
        self.cur.execute("SELECT * FROM card WHERE number = ? AND pin = ?", (card_number, card_pin))
        temp_info = self.cur.fetchone()

        # If found in DB, then login
        if temp_info is not None:
            self.card_id = int(temp_info[0])
            self.card_number = int(temp_info[1])
            self.card_pin = int(temp_info[2])
            self.card_balance = int(temp_info[3])
            print("You have successfully logged in!")
            self.banking_menu()
        else:
            print("Wrong card number or PIN!")

    def banking_menu(self):

        # int menu
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")

        banking_input = input()  # Take Input

        # Do stuff with input
        if banking_input == "1":
            self.balance()
        elif banking_input == "2":
            self.add_income()
        elif banking_input == "3":
            self.do_transfer()
        elif banking_input == "4":
            self.close_account()
            return
        elif banking_input == "5":
            print("You have successfully logged out!")
            return
        elif banking_input == "0":
            print("Bye!")
            exit()
        self.banking_menu()

    def balance(self):
        print(f"Balance: {self.card_balance}")

    def add_income(self):
        # Takes input
        income = int(input("Enter income:"))

        # Update Variable & DB
        self.card_balance += income
        self.cur.execute("UPDATE card SET balance = balance + ? WHERE id = ?", (income, self.card_id))
        self.conn.commit()
        print("Income was added!")
        self.banking_menu()

    def do_transfer(self):
        transfer_to = input("Enter card number:")  # Takes input

        # Queries DB
        self.cur.execute("SELECT * FROM card WHERE number = ?;", (transfer_to,))
        check_number = self.cur.fetchone()

        # Checks card number
        if transfer_to == self.card_number:
            print("You can't transfer money to the same account!")
        elif generate_checksum(transfer_to[:-1]) != transfer_to[-1]:
            print("Probably you made a mistake in the card number. Please try again!")
        elif check_number is None:
            print("Such a card does not exist.")
        else:
            transfer_amount = int(input("Enter how much money you want to transfer:"))
            if int(transfer_amount) > self.card_balance:
                print("Not enough money!")
            else:
                # Does stuff with cards
                self.card_balance -= transfer_amount
                self.cur.execute("UPDATE card SET balance = balance - ? WHERE id = ?", (transfer_amount, self.card_id))
                self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;",
                                 (transfer_amount, transfer_to))
                self.conn.commit()
                print("Success!")

    def close_account(self):
        self.cur.execute("DELETE FROM card WHERE number = ?;", (self.card_number,))
        self.conn.commit()
        self.reset_variables()
        print("The account has been closed!")


# Number generation
def generate_card_number():
    first_15 = f"400000{str(random.randint(0, 999999999)).zfill(9)}"
    return f"{first_15}{generate_checksum(first_15)}"


def generate_checksum(first_num):
    temp_num = list(map(int, first_num))
    sum_temp_num = 0
    for i_ in range(len(temp_num)):
        if i_ % 2 == 0:
            temp_num[i_] *= 2
            if temp_num[i_] > 9:
                temp_num[i_] -= 9
        sum_temp_num += temp_num[i_]
    return str(10 - (sum_temp_num % 10))[-1:]


def generate_pin_number():
    return str(random.randint(0, 9999)).zfill(4)


# Bank Class
bank = BankingSystem("card")

