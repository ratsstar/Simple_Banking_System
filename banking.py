# constants
import sqlite3
import random
BIN = '400000'
# create a connection. creates a database if it doesnt exist
conn = sqlite3.connect('card.s3db')
# create a cursor
cur = conn.cursor()
# create a table in database to store info on cards in case it doesnt exist
cur.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
# commit DB changes (table created) after executing the query above
conn.commit()
# variables
cur.execute('SELECT COUNT(*) FROM card;')  # returns number of cards issued (info stored in card DB)
n = cur.fetchone()[0]  # retrieves data after executing the SELECT statement (tuple type)
account_id = 1000000000 - n
input_id = n


# define function to calculate Luch digit
def luch_calc(acc_id_list):
    # multiply odd digits by 2
    i = 0
    while i < len(acc_id_list):
        acc_id_list[i] = acc_id_list[i] * 2
        i += 2
    # subtract 9 from numbers over 9
    i = 0
    while i < len(acc_id_list):
        if acc_id_list[i] > 9:
            acc_id_list[i] = acc_id_list[i] - 9
        i += 1
    # find sum of digits
    s = 0
    i = 0
    while i < len(acc_id_list):
        s += acc_id_list[i]
        i += 1
    # calculate Luch digit
    reminder = s % 10
    if reminder == 0:
        luch_digit = 0
    else:
        luch_digit = 10 - reminder
    return luch_digit


# define function to convert first 15 symbols of card number to list of integers
def conv_to_intlist(acc_to_verify):
    acc_id_list = list(map(int, acc_to_verify))
    return acc_id_list


while True:
    customer_choice = int(input("1. Create an account\n"
                                "2. Log into account\n"
                                "0. Exit\n"))
    if customer_choice == 1:
        input_id += 1
        account_id -= 1
        # calc Luch digit
        # create list of account_id digits
        acc_to_verify = (BIN + str(account_id))
        acc_id_list = conv_to_intlist(acc_to_verify)
        checksum = luch_calc(acc_id_list)
        # define card number 
        card_number = BIN + str(account_id) + str(checksum)
        # text datatype was assigned to pin attribute in card table
        # pins starting with zero are not generated since in such case first symbol in pin is dropped when committing to DB
        pin = str(random.randrange(1, 10, 1)) + str(random.randrange(0, 10, 1)) + str(random.randrange(0, 10, 1)) + str(random.randrange(0, 10, 1))
        # append DB
        cur.execute('INSERT INTO card (id, number, pin) VALUES ({}, {},{})'.format(input_id, card_number, pin))
        conn.commit()
        # print the required msg to customer
        print(("Your card has been created\n"
               "Your card number:\n"
               "{}\n"
               "Your card PIN:\n"
               "{}").format(card_number, pin))
    # If the customer chooses ‘Log into account’, they are asked to enter their card information
    elif customer_choice == 2:
        input_card_n = input('Enter your card number:')
        input_pin = input('Enter your PIN:')
        try:
            cur.execute('SELECT pin FROM card where number = {};'.format(input_card_n))
            r = cur.fetchone()[0]
            # if card number and pin entered are right and match each other ...
            if r == input_pin:
                # ... 'You have successfully logged in!' is printed ...
                print('You have successfully logged in!')
                # ... and the program offers menu to chose further actions
                customer_choice_2 = int(input("1. Balance\n"
                                              "2. Add income\n"
                                              "3. Do transfer\n"
                                              "4. Close account\n"
                                              "5. Log out\n"
                                              "0. Exit\n"))
                # the same menu is offered to a customer each time they chose 1, 2 and 3 options
                while customer_choice_2 in range(1, 4):
                    cur.execute('SELECT balance FROM card WHERE number = {};'.format(input_card_n))
                    b = cur.fetchone()[0]
                    if customer_choice_2 == 1:
                        print('Balance: {}'.format(b))
                    elif customer_choice_2 == 2:
                        input_inc = int(input('Enter income:'))
                        res_bal = b + input_inc
                        cur.execute('UPDATE card SET balance = {} WHERE number = {};'.format(res_bal, input_card_n))
                        conn.commit()
                        print('Income was added!')
                    elif customer_choice_2 == 3:
                        input_tr_account = input('Transfer\nEnter card number:')
                        if input_tr_account == input_card_n:
                            print('You can\'t transfer money to the same account!')
                        # Luch check
                        acc_to_verify = input_tr_account[0:15]
                        acc_id_list = conv_to_intlist(acc_to_verify)
                        Luch_digit = luch_calc(acc_id_list)
                        if int(input_tr_account[15]) != Luch_digit:
                            print('Probably you made a mistake in the card number. Please try again!')
                        # check if card entered is available in DB
                        cur.execute('SELECT COUNT(number) FROM card WHERE NUMBER = {};'.format(input_tr_account))
                        p = cur.fetchone()[0]
                        if (p == 0) and (int(input_tr_account[15]) == Luch_digit):
                            print('Such a card does not exist.')
                        if (int(input_tr_account[15]) == Luch_digit) and (p > 0) and (input_tr_account != input_card_n):
                            input_tr_amount = int(input('Enter how much money you want to transfer:'))
                            cur.execute('SELECT balance FROM card where number = {};'.format(input_card_n))
                            r1 = cur.fetchone()[0]
                            # check if balance is enough to transfer
                            if r1 >= input_tr_amount:
                                cur.execute('SELECT balance FROM card where number = {};'.format(input_tr_account))
                                r2 = cur.fetchone()[0]
                                new_r1_b = r1 - input_tr_amount
                                new_r2_b = r2 + input_tr_amount
                                cur.execute('UPDATE card SET balance = {} WHERE number = {};'.format(new_r1_b, input_card_n))
                                cur.execute('UPDATE card SET balance = {} WHERE number = {};'.format(new_r2_b, input_tr_account))
                                conn.commit()
                                print('Success!')
                            else:
                                print('Not enough money!')

                    customer_choice_2 = int(input("1. Balance\n"
                                                  "2. Add income\n"
                                                  "3. Do transfer\n"
                                                  "4. Close account\n"
                                                  "5. Log out\n"
                                                  "0. Exit\n"))
                else:
                    # when customer chooses 2 '2. Log out' the iteration ends and the customer is transferred to outer loop
                    if customer_choice_2 == 4:
                        cur.execute('UPDATE card SET number = NULL, pin = NULL, balance = 0 WHERE number = {};'.format(input_card_n))
                        conn.commit()
                        print('The account has been closed!')
                    elif customer_choice_2 == 5:
                        print('You have successfully logged out!')
                    # when customer chooses 0 '0. Exit', the program exits the outer loop
                    elif customer_choice_2 == 0:
                        print('Bye!')
                        conn.close()
                        break
                    else:
                        print('error')
            # if card number or pin entered are wrong, message 'Wrong card number or PIN!' is printed
            else:
                print('Wrong card number or PIN!')
        # if card number or pin entered give KeyError, message 'Wrong card number or PIN!' is printed
        except TypeError:
            print('Wrong card number or PIN!')
        except sqlite3.OperationalError:
            print('Wrong card number or PIN!')
    elif customer_choice == 0:
        print('Bye!')
        conn.close()
        break
