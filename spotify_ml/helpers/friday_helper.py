from datetime import datetime, date
from dateutil.relativedelta import relativedelta, FR

class FridayHelper:
    def __init__(self):
        pass

    def get_most_recent_friday(self):
        if self.it_is_friday():
            return datetime.now()
        else:
            return self.get_last_friday()

    def get_last_friday(self):
        last_friday = datetime.now() + relativedelta(weekday=FR(-1))
        return last_friday
    
    def it_is_friday(self):
        if date.today().weekday() == 4:
            return True
        else:
            return False