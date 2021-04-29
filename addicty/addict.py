import copy
import os
import yaml
import logging


class Dict(dict):

    def __init__(__self, *args, **kwargs):
        object.__setattr__(__self, '__parent', kwargs.pop('__parent', None))
        object.__setattr__(__self, '__key', kwargs.pop('__key', None))
        object.__setattr__(__self, '__frozen', False)
        for arg in args:
            if not arg:
                continue
            elif isinstance(arg, dict):
                for key, val in arg.items():
                    __self[key] = __self._hook(val)
            elif isinstance(arg, tuple) and (not isinstance(arg[0], tuple)):
                __self[arg[0]] = __self._hook(arg[1])
            else:
                for key, val in iter(arg):
                    __self[key] = __self._hook(val)

        for key, val in kwargs.items():
            __self[key] = __self._hook(val)

    def __setattr__(self, name, value):
        if hasattr(self.__class__, name):
            raise AttributeError("'Dict' object attribute "
                                 "'{0}' is read-only".format(name))
        else:
            self[name] = value

    def __setitem__(self, name, value):
        isFrozen = (hasattr(self, '__frozen') and
                    object.__getattribute__(self, '__frozen'))
        if isFrozen and name not in super(Dict, self).keys():
                raise KeyError(name)
        super(Dict, self).__setitem__(name, value)
        try:
            p = object.__getattribute__(self, '__parent')
            key = object.__getattribute__(self, '__key')
        except AttributeError:
            p = None
            key = None
        if p is not None:
            p[key] = self
            object.__delattr__(self, '__parent')
            object.__delattr__(self, '__key')

    def __add__(self, other):
        if not self.keys():
            return other
        else:
            self_type = type(self).__name__
            other_type = type(other).__name__
            msg = "unsupported operand type(s) for +: '{}' and '{}'"
            raise TypeError(msg.format(self_type, other_type))

    @classmethod
    def _hook(cls, item):
        if isinstance(item, dict):
            return cls(item)
        elif isinstance(item, (list, tuple)):
            try:
                return type(item)(cls._hook(elem) for elem in item)
            except TypeError:
                # some subclasses don't implement a constructor that
                # accepts a generator, e.g. namedtuple
                return type(item)(*(cls._hook(elem) for elem in item))
        return item

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __missing__(self, name):
        if object.__getattribute__(self, '__frozen'):
            raise KeyError(name)
        return self.__class__(__parent=self, __key=name)

    def __delattr__(self, name):
        del self[name]

    def to_dict(self):
        base = {}
        for key, value in self.items():
            if isinstance(value, type(self)):
                base[key] = value.to_dict()
            elif isinstance(value, (list, tuple)):
                try:
                    base[key] = type(value)(
                        item.to_dict() if isinstance(item, type(self)) else
                        item for item in value)
                except TypeError:
                    # some subclasses don't implement a constructor that
                    # accepts a generator, e.g. namedtuple
                    base[key] = type(value)(*(
                        item.to_dict() if isinstance(item, type(self)) else
                        item for item in value))
            else:
                base[key] = value
        return base

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)

    def __deepcopy__(self, memo):
        other = self.__class__()
        memo[id(self)] = other
        for key, value in self.items():
            other[copy.deepcopy(key, memo)] = copy.deepcopy(value, memo)
        return other

    def update(self, *args, **kwargs):
        other = {}
        if args:
            if len(args) > 1:
                raise TypeError()
            other.update(args[0])
        other.update(kwargs)
        for k, v in other.items():
            if ((k not in self) or
                (not isinstance(self[k], dict)) or
                (not isinstance(v, dict))):
                self[k] = v
            else:
                self[k].update(v)

    def __getnewargs__(self):
        return tuple(self.items())

    def __getstate__(self):
        state = self.to_dict()
        isFrozen = (hasattr(self, '__frozen') and
                    object.__getattribute__(self, '__frozen'))
        state['__addict__frozen__'] = isFrozen
        return state

    def __setstate__(self, state):
        shouldFreeze = state.pop('__addict__frozen__', False)
        self.update(state)
        self.freeze(shouldFreeze)

    def __or__(self, other):
        if not isinstance(other, (Dict, dict)):
            return NotImplemented
        new = Dict(self)
        new.update(other)
        return new

    def __ror__(self, other):
        if not isinstance(other, (Dict, dict)):
            return NotImplemented
        new = Dict(other)
        new.update(self)
        return new

    def __ior__(self, other):
        self.update(other)
        return self

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def freeze(self, shouldFreeze=True):
        object.__setattr__(self, '__frozen', shouldFreeze)
        for key, val in self.items():
            if isinstance(val, Dict):
                val.freeze(shouldFreeze)

    def unfreeze(self):
        self.freeze(False)

    @classmethod
    def load(
            cls,
            filename,
            logger=None,
            encoding='utf-8',
            Loader=yaml.SafeLoader,
            freeze=True,
    ):
        """
        Load a Dict from a YAML file.

        Parameters
        ----------
        filename : str or File-like
            A filename of a yaml file to load, or the content of a yaml file
            loaded as a string, or a file-like object from which to load the
            yaml content.
        logger : logging.Logger, optional
            A logger for error messages.
        encoding : str, default 'utf-8'
            The encoding of the file to be loaded (if any).
        Loader : yaml.Loader, optional
            Defaults to the SafeLoader.
        freeze : bool, default True
            Whether to freeze this Dict after loading.

        Returns
        -------
        Dict
        """
        from .yaml_checker import yaml_check
        if isinstance(filename, str) and '\n' not in filename:
            if not os.path.exists(filename):
                raise FileNotFoundError(filename)
            if logger is not None:
                yaml_check(filename, logger=logger)
            with open(filename, 'r', encoding=encoding) as f:
                try:
                    result = cls(yaml.load(f, Loader=Loader))
                except Exception as err:
                    from io import StringIO
                    buffer = StringIO()
                    err_logger = lambda x: buffer.write(f"{x}\n")
                    yaml_check(filename, logger=err_logger)
                    raise ValueError(buffer.getvalue()) from err
        else:
            result = cls(yaml.load(filename, Loader=Loader))
        if freeze:
            result.freeze(True)
        return result

    def dump(self, *args, **kwargs):
        if 'default_flow_style' not in kwargs:
            kwargs['default_flow_style'] = False
        if 'indent' not in kwargs:
            kwargs['indent'] = 2
        if len(args) and isinstance(args[0], str):
            if os.path.exists(args[0]):
                raise FileExistsError(args[0])
            dirname = os.path.dirname(args[0])
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(args[0], 'w') as f:
                yaml.safe_dump(self.to_dict(), f, **kwargs)
        else:
            return yaml.safe_dump(self.to_dict(), **kwargs)

    def __repr__(self):
        return self.dump(
            explicit_start=True,
            explicit_end=True,
        ).rstrip("\n")
