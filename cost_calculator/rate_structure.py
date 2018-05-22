__author__ = 'Olivier Van Cutsem'

from enum import Enum
from datetime import datetime

# --------------- Schedule structures --------------- #


class ChargeType(Enum):
    FIXED = 'fix',
    DEMAND = 'demand',
    ENERGY = 'energy'


class BlockRate:
    """

    """

    def __init__(self, cost_base, block_rate=None):

        self.__rates = [cost_base]
        self.__thresholds = [0]

        if block_rate is not None:

            (costs, thres) = block_rate
            self.__rates += costs
            self.__thresholds += thres

        self.__thresholds.append(float('inf'))

    def get_rate(self, acc=None):
        """

        :param acc:
        :return:
        """

        if acc is None:
            return self.__rates[0]
        else:
            return [self.__rates[i] for i in range(len(self.__rates)) if self.__thresholds[i] <= acc < self.__thresholds[i+1]][0]


class TouRateSchedule:
    """
    This structure stores the Time-Of-Use rates related to power or energy.
    It is made of a set of methods that manipulate a dict formatted as follow:

    {
        "monthly_label1":
        {
            "months_list": [m1, m2, ...],
            "daily_rates":
            {
                "daily_label1:
                {
                    "days_list": [d1, d2, ...],
                    "rates": list OR float
                },
                ...
            }
        },
        ...
    }

    Remark: a month spans from 1 (january) to 12 (december) ; a day spans from 0 (sunday) to 6 (saturday)

    """

    # TODO: use BlockRate instead of assuming it's a float !

    # Keys used internally
    MONTHLIST_KEY = 'months_list'
    DAILY_RATE_KEY = 'daily_rates'
    DAYSLIST_KEY = 'days_list'
    RATES_KEY = 'rates'

    def __init__(self, rates_schedule):
        """
        Constructor
        :param rates_schedule: a dict formatted as explain in the class description
        """

        # TODO: assert the format is correct

        self.__rates = rates_schedule

    def get_from_timestamp(self, date):
        """
        Return the rate corresponding to a given timestamp
        :param date: a float, the timestamp
        :return: a float, the rate corresponding to the timestamp. None if there is no associated rate
        """

        # Get (m, d, h, m) from date
        if type(date) is float or  type(date) is int:
            date_struct = datetime.fromtimestamp(date)
        else:
            date_struct = date

        m_date = date_struct.month
        d_date = date_struct.weekday()
        h_date = date_struct.hour
        min_date = date_struct.minute

        rates = self.get_rate(m_date, d_date)

        return self.get_rate_in_day(rates, (h_date, min_date))

    def get_daily_rate(self, date):
        """
        Return the daily rates, as a vector sampled at a given period
        :param date: a float, the timestamp
        :return: a list in float
        """

        if type(date) is float or  type(date) is int:
            date_struct = datetime.fromtimestamp(date)
        else:
            date_struct = date

        m_date = date_struct.month
        d_date = date_struct.weekday()

        rate_struct = self.get_rate(m_date, d_date)

        if type(rate_struct) is not list:
            return [rate_struct]
        else:
            return rate_struct

    # --- private
    def get_rate_in_day(self, rate_struct, time_select):
        """
        Return the rate in 'rate_struct' corresponding to instant "time_select"
        :param rate_struct: either a float or an int, representing the rate(s) of the day
        :param time_select: a tuple (h, m) representing the hour and minute to select
        :return: a float, the rate at the selected time
        """

        (h, m) = time_select

        if type(rate_struct) is not list:
            return rate_struct
        else:
            idx = (h + m/60.0 ) * len(rate_struct) / 24.0
            return rate_struct[int(idx)]

    def get_rate(self, m_date, d_date):
        """

        :param self:
        :param m_date:
        :param d_date:
        :return:
        """

        # TODO use map ?

        for m_lab, m_data in self.__rates.items():
            if m_date in m_data[self.MONTHLIST_KEY]:
                for d_lab, d_data in m_data[self.DAILY_RATE_KEY].items():
                    if d_date in d_data[self.DAYSLIST_KEY]:
                        return d_data[self.RATES_KEY]

    @property
    def main_structure(self):
        return self.__rates