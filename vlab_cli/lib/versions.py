# -*- coding: UTF-8 -*-
"""
This module make obtaining and comparing version strings easy!
"""
import glob
import os
from collections import namedtuple
from pkg_resources import get_distribution, DistributionNotFound


class Version(object):
    """Implements comparison operators for common version strings
    Only versions strings upwards of 4 digits and consisting only of numbers is
    supported. Version strings breakdown into ``major``, ``minor``, ``patch``,
    and ``build``.
    Example::
        >>> version_as_string = '1.2.3'
        >>> version = Version(name='myPackage', version=version_as_string)
        >>> version.major
        1
        >>> version.patch
        3
        >>> type(version.minor)
        <type 'int'>
        >>> type(version.build)
        <type 'NoneType'>
    Comparing Versions::
        >>> v1 = Version(name='myPackage', version='1.2.3')
        >>> v2 = Version(name='newPackage', version='1.4.0')
        >>> v1 < v2
        True
        >>> v2 >= v1
        True
        >>> v2 == v1
        False
    The Version object also support comparison of string versions::
        >>> v1 = Version(name='foo', version='4.5')
        >>> v1 > '5.0'
        False
    It's worth noting, more specific versions (that would otherwise be equal),
    are considered greater::
        >>> v1 = Version(name='bar', version='1.2.0')
        >>> v1 > '1.2'
        True
    This is because a version without a value is None, and zero is greater than None in Python::
       >>> 0 > None
       True
    """

    # for semantic versioning http://semver.org
    _semver = ('major', 'minor', 'patch', 'build')

    def __init__(self, version, name):
        self._name = name
        if not isinstance(version, str):
            msg = 'Version object can only be created from string, supplied %s, %s' % (version, type(version))
            raise TypeError(msg)
        else:
            version_breakdown = version.split('.')
            if len(version_breakdown) < 2:
                # Pretty much every version number is dot-delimited so we should
                # at least two items, must not be a version
                raise ValueError("Unexpected value for version, %s" % version)
            else:
                for idx, semantic_version in enumerate(self._semver):
                    try:
                        number = int(version_breakdown[idx])
                        setattr(self, '_%s' % semantic_version, number)
                    except ValueError:
                        msg = 'Version only support integer values, failed to cast %s for %s' % (semantic_version, version)
                        raise ValueError(msg)
                    except IndexError:
                        if idx == 3 or idx == 2:
                            # some versions only consist of major.monior, like google chrome
                            setattr(self, '_%s' % semantic_version, -1)
                        else:
                            # re-raise the error for debugging
                            raise

        self._version = version

    @property
    def name(self):
        return self._name

    @property
    def semver(self):
        return self._semver

    @property
    def version(self):
        return self._version

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def patch(self):
        return self._patch

    @property
    def build(self):
        return self._build

    def __len__(self):
        return len(self._version.split('.'))

    def __str__(self):
        return self._version

    def __repr__(self):
        """How to represent the object"""
        return 'Version(name=%s, version=%s)' % (self.name, self.version)

    def _get_other(self, other):
        """This method is to enable comparison with versions as strings

        :Returns: Version

        :param other: **Required** The object being compared to this one
        :type other: String or Version
        """
        if isinstance(other, str):
            try:
                other_version = Version(other, name=None)
            except ValueError:
                msg = "Unable to compare %s and %s" % self, other
                raise TypeError(msg)
            else:
                return other_version
        elif isinstance(other, Version):
            return other
        else:
            msg = 'Unable to compare types %s and %s' % (type(self), type(other))
            raise TypeError(msg)

    def __hash__(self):
        """Because __hash__ goes away if you define __eq__"""
        return hash(self._version)

    def __eq__(self, other):
        """Defines the behavior for testing for equivalence, '=='

        :Returns: Boolean

        :param other: The other object to compare this one against
        :type other: Version
        """
        other_version = self._get_other(other)
        for semver in self._semver:
            this_ver = getattr(self, semver)
            other_ver = getattr(other_version, semver)
            if other_ver is None:
                return False
            elif this_ver != other_ver:
                return False
        else:
            # Yup, for/else is a thing in Python: http://book.pythontips.com/en/latest/for_-_else.html
            return True

    def __ne__(self, other):
        """Defines the behavior for testing for non-equivalence, '!='

        :Returns: Boolean

        :param other: The other object to compare this one against
        :type other: Version
        """
        other_version = self._get_other(other)
        for semver in self._semver:
            this_ver = getattr(self, semver)
            other_ver = getattr(other_version, semver)
            if other_ver is None:
                return False
            if this_ver != other_ver:
                return True
        else:
            return False

    def __lt__(self, other):
        """Define the behavior for testing for less than '<'

        :Returns: Boolean

        :param other: The other object to compare this one against
        :type other: Version
        """
        other_version = self._get_other(other)
        for semver in self._semver:
            this_ver = getattr(self, semver)
            other_ver = getattr(other_version, semver)
            if other_ver is None:
                return False
            if this_ver > other_ver:
                return False
            elif this_ver < other_ver:
                return True

        if len(self) == len(other_version):
            return False

    def __gt__(self, other):
        """Define the behavior for testing for greater than or equal, '>'

        :Returns: Boolean

        :param other: The other object to compare this one against
        :type other: Version
        """
        result = True
        other_version = self._get_other(other)
        for semver in self._semver:
            this_ver = getattr(self, semver)
            other_ver = getattr(other_version, semver)
            if other_ver is None:
                return False
            if this_ver > other_ver:
                return True
            elif this_ver < other_ver:
                return False

        if len(self) == len(other_version):
            return False

    def __le__(self, other):
        """Define the behavior for testing for less than or equal '<='

        :Returns: Boolean

        :param other: The other object to compare this one against
        :type other: Version
        """
        other_version = self._get_other(other)
        for semver in self._semver:
            this_ver = getattr(self, semver)
            other_ver = getattr(other_version, semver)
            if other_ver is None:
                return False
            if this_ver < other_ver:
                return True
            elif this_ver > other_ver:
                return False

        if len(self) == len(other_version):
            return True

    def __ge__(self, other):
        """Define the behavior for testing for greater than, '>='

        :Returns: Boolean

        :param other: The other object to compare this one against
        :type other: Version
        """
        other_version = self._get_other(other)
        for semver in self._semver:
            this_ver = getattr(self, semver)
            other_ver = getattr(other_version, semver)
            if other_ver is None:
                return False
            if this_ver > other_ver:
                return True
            elif this_ver < other_ver:
                return False

        if len(self) == len(other_version):
            return True
