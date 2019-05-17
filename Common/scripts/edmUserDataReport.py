#!/usr/bin/env python
import ROOT
import os
import sys
import yaml

from DataFormats.FWLite import Events, Handle

from collections import namedtuple

#class UserDataTag(yaml.YAMLObject, namedtuple('UserDataTag', ['type', 'key'])):
class UserDataTag(namedtuple('UserDataTag', ['type', 'key'])):

    yaml_tag = u'!UserDataTag'

    def __str__(self):
        return "{} ({})".format(self.key, self.type.lower())

    #@classmethod
    #def to_yaml(cls, dumper, data):
    #    return dumper.represent_dict({'type': data.type, 'key': data.key})

    def __repr__(self):
        return "%s(type=%r, key=%r)" % (
            self.__class__.__name__, self.type, self.key)


class UserDataReport(object):

    _DATA_TYPES = ('Float', 'Int', 'Cand', 'Data')

    def __init__(self, filename, with_values=False, max_events=10, show_errors=False, show_events=False):

        self._with_values = with_values
        self._max_events = max_events
        self._show_errors = show_errors
        self._show_events = show_events

        ROOT.gROOT.SetBatch()

        self._tfile = ROOT.TFile.Open(filename)

        self._branch_infos = []
        for _b in self._tfile.Get("Events").GetListOfBranches():
            _type_name = _b.GetTypeName()
            _branch_name =_b.GetName()

            if 'edm::Wrapper' in _type_name:
                _type_name = _type_name[13:-1].strip()
                _, _module_name, _, _ = _branch_name.split('_')
            else:
                # ignore non-product branches
                continue

            self._branch_infos.append((_type_name, _module_name, Handle(_type_name)))

        self._report = dict()
        self._values = dict()
        self._processed_events = []

    def _fill_one(self, key, product_entry):
        _user_tag_set = self._report.setdefault(key, set())
        for _dt in self._DATA_TYPES:
            try:
                _user_tags_method = getattr(product_entry, 'user{}Names'.format(_dt))
            except AttributeError:
                # product class has not userData... methods -> skip
                continue
            _user_tags = set([UserDataTag(_dt, _ut) for _ut in _user_tags_method()])
            if _user_tags:
                _user_tag_set.update(_user_tags)

    def _fill_one_values(self, key, product_entry):
        _user_tag_contents = self._values.setdefault(key, dict())
        for _user_tag in self._report[key]:
            _user_value_method = getattr(product_entry, 'user{}'.format(_user_tag.type))
            _user_tag_vals = _user_tag_contents.setdefault(_user_tag, list())
            try:
                _user_tag_vals += [_user_value_method(_user_tag.key)]
            except Exception as e:
                if self._show_errors:
                    print("ERROR: ", e)

    def _fill_all(self, key, product):
        try:
            iter(product)
        except:
            # case: product is not a collection
            self._fill_one(key, product)
            if self._with_values:
                self._fill_one_values(key, product)
        else:
            # case: product is a collection
            if len(product):
                # one entry is enough: all others have the same tags
                try:
                    self._fill_one(key, product[0])
                except TypeError:
                    # collection does not support indexing -> skip
                    pass
                else:
                    if self._with_values:
                        self._fill_one_values(key, product[0])
            #for _product_entry in product:
            #    self._fill_one(key, _product_entry)
            #    break  # one entry is enough: all others have the same tags

    def _fill_report(self):

        events = Events(self._tfile)

        for i_event, event in enumerate(events):

            # break once maximum event number has been processed
            if self._max_events is not None and (i_event >= self._max_events):
                break

            if self._show_events:
                _event_ID = event.eventAuxiliary().id()
                self._processed_events.append(
                    (int(_event_ID.run()), int(_event_ID.luminosityBlock()), int(_event_ID.event()))
                )

            for _bi in self._branch_infos:
                #print("{}".format(_bi[1]))
                try:
                    event.getByLabel(_bi[1], _bi[2])
                    _product = _bi[2].product()
                except RuntimeError:
                    # could not retrieve product -> just skip
                    continue

                self._fill_all(
                    key=_bi[1],
                    product=_product,
                )


    def report(self, as_yaml=False):
        self._fill_report()

        if as_yaml:
            yaml.dump(self._report, sys.stdout)
        else:
            for _branch, _user_data_set in sorted(self._report.items()):
                print("\nBranch '{}':".format(_branch))
                if not _user_data_set:
                    print("    (no user data)")
                    continue
                for _user_data_tag in sorted(_user_data_set, key=lambda udt: (udt.key, udt.type)):
                    if self._with_values:
                        print("    {} = {}".format(_user_data_tag, self._values[_branch].get(_user_data_tag, None)))
                    else:
                        print("    {}".format(_user_data_tag))

        if self._show_events:
            print("")
            for _i_event, _event in enumerate(self._processed_events):
                print(
                    "Processed event #{} with (run, lumi, event) = {}".format(
                        _i_event,
                        _event
                    )
                )



if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser(description="Utility for printing out all available user data keys contained by PAT objects in the given EDM file.")
    p.add_argument('FILE', help="EDM file to scan for PAT objects with user data information", type=str)
    p.add_argument('-n', '--max-events', help="Maximum number of events to loop through when scanning for user data", default=10, type=int)
    p.add_argument('-c', '--with-values', help="Also show examples of the values stored as user data (for all scanned events), not just the keys.", default=False, action='store_true')
    p.add_argument('--show-errors', help="If errors occur, show them (default is to hide errors)", default=False, action='store_true')
    p.add_argument('--show-events', help="Print out run:lumi:event for all processed events", default=False, action='store_true')

    args = p.parse_args()

    if not os.path.exists(args.FILE):
        raise IOError("File '{}' does not exist!".format(args.FILE))

    if (args.max_events > 50):
        _in = raw_input("Unreasonably large --max-events={} (10 is the default). Are you sure? [yN] >".format(args.max_events))
        if _in.strip().lower() not in ("y", "yes"):
            print("Aborted!")
            exit(1)

    udr = UserDataReport(args.FILE, with_values=args.with_values, max_events=args.max_events, show_errors=args.show_errors, show_events=args.show_events)

    udr.report(as_yaml=False)
