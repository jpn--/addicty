import os

NO_DEFAULT = "< NO DEFAULT >"


class IsA:
    """
    Decorator for a class attribute that validates type and provides defaults.
    """

    def __init__(
            self,
            *required_types,
            coerce=False,
            default=NO_DEFAULT,
            doc=None,
            type_descrip=None,
    ):
        """
        Class attribute that validates type and provides defaults

        Parameters
        ----------
        required_types : Tuple[type]
        coerce : bool
        default : Any
        doc : str
        """
        assert len(required_types)
        self.required_types = required_types
        self.coerce = coerce
        self.default = default
        self.type_descrip = type_descrip or ", ".join(
            str(getattr(i, "__name__", i)) for i in required_types
        )
        if doc:
            if "\n" in doc:
                self.__doc__ = doc
            else:
                self.__doc__ = f"{self.type_descrip}: {doc}"

    def __set_name__(self, owner, name):
        # self : IsA
        # owner : parent class that will have `self` as a member
        # name : the name of the attribute that `self` will be
        self.public_name = name
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        # self : IsA
        # obj : instance of parent class that has `self` as a member
        # objtype : class of `obj`
        if obj is None:
            return self
        v = getattr(obj, self.private_name, self.default)
        if v == NO_DEFAULT:
            try:
                f = obj._frozen
            except AttributeError:
                pass
            else:
                if f:
                    raise ValueError(f"{self.public_name!r} is not set and has no default")
        return v

    def __set__(self, obj, value):
        # self : IsA
        # obj : instance of parent class that has `self` as a member
        # value : the new value that is trying to be assigned
        if value is not None and not isinstance(value, self.required_types):
            if self.coerce:
                try:
                    value = self.required_types[0](value)
                except Exception as err:
                    raise AttributeError(f"for {self.public_name!r} can't coerce {type(value)}") from err
            else:
                raise AttributeError(f"can't set {self.public_name!r} with {type(value)}, must be {self.type_descrip}")
        setattr(obj, self.private_name, value)

    def __delete__(self, obj):
        # self : IsA
        # obj : instance of parent class that has `self` as a member
        delattr(obj, self.private_name)

    def validate(self, obj):
        pass

class IsPath(IsA):

    def __init__(
            self,
            *,
            coerce=True,
            default=NO_DEFAULT,
            doc=None,
            create=False,
            exists=False,
            isdir=False,
    ):
        super(IsPath, self).__init__(str, coerce=coerce, default=default, doc=doc)
        self._create = create
        self._exists = exists
        self._isdir = isdir

    def __set__(self, obj, value):
        # self : Path
        # obj : instance of parent class that has `self` as a member
        # value : the new value that is trying to be assigned
        if value is not None and not isinstance(value, self.required_types):
            if self.coerce:
                try:
                    value = self.required_types[0](value)
                except Exception as err:
                    raise AttributeError(f"for {self.public_name} can't coerce {type(value)}") from err
            else:
                raise AttributeError(f"can't set {self.public_name} with {type(value)}")
        if self._exists and not os.path.exists(value):
            raise FileNotFoundError(value)
        if self._isdir and not os.path.isdir(value):
            raise NotADirectoryError(value)
        setattr(obj, self.private_name, value)


class IsSubconfig(IsA):

    def __init__(
            self,
            *required_types,
            coerce=True,
            default=NO_DEFAULT,
            doc=None,
    ):
        super().__init__(dict, *required_types, coerce=coerce, default=default, doc=doc)

    def __set__(self, obj, value):
        # self : Path
        # obj : instance of parent class that has `self` as a member
        # value : the new value that is trying to be assigned
        if value is not None and not isinstance(value, self.required_types[1:]):
            if self.coerce:
                try:
                    value = self.required_types[1](**value)
                except Exception as err:
                    raise AttributeError(f"for {self.public_name} can't coerce {type(value)}") from err
            else:
                raise AttributeError(f"can't set {self.public_name} with {type(value)}")
        setattr(obj, self.private_name, value)


class Configuration:

    def __setattr__(self, name, value):
        if name[0]=="_" and name[-1] != "_":
            super().__setattr__(name, value)
        else:
            if not hasattr(self, name):
                try:
                    frozen = self._frozen
                except AttributeError:
                    pass
                else:
                    if frozen:
                        raise ValueError(f"cannot set attribute {name!r}")
            super().__setattr__(name, value)

    def __init__(self, **kwargs):
        self._frozen = False
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._frozen = True
        for k in dir(self):
            if k[:2] == "__" and k[-2:] == "__":
                continue
            try:
                setattr(self, k, getattr(self, k))
            except:
                raise #TypeError(f"missing required keyword {k!r}")

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


