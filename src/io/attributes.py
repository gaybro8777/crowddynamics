from timeit import default_timer as timer


class Attr:
    def __init__(self, name, is_resizable=False, is_recordable=False):
        self.name = name
        self.is_resizable = is_resizable
        self.is_recordable = is_recordable

    def __str__(self):
        return "Attr({name}, " \
               "is_resizable={is_resizable}, " \
               "is_recordable={is_recordable})" \
            .format(name=self.name,
                    is_resizable=self.is_resizable,
                    is_recordable=self.is_recordable)


class Attrs(dict):
    def __init__(self, names_or_attrs, save_func=None):
        super().__init__()
        for value in names_or_attrs:
            if isinstance(value, Attr):
                self[value.name] = value
            elif isinstance(value, str):
                self[value] = Attr(value)
            else:
                raise ValueError("Value: {value} of type {type} not valid "
                                 "type for names_or_attrs."
                                 .format(value=value, type=type(value)))
        self.save_func = save_func

    def check_hasattr(self, struct):
        for key, attr in self.items():
            if not hasattr(struct, attr.name):
                raise Warning("struct has no attribute {}".format(attr))
        if len(self) == 0:
            raise ValueError("Struct \"{}\" doesn't contain any of given "
                             "attributes.".format(struct))

    def __iter__(self):
        return iter(self.values())

    def __str__(self):
        return "Attrs(\n\t" + ",\n\t".join((str(i) for i in self)) + "\n)"


class Intervals:
    def __init__(self, interval):
        self.interval = interval
        if self.interval < 0:
            raise ValueError("Interval should be > 0")
        self.prev = timer()

    @property
    def name(self):
        return self.__class__.__name__

    def __call__(self, *args, **kwargs):
        if self.interval == 0:
            return True
        else:
            current = timer()
            diff = current - self.prev
            ret = diff >= self.interval
            if ret:
                self.prev = current
            return ret

    def __str__(self):
        return "{name}({interval})".format(name=self.name,
                                           interval=self.interval)
