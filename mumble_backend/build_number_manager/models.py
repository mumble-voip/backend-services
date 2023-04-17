from django.db import models


class Series(models.Model):
    major = models.PositiveIntegerField()
    minor = models.PositiveIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%i.%i.x" % (self.major, self.minor)  # e.g. 1.4.x

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["major", "minor"], name="major_minor_unique"
            )
        ]
        verbose_name_plural = "series"


class Build(models.Model):
    series = models.ForeignKey(Series, on_delete=models.PROTECT)
    commit_hash = models.CharField(max_length=128)
    build_number = models.PositiveIntegerField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%i.%i.%i" % (
            self.series.major,
            self.series.minor,
            self.build_number,
        )  # e.g. 1.4.142

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["series", "commit_hash"], name="commit_unique_in_series"
            )
        ]
