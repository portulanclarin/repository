from django.db import models

from metashare.storage.models import StorageObject

# the following code is based on http://djangosnippets.org/snippets/2451/

class OAIPMHRepository(models.Model):
    """A model that represents a dictionary. This model implements most of 
    the dictionary interface,allowing it to be used like a python dictionary.

    """
    repository_name = models.CharField(max_length=255)

    @staticmethod
    def get_repository(repository_name):
        """Get the Dictionary of the given name.

        """
        df = OAIPMHRepository.objects.select_related().get(repository_name=repository_name)

        return df

    def __getitem__(self, remote_id):
        """Returns the resource of the selected remote_id.

        """
        return (self.remoteidresourcepair_set.get(remote_id=remote_id).resource, \
            self.remoteidresourcepair_set.get(remote_id=remote_id).digest_checksum)

    def __setitem__(self, remote_id, (resource, digest_checksum)):
        """Sets the resource of the given remote_id in the repository.

        """
        try:
            ridrp = self.remoteidresourcepair_set.get(remote_id=remote_id)
        except RemoteIDResourcePair.DoesNotExist:
            RemoteIDResourcePair.objects.create(container=self, \
                                                remote_id=remote_id, \
                                                resource=resource, \
                                                digest_checksum=digest_checksum)
        else:
            ridrp.resource = resource
            ridrp.digest_checksum = digest_checksum
            ridrp.save()

    def __delitem__(self, remote_id):
        """Removed the given remote id from the repository.

        """
        try:
            ridrp = self.remoteidresourcepair_set.get(remote_id=remote_id)
        except RemoteIDResourcePair.DoesNotExist:
            raise KeyError
        else:
            ridrp.delete()

    def __len__(self):
        """Returns the length of this Dictionary.

        """
        return self.remoteidresourcepair_set.count()

    def iter_remote_ids(self):
        """Returns an iterator for the keys of this Dictionary.

        """
        return iter(ridrp.remote_id for ridrp in self.remoteidresourcepair_set.all())

    def iter_resources(self):
        """Returns an iterator for the keys of this Dictionary.

        """
        return iter(ridrp.resource for ridrp in self.remoteidresourcepair_set.all())

    __iter__ = iter_remote_ids

    def iteritems(self):
        """Returns an iterator over the tuples of this Dictionary.

        """
        return iter((ridrp.remote_id, ridrp.resource, ridrp.digest_checksum) \
                for ridrp in self.remoteidresourcepair_set.all())

    def remote_ids(self):
        """Returns all keys in this Dictionary as a list.

        """
        return [ridrp.remote_id for ridrp in self.remoteidresourcepair_set.all()]

    def resources(self):
        """Returns all resources in this repository as a list.

        """
        return [ridrp.resource for ridrp in self.remoteidresourcepair_set.all()]

    def items(self):
        """Get a list of tuples of key, resource for the items in this Dictionary.
        This is modeled after dict.items().

        """
        return [(ridrp.remote_id, ridrp.resource, ridrp.digest_checksum) \
            for ridrp in self.remoteidresourcepair_set.all()]

    def get(self, remote_id, default=None):
        """Gets the given key from the Dictionary. If the key does not exist, it
        returns default.

        """
        try:
            return self[remote_id]
        except KeyError:
            return default

    def has_remote_id(self, remote_id):
        """Returns true if the Dictionary has the given key, false if not.

        """
        return self.contains(remote_id)

    def contains(self, remote_id):
        """Returns true if the Dictionary has the given key, false if not.

        """
        try:
            self.remoteidresourcepair_set.get(remote_id=remote_id)
            return True
        except RemoteIDResourcePair.DoesNotExist:
            return False

    def clear(self):
        """Deletes all keys in the Dictionary.

        """
        self.remoteidresourcepair_set.all().delete()

    def __unicode__(self):
        """Returns a unicode representation of the Dictionary.

        """
        _unicode = u'<{} = {}>'.format(self.repository_name, \
                                       unicode(self.asPyDict()))
        return _unicode

    def asPyDict(self):
        """Get a python dictionary that represents this Dictionary object.
        This object is read-only.

        """
        fieldDict = dict()
        for ridrp in self.remoteidresourcepair_set.all():
            fieldDict[ridrp.remote_id] = [ridrp.resource, ridrp.digest_checksum]
        return fieldDict


class RemoteIDResourcePair(models.Model):
    """A Key-Value pair with a pointer to the Dictionary that owns it.

    """
    container = models.ForeignKey(OAIPMHRepository, db_index=True)
    remote_id = models.CharField(max_length=340, db_index=True)
    resource = models.OneToOneField(StorageObject)
    digest_checksum = models.CharField(max_length=240)