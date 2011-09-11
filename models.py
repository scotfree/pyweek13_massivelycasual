from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Node(models.Model):
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    controller = models.ForeignKey(User)
    last_modified = models.DateTimeField(auto_now=True)

class Edge(models.Model):
    from_node = models.ForeignKey(Node, related_name='goes_to')
    to_node = models.ForeignKey(Node, related_name='comes_from')
    strength = models.FloatField(default=0.0)
    
    def __str__(self):
        return str( self.from_node ) + " --> " + str( self.to_node )

class Role(models.Model):
    pass
