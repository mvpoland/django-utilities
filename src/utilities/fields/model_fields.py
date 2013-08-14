from django.db.models import DateTimeField
from django.utils.translation import ugettext_lazy as _

class CreatedOnField(DateTimeField):
    """
    Field for storing the object's creation time.
    """
    
    def __init__(self, *args, **kwargs):
        self.verbose_name = None
        if 'verbose_name' in kwargs:
            self.verbose_name = kwargs['verbose_name']
            del kwargs['verbose_name']
        super(CreatedOnField, self).__init__(auto_now_add=True, db_index=True,
                                verbose_name=self.verbose_name or _('created on'), editable=False)

class UpdatedOnField(DateTimeField):
    """
    Field for storing the object's last modification time.
    """
    
    def __init__(self, *args, **kwargs):
        self.verbose_name = None
        if 'verbose_name' in kwargs:
            self.verbose_name = kwargs['verbose_name']
            del kwargs['verbose_name']
        super(UpdatedOnField, self).__init__(auto_now=True, db_index=True,
                                verbose_name=self.verbose_name or _('updated on'), editable=False)
    