from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import simplejson as json
    
RESOURCE_CHOICES = (
    ('B', 'Biologicals'),
    ('M', 'Minerals'),
    ('C', 'Culture'),
    ('A', 'Any'),
    
)

JOB_CHOICES = (
    ('P', 'Produce'),
    ('T', 'Trade'),
    ('S', 'Study'),
    ('B', 'Breed')
    )


class Game(models.Model):
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # admin = models.ForeignKey(User)
    last_modified = models.DateTimeField(auto_now=True)
    current_turn = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)
    
class System(models.Model):
    game = models.ForeignKey(Game)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    controller = models.ForeignKey(User)
    last_modified = models.DateTimeField(auto_now=True)
    resources_string = models.CharField(max_length=200, blank=True)
    production_string = models.CharField(max_length=200, blank=True)

    def get_production(self):
        return json.loads( self.production_string )
    
    def set_production(self, res_dict):
        self.production_string = json.dumps( res_dict )

    def get_pop(self):
        return self.get_resources()['P']
        
    def get_resources(self):
        return json.loads( self.resources_string )

    def set_resources(self, res_dict):
        self.resources_string = json.dumps( res_dict )

    def add_resources(self, res_dict):
        sys_res = self.get_resources()
        for k,v in res_dict.iteritems():
            sys_res[k] = sys_res.get(k,0) + int(v)
        self.set_resources(sys_res)

    def remove_resources(self, res_dict):
        sys_res = self.get_resources()
        for k,v in res_dict.iteritems():
            if sys_res.get(k,0) > v:
                print "Using %i of %i" % (v, sys_res[k])
                sys_res[k] -= v
            else:
                print "Not enough %s" % str(k)
                return False
        self.set_resources(sys_res)

        
        
    def __str__(self):
        return str(self.name)

    def as_dict(self):
        
        return {
            "game_id": self.game.id,
            "name": self.game.name,
            "controller": self.game.controller_id,
            "resources": self.get_resources()
            }
    
class Edge(models.Model):
    from_node = models.ForeignKey(System, related_name='goes_to')
    to_node = models.ForeignKey(System, related_name='comes_from')
    strength = models.FloatField(default=0.0)
    
    def __str__(self):
        return str( self.from_node ) + " --> " + str( self.to_node )

#class ResourceSet(models.Model):
#    # tag = models.CharField(max_length=5)
#    name = models.CharField(max_length=200)
#    description = models.TextField(blank=True)
    
    
class Job(models.Model):
    controller = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    pop = models.IntegerField(default=0)
    recipe = models.CharField(max_length=200, blank=True)
    
    from_node = models.ForeignKey(System, related_name='works_to')
    #from_resources_json = models.CharField(max_length=200, default={'pop',1})
    #from_resources = models.ManyToManyField(Resource, related_name='uses')
    #from_amount = models.IntegerField(default=1)

    #to_resources_jso = models.CharField(max_length=200, default={'pop',1})
    #to_resource = models.ManyToManyField(Resource, related_name='makes')
    #to_amount = models.IntegerField(default=1)
    to_node = models.ForeignKey(System, related_name='works_from')

    
    def __str__(self):
        return str("[%i] T: %s (%s to %s)" % (self.pop, self.recipe, str(self.from_node), str(self.to_node)))
    
    def parse_resource_set(self, res_set_string):
        res_set = {}
        for item in res_set_string.split(","):
            res_set[item[0]] = int(item[1])
        return res_set

    def get_transform(self):
        
        return json.loads(self.recipe)
        in_res, out_res = self.recipe.split("->")
        return {"input": self.parse_resource_set(in_res),
                "output": self.parse_resource_set(out_res)}
                
    

class Turn(models.Model):
    game=models.ForeignKey(Game)
    index=models.IntegerField(default=0)
    state_json=models.TextField(blank=True,null=True)
    graph_json=models.TextField(blank=True,null=True)
    started=models.DateTimeField(default=None, null=True, blank=True)
    ended=models.DateTimeField(default=None, null=True, blank=True)
    get_latest_by = "started"

    
#    def save(self, *args, **kwargs):
        #do_something()
        
#        super(Turn, self).save(*args, **kwargs)
        #do_something_else()
#    def __str__(self):
#        return "T%i G%i" % (self.index, self.game)
