import threading
import time

import pywebio
import pywebio.exceptions
import redis
from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import put_input, pin_wait_change, pin
from pywebio.session import register_thread
import envs

"""
Redis statements
"""
r = redis.StrictRedis(
    host=envs.REDIS_HOST,
    port=envs.REDIS_PORT,
    password=envs.REDIS_PASSWORD,
    decode_responses=True,
    db=0,
)


def prog():
    """
    function that display all information to frontend
    """
    put_markdown(
        " Input your referral link to enjoy free using airtable"
    )
    put_input(
        "referral_link",
        label="Input your referral link",
        placeholder="referral link",
        type="text",
        value=r.get('referral_link'),
        help_text="* This field should not be empty"
    )
    put_input(
        "required_accounts",
        label="Input required accounts",
        placeholder="Number of accounts",
        type="number",
        value=r.get('required_accounts'),
        help_text="* This field should not be empty"
    )
    put_table(
        [
            [
                "Accounts created:",
                put_input("numbers_of_account", value="True", readonly=True),
            ],
            ["Tasks in the queue:", put_input("bot_is_active", value="True", readonly=True)],
            ["Bad attempts:", put_input("bad_attempts", value="True", readonly=True)],
            [
                "Initialise operation:",
                put_buttons(["Run"], onclick=lambda _: [store_data(), progress_bar()])
            ],
            ["Stop operation:", put_buttons(["Stop"], onclick=lambda _: stop_worker())],
        ]
    )
    x = threading.Thread(target=update_numbers_of_account, daemon=True)
    register_thread(x)
    x.start()
    check_data()
    while True:
        changed = pin_wait_change("Run", "Stop")


def check_data():
    """
    function to check valid data in other functions
    """
    if r.get('run') == '1' and r.get('required_accounts') and r.get('referral_link') is not None:
        progress_bar()

    if pin.required_accounts == '':
        popup('Warning!', ' You must enter integer!', size=PopupSize.SMALL)


def start():
    """
    function that start eb app
    """
    while True:
        pass_ = input("Enter password:", type='password')
        if pass_ != '123':
            popup('You have entered the wrong password!')
        else:
            break
    prog()


def store_data():
    """
    function to store data in redis
    """
    try:
        referral_link = pin.referral_link
        required_accounts = pin.required_accounts
        r.set("referral_link", referral_link)
        r.set("numbers_of_account", 0)
        r.set("run", 1)
        r.set('bad_attempts', 0)
        r.set('task_progress', 1)
    except:
        pywebio.exceptions.SessionNotFoundException('Sorry you closed the page')
        popup("You already pressed 'Run' button")

    try:
        if pin.required_accounts > 0:
            r.set("required_accounts", required_accounts)
        else:
            popup('The number must be positive')
    except Exception:
        pywebio.exceptions.SessionNotFoundException('Sorry you closed the page')
        popup('Enter the integer on required accounts field')
        time.sleep(3)


def stop_worker():
    """
    function to stop whole app
    """
    r.set("run", 0)
    r.delete('queue_worker')
    r.set('numbers_of_account', 0)
    popup('You have pressed the Stop button', ' The process has stopped', size=PopupSize.SMALL)
    r.delete('required_accounts')
    r.delete("bad_attempts")
    pin.required_accounts = 0
    pin.bad_attempts = 0
    remove('bar')


def update_numbers_of_account():
    """
    function that update numbers of accounts
    """
    while True:
        try:
            numbers_of_account = r.get("numbers_of_account")
            bad_attempts = r.get("bad_attempts")
            queue_worker = r.llen("queue_worker")
            pin.bad_attempts = bad_attempts or 0
            pin.bot_is_active = queue_worker
            pin.numbers_of_account = numbers_of_account or 0

            task_progress = int(r.get("task_progress"))
            if task_progress == 0:
                r.incr("task_progress", 1)

            elif task_progress == 10:
                time.sleep(1)
                r.set('task_progress', 0)
            rec_acc = int(r.get('required_accounts'))
            num_acc = int(r.get('numbers_of_account'))

            set_processbar('tasks_completed', num_acc / rec_acc)
            set_processbar('task_progress', task_progress / 10)

            if r.get('required_accounts') == r.get("numbers_of_account"):
                r.set('task_progress', 10)
                time.sleep(1)
                stop_worker_without_popup()
                time.sleep(2)
                popup('Congratulations!', ' All tasks completed!', size=PopupSize.SMALL)
                time.sleep(1)


        except:
            pywebio.exceptions.SessionNotFoundException('Sorry you closed the page')
        time.sleep(1)


def stop_worker_without_popup():
    """
    function to stop whole app without popup
    """
    r.set("run", 0)
    r.delete('queue_worker')
    r.delete('required_accounts')
    pin.required_accounts = 0
    remove('bar')


@use_scope('bar', clear=True)
def progress_bar():
    """
    function that display progressbars
    """
    if r.get('run') == '1' and r.get('required_accounts') is None:
        return
    put_text("Progress of performance single task")
    put_processbar('task_progress', label="progress of task's implementation")

    put_text('Completed tasks')
    put_processbar('tasks_completed', label='quantity of completed tasks')

    x = threading.Thread(target=update_numbers_of_account, daemon=True)
    register_thread(x)
    x.start()



if __name__ == "__main__":
    start_server(start, port=36551, debug=True)
