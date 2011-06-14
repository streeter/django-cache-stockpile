import hashlib
from stockpile import conf
from django.utils import encoding, translation


def make_key(k, with_locale=True):
    """Generate the full key for ``k``, with a prefix."""
    key = encoding.smart_str('%s:%s' % (conf.PREFIX, k))
    if with_locale:
        key += encoding.smart_str(translation.get_language())
    # memcached keys must be < 250 bytes and w/o whitespace, but it's nice
    # to see the keys when using locmem.
    return hashlib.md5(key).hexdigest()


def make_flush_key(obj):
    """We put flush lists in the flush: namespace."""
    key = obj if isinstance(obj, basestring) else obj.cache_key
    return FLUSH + make_key(key, with_locale=False)


###############################################################################
## Cache Invalidation

class Invalidator(object):

    def invalidate_keys(self, keys):
        """Invalidate all the flush lists named by the list of ``keys``."""
        if not keys:
            return
        flush, flush_keys = self.find_flush_lists(keys)

        if flush:
            cache.set_many(dict((k, None) for k in flush), 5)
        if flush_keys:
            self.clear_flush_lists(flush_keys)

    def cache_objects(self, objects, query_key, query_flush):
        # Add this query to the flush list of each object.  We include
        # query_flush so that other things can be cached against the queryset
        # and still participate in invalidation.
        flush_keys = [o.flush_key() for o in objects]

        flush_lists = collections.defaultdict(set)
        for key in flush_keys:
            flush_lists[key].add(query_flush)
        flush_lists[query_flush].add(query_key)

        # Add each object to the flush lists of its foreign keys.
        for obj in objects:
            obj_flush = obj.flush_key()
            for key in map(flush_key, obj._cache_keys()):
                if key != obj_flush:
                    flush_lists[key].add(obj_flush)
                if FETCH_BY_ID:
                    flush_lists[key].add(byid(obj))
        self.add_to_flush_list(flush_lists)

    def find_flush_lists(self, keys):
        """
        Recursively search for flush lists and objects to invalidate.

        The search starts with the lists in `keys` and expands to any flush
        lists found therein.  Returns ({objects to flush}, {flush keys found}).
        """
        new_keys = keys = set(map(flush_key, keys))
        flush = set(keys)

        # Add other flush keys from the lists, which happens when a parent
        # object includes a foreign key.
        while 1:
            to_flush = self.get_flush_lists(new_keys)
            flush.update(to_flush)
            new_keys = set(k for k in to_flush if k.startswith(FLUSH))
            diff = new_keys.difference(keys)
            if diff:
                keys.update(new_keys)
            else:
                return flush, keys

    def add_to_flush_list(self, mapping):
        """Update flush lists with the {flush_key: [query_key,...]} map."""
        flush_lists = collections.defaultdict(set)
        flush_lists.update(cache.get_many(mapping.keys()))
        for key, list_ in mapping.items():
            if flush_lists[key] is None:
                flush_lists[key] = set(list_)
            else:
                flush_lists[key].update(list_)
        cache.set_many(flush_lists)

    def get_flush_lists(self, keys):
        """Return a set of object keys from the lists in `keys`."""
        return set(e for flush_list in
                   filter(None, cache.get_many(keys).values())
                   for e in flush_list)

    def clear_flush_lists(self, keys):
        """Remove the given keys from the database."""
        cache.delete_many(keys)


class NullInvalidator(Invalidator):
    def add_to_flush_list(self, mapping):
        return


if conf.INVALIDATION_NONE:
    invalidator = NullInvalidator()
else:
    invalidator = Invalidator()
