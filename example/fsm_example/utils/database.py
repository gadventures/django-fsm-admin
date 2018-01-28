from django.db import connection
from django.utils.decorators import ContextDecorator

from .common import UniquelyCustomizedEnum


class ModelEnum(UniquelyCustomizedEnum):
    pass


class QueryCountMe(ContextDecorator):

    def __init__(self, *args, **kwargs):
        self.label = kwargs["label"] if "label" in kwargs else ""

    def __call__(self, *args, **kwargs):
        if not self.label:
            self.label = args[0].__name__ if args else self.label

        return super(QueryCountMe, self).__call__(*args, **kwargs)

    def __enter__(self):
        self.initial_query_count = len(connection.queries)
        return self

    def __exit__(self, *args):
        count = len(connection.queries) - self.initial_query_count
        total_time = reduce(lambda a, b: a + float(b['time']), connection.queries[-count:], 0.0)

        print("For {} {} queries hit".format(self.label, count))
        print("Total time taken {}".format(total_time))

        return False
