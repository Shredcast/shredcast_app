from tastypie.resources import ModelResource

from mountains.models import Mountain


class MountainResource(ModelResource):
    class Meta:
        queryset = Mountain.objects.all()
        resource_name = 'mountain'