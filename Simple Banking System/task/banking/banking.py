# Write your code here
import random
import sqlite3


class BancoDeDados:
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()

    def __init__(self):
        f = open("card.s3db", "a")
        f.close()
        self.create_table()

    def salva_conta(self, banco, account):
        self.c.execute('INSERT INTO card (ID, NUMBER, PIN) VALUES (?, ?, ?)',
                       (account.id_, account.card_number, account.pin))
        self.conn.commit()

    def conta_existe(self, card_transfer):
        cursor = self.c.execute(f'select 1 from card where number="{card_transfer}"')
        conta_existe = cursor.fetchone()
        if conta_existe is None:
            return False
        else:
            return True

    def create_table(self):
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS "card" ("ID" INTEGER, "NUMBER" TEXT, "PIN" TEXT, "BALANCE" INTEGER DEFAULT 0)''')
        self.conn.commit()

    def get_balance(self, card_number):
        cursor = self.c.execute(f'select balance from card where number="{card_number}"')
        balance = cursor.fetchone()
        if balance is None:
            return 0
        return balance[0]

    def transfere(self, card_number, card_transfer, money):
        cursor = self.c.execute(f'select balance from card where number="{card_number}"')
        dinheiro = cursor.fetchone()
        total_balance = dinheiro[0] - money
        cursor = self.c.execute(f'update card set balance = {total_balance} where number = {card_number}')
        cursor = self.c.execute(f'select balance from card where number="{card_transfer}"')
        dinheiro = cursor.fetchone()
        total_balance = money + dinheiro[0]
        cursor = self.c.execute(f'update card set balance = {total_balance} where number = {card_transfer}')
        self.conn.commit()

    def get_contas(self):
        cursor = self.c.execute('select * from card')
        contas = cursor.fetchall()
        listaContas = []
        for conta in contas:
            account = Account(conta[1], conta[2], conta[0], conta[3])
            listaContas.append(account)
        return listaContas

    def get_last_id(self):
        cursor = self.c.execute('select max(ID) from card')
        last_id = cursor.fetchone()
        return last_id[0]

    def deposita(self, card_number, money):
        cursor = self.c.execute(f'select balance from card where number="{card_number}"')
        dinheiro = cursor.fetchone()
        total_balance = money + dinheiro[0]
        cursor = self.c.execute(f'update card set balance = {total_balance} where number = {card_number}')
        self.conn.commit()

    def deleta_conta(self, card_number):
        self.c.execute(f'delete from card where number={card_number}')
        self.conn.commit()


class Bank:
    accounts = dict()
    last_id = 0
    inn = "400000"

    def __init__(self, banco):
        self.accounts = BancoDeDados.get_contas(banco)
        self.last_id = BancoDeDados.get_last_id(banco)

    def create_account(self, banco):
        self.last_id = BancoDeDados.get_last_id(banco)
        if BancoDeDados.get_last_id(banco) is None:
            self.last_id = 0
        random.seed(self.last_id + 1)
        card_final = str(random.randint(0, 999999999))
        if len(card_final) <= 12:
            card_final = card_final[:0] + "0" + card_final[0:]
        card_number = self.inn + card_final
        valido = self.verifica_luhn(card_number)
        while not valido:
            card_final = str(random.randint(0, 999999999))
            if len(card_final) <= 12:
                card_final = card_final[:0] + "0" + card_final[0:]
            card_number = self.inn + card_final
            valido = self.verifica_luhn(card_number)

        random.seed(self.last_id + 1)
        _pin = str(random.randint(0, 9999))
        if len(_pin) < 4:
            _pin = _pin[:0] + "0" + _pin[0:]
        pin = _pin
        account = Account(card_number, pin, self.last_id + 1, 0)
        banco.salva_conta(self, account)
        print("Your card has been created")
        print(f"Your card number:\n{account.card_number}\nYour card PIN:\n{account.pin}\n")

    def log_in_account(self, banco):
        print("Enter your card number:")
        card = str(input())
        print("Enter your PIN:")
        pin = str(input())
        for account in BancoDeDados.get_contas(banco):
            if account.card_number == card:
                if account.pin == pin:
                    print("You have successfully logged in!")
                    Account.menu(account)
                    break
                else:
                    print("Wrong card number or PIN!")
                    break
        else:
            print("Wrong card number or PIN!")

    def verifica_luhn(self, card_number):
        luhn = [int(char) for char in str(card_number)]
        for i, num in enumerate(luhn):
            if (i + 1) % 2 == 0:
                continue
            temp = num * 2
            luhn[i] = temp if temp < 10 else temp - 9
        return sum(luhn) % 10 == 0


class Account:
    id_ = 0
    balance = 0
    card_number = None
    pin = None

    def __init__(self, card_number, pin, id_, balance):
        self.id_ = id_
        self.card_number = card_number
        self.pin = pin
        self.balance = balance

    def transfer(self):
        print("Transfer\nEnter card number:")
        card = int(input())
        card_transfer = card
        if not Bank.verifica_luhn(Bank, card_transfer):
            print("Probably you made mistake in card number. Please try again!")
        elif not BancoDeDados.conta_existe(BancoDeDados, card_transfer):
            print("Such a card does not exist.\n")
        else:
            print("Enter how much money you want to transfer:")
            money = int(input())
            if BancoDeDados.get_balance(BancoDeDados, self.card_number) < money:
                print("Not enough money!")
            else:
                BancoDeDados.transfere(BancoDeDados, self.card_number, card, money)
                print("Success!")

    def add_balance(self):
        print("Enter income:")
        money = int(input())
        BancoDeDados.deposita(BancoDeDados, self.card_number, money)
        print("Income was added!")

    def fecha_conta(self):
        BancoDeDados.deleta_conta(BancoDeDados, self.card_number)
        print("The account has been closed!")

    def menu(self):
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")
        acao = int(input())
        while acao != 0:
            if acao == 1:
                print("Balance: " + str(BancoDeDados.get_balance(BancoDeDados, self.card_number)) + "\n ")
            elif acao == 2:
                Account.add_balance(self)
            elif acao == 3:
                Account.transfer(self)
            elif acao == 4:
                Account.fecha_conta(self)
                menu()
            elif acao == 5:
                print("You have successfully logged out!\n")
                break
            elif acao == 0:
                print("Bye")
                BancoDeDados.conn.close()
                break
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            acao = int(input())
        exit()


def menu():
    banco = BancoDeDados()
    bank = Bank(banco)
    while 1 == 1:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        acao = int(input())
        if acao == 1:
            Bank.create_account(bank, banco)
        elif acao == 2:
            Bank.log_in_account(bank, banco)
        elif acao == 3:
            print(BancoDeDados.get_contas(banco))
        elif acao == 0:
            print("Bye")
            banco.conn.close()
            exit()


menu()
