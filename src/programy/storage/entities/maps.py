"""
Copyright (c) 2016-2019 Keith Sterling http://www.keithsterling.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from programy.storage.entities.store import Store


class MapsReadOnlyStore(Store):

    def __init__(self):
        Store.__init__(self)

    def load_all(self, collector):
        raise NotImplementedError("load_all missing from Maps Store")

    def load(self, collector, name=None):
        raise NotImplementedError("load missing from Maps Store")

    def split_into_fields(self, line):
        splits = line.split(":")
        key = splits[0].upper()
        value = ":".join(splits[1:])
        return [key, value]


class MapsReadWriteStore(MapsReadOnlyStore):

    def __init__(self):
        MapsReadOnlyStore.__init__(self)

    def load_all(self, collector):
        raise NotImplementedError("load_all missing from Maps Store")

    def load(self, collector, name=None):
        raise NotImplementedError("load missing from Maps Store")

    def process_line(self, name, fields, verbose=False):
        if fields:
            return self.add_to_map(name, fields[0], fields[1])
        return False

    def add_to_map(self, name, key, value, overwrite_existing=False):
        raise NotImplementedError("add_to_map missing from Maps Store")

    def remove_from_map(self, name, key):
        raise NotImplementedError("remove_from_map missing from Maps Store")

    def split_into_fields(self, line):
        splits = line.split(":")
        key = splits[0].upper()
        value = ":".join(splits[1:])
        return [key, value]

    def process_line(self, name, fields, verbose=False):
        if fields:
            return self.add_to_map(name, fields[0], fields[1])
        return False
