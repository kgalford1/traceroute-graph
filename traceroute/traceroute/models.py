from django.db import models


class Partner(models.Model):
    name = models.CharField(verbose_name='Partner Name', max_length=256, help_text="e.g.",
                            unique=True, )

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Location(models.Model):
    location = models.CharField('Location', max_length=256, help_text="e.g.", )
    partner = models.ForeignKey('Partner', on_delete=models.CASCADE, null=True, )

    class Meta:
        unique_together = ('location', 'partner',)
        ordering = ['partner__name', 'location', ]

    def __str__(self):
        return '{}, {}'.format(self.partner.name, self.location)


class Target(models.Model):
    contact_centre = models.ForeignKey('Location', on_delete=models.CASCADE, null=True, )
    ip_address = models.CharField(verbose_name="Address", max_length=256, help_text="Enter domain name / IP address.",
                                  unique=True, )

    class Meta:
        verbose_name = "Target"
        verbose_name_plural = "Targets"
        ordering = ['contact_centre__partner__name', 'contact_centre__location', 'ip_address', ]

    def __str__(self):
        return str(self.contact_centre) + ' - ' + self.ip_address


class Time(models.Model):
    rrd_graph_time = models.CharField(verbose_name="Graph Time", max_length=16, help_text="Refer to RRD documentation.")

    def __str__(self):
        return str(self.rrd_graph_time)

