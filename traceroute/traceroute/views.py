from django.shortcuts import render
from .models import Target, Partner, Location
from django.views import generic
from .rrdpy.rrd import graph
from .rrdpy.utilities import get_args
import os
import shutil


def index(request):
    num_targets = Target.objects.all().count()

    return render(
        request,
        'index.html',
        context={'num_targets': num_targets},
    )


class PartnerListView(generic.ListView):
    model = Partner


class LocationListView(generic.ListView):
    def get_queryset(self):
        if self.kwargs['partner'] == 'all':
            return Location.objects.all()
        else:
            return Location.objects.filter(partner__name__iexact=self.kwargs['partner'])


class TargetListView(generic.ListView):
    def get_queryset(self):
        if self.kwargs['partner'] == 'all':
            return Target.objects.all()
        elif self.kwargs['location'] == 'all':
            return Target.objects.filter(contact_centre__partner__name__iexact=self.kwargs['partner'], )
        else:
            return Target.objects.filter(contact_centre__partner__name__iexact=self.kwargs['partner'],
                                         contact_centre__location__iexact=self.kwargs['location'], )


def graph_view(request, target, path):
    template_name = 'traceroute/graph_view.html'
    directory = '/var/www/html/django'  # TODO: Remove hardcoded location.

    def get_images():
        if path == 'default':
            with open(directory + '/db/' + target + '/current.txt', 'r') as f:
                path_id = f.readline().strip()
        else:
            path_id = path

        file = directory + '/db/' + target + '/' + path_id + '.rrd'

        graph_dir = '/var/www/html/django/traceroute/static/' + target
        for ffile in os.listdir(graph_dir):
            fpath = os.path.join(graph_dir, ffile)
            try:
                if os.path.isfile(fpath):
                    os.unlink(fpath)
            except Exception as e:
                pass

        graph(get_args(directory + '/db', target), file)
        images = os.listdir(graph_dir)
        images = ['/' + target + '/' + i for i in images if not i.startswith(target)]
        images = sorted(images)
        images.insert(0, '/' + target + '/' + target + '.png')
        return images, path_id

    def get_paths():
        return [f[:-4] for f in os.listdir(directory + '/db/' + target) if f.endswith(".hop")]

    return render(
        request,
        template_name,
        context={'hash': get_images()[1], 'images': get_images()[0], 'paths': get_paths(), 'target': target},
    )

