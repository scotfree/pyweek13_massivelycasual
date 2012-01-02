from django.conf.urls.defaults import *
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse

from indra.pw13mc.models import System, Edge, Job, Game, Turn
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django import forms
from django.contrib.auth.forms import UserCreationForm
import simplejson as json
import random, pprint

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/nodes/")
    else:
        form = UserCreationForm()
    return render_to_response("nodes/register.html", {
        'form': form,
        }, context_instance=RequestContext(request))


# Graph generation
# ----------------

def get_game_graph(game_id):
    sg = {}
    g = Game.objects.get(pk=game_id)
    for s in g.system_set.all():
        sg[s.id] = (s, s.goes_to.all())
    return sg

def get_author_subgraph(username):
    sg = {}
    author = User.objects.get(username__exact=username)
    for n in author.node_set.all():
        sg[n.id] = (n, n.goes_to.all())
    return sg


def node_graph_html(request, node_id):
    
    return render_to_response("nodes/nodegraph.html",{}, context_instance=RequestContext(request))

def author_graph_html(request, node_id):
    return render_to_response("nodes/authorgraph.html",{}, context_instance=RequestContext(request))
         
def build_graph(object_list, events):
    stuff = []
    for o,z in object_list.values():
        # system_events = str(events['nodes'][str(o)])
        stuff.append( {
                "adjacencies":
                    [{"nodeTo": int(e.from_node.id), "nodeFrom": int(e.to_node.id),
                      "$lineWidth": random.randint(1,15),
                      "$color": '#%02x%02x%02x' % (
                            random.randint(0,255),
                            random.randint(0,255),
                            random.randint(0,255))}
                     for e in o.comes_from.all()],
                "data":{"$type":"circle","$dim":10},
                "id" : o.id, "name" : o.name} )
    return json.dumps(stuff)

       


def old_build_graph(object_list):
    stuff = '[\n'

    stuff += '{\n"adjacencies": [' + '\n   ' 
    stuff += ",\n   ".join( ['{"nodeTo":"%s", "nodeFrom":"%s", "data":{"$lineWidth":%i,"$color":"%s"}}' % \
                                 (str(e.from_node.id), str(e.to_node.id), random.randint(1,15),
                                  '#%02x%02x%02x' % \
                                      (random.randint(0,255),random.randint(0,255),random.randint(0,255)))
                                 for e in o.comes_from.all()] )
    stuff += '\n],"data":{"$type":"circle","$dim":10, "system_events": "blah"},' + "\n"
    stuff += '"id":"%s", "name":"%s"},' % (str(o.id), str(o.name)) + "\n"
    stuff = stuff[:-2] + "]" + "\n"    
    return stuff


def author_graph(request, username):
    return render_to_response("nodes/graph.html",
                              {'object_list': object_list,
                               'stuff':build_graph(object_list)})



def client(request, game_id, player_id=None):
    g = Game.objects.get(pk=game_id)
    t = g.turn_set.latest(field_name='started')
    return render_to_response("pw13mc/client.html",
                              {'stuff':t.graph_json,
                               'things': t.state_json})
    
    
def graph(request, graph_type, graph_param):
    if graph_type == 'author':
        #sg = get_author_subgraph(graph_param)
        #graph_title = "Author Graph for " + graph_param
        pass
    elif graph_type == 'game':
        g = Game.objects.get(pk=graph_param)
        t = g.turn_set.get(index=g.current_turn)
        stuff = t.graph_json
        #
        graph_title = "Summary of all Nodes for game %s" % str(graph_param)
    #elif graph_type == 'node':
    #    node = Node.objects.get(pk=graph_param)
    #    sg = get_subgraph(node)
    #    graph_title = "Graph for: " + node.title
    #stuff = build_graph(sg)
    return render_to_response("pw13mc/game_graph.html",
                              {'graph_title': graph_title,
                               'stuff':stuff})


def random_color_str():
    return '#%02x%02x%02x' % (
        random.randint(0,255),
        random.randint(0,255),
        random.randint(0,255))

def random_color():
    #red="F5001D"
    #blue="0B61A4"
    #yellow="ECFC00"
    components = [10,120]
    choices = (
        random.choice( components ),
        random.choice( components ),
        random.choice( components ))
    return ('#%02x%02x%02x' % choices, choices)


def cching(request):
    outside_color, outside_choices=random_color()
    inside_color, inside_choices=random_color()
    return render_to_response("pw13mc/colors.html",{'data':locals()})

# Game State Export
# -----------------

def game_json(request, game_id):
    g = Game.objects.get(pk=game_id)
    t = g.turn_set.latest(field_name='started')
    #data = t.state
    #history = t.events
    format_param = request.GET.get('format', 'json')            
    if format_param == 'json':        
        return HttpResponse(t.state_json, mimetype='text/json')
    else:
        return HttpResponse(t.state_json, mimetype='text/plain')
    
def system_json(request, system_id):
    s = System.objects.get(pk=system_id)
    g = s.game
    t = g.turn_set.latest(field_name='started')
    #data = t.state
    #history = t.events
    format_param = request.GET.get('format', 'json')            
    if format_param == 'json':        
        return HttpResponse(t.state_json, mimetype='text/json')
    else:
        return HttpResponse(t.state_json, mimetype='text/plain')
    

    


    
def game_state_json(game_id, status_message="No status.", raw_return = False):
    game = Game.objects.get(id=game_id) 
    removed_fields = ['_state','last_modified']

    stuff = {
        'name': str(game.name),
        'game_id': game_id,
        'systems': {},
        'jobs': {},
        'edges' : {}
        }

    
    for s in game.system_set.all():
        state_dict = s.__dict__.copy()
        for x in removed_fields:
            del(state_dict[x])
        stuff['systems'][s.id] = state_dict
        stuff['jobs'][s.id] = {}
        stuff['edges'][s.id] = {}
        for j in s.works_from.all():
            recipe = json.loads( j.recipe )
            recipe['pop'] = j.pop
            if stuff['jobs'][s.id].has_key( j.from_node.id ):
                stuff['jobs'][s.id][j.from_node.id].append( recipe )
            else:
                stuff['jobs'][s.id][j.from_node.id] = [ recipe ]
        for e in s.goes_to.all():
            if stuff['edges'][s.id].has_key( e.to_node.id ):
                stuff['edges'][s.id][e.to_node.id].append( str(e) )
            else:
                stuff['edges'][s.id][e.to_node.id] = [ str(e), ]
    json_data = json.dumps( stuff )
    if raw_return:
        return (stuff, json_data)
    else:
        return json_data


# Actual game mechanics
# ======================

def basic_system_jobs(game, s):
    return s.works_from.all() 

def get_sample( things, weights, controls=[], pop=1):
    tot = sum(weights) + sum(controls)
    selected = []
    for i in range(pop):
        so_far = 0
        roll = random.randint(0,tot)
        for j,w in enumerate(weights):
            so_far += w
            if so_far >= roll:
                selected.append( things[j] )
                break
    return selected


def get_edges(game):
    pass
                
def get_system_jobs(game, s):
    #print str(s.works_from.all())
    
    # sample for current_pop:
       # set job.pop for next turn
       # add copy of job to system_jobs for this turn


    # Get all jobs working in the given system s
    # ---------
    current_pop = s.get_pop()
    aggregated = s.works_from.all()
    print "\n\nProcessing %i/%i sys jobs: %s" % (current_pop, len(aggregated), str(aggregated))
    
    # Assign the actual current population to these jobs,
    # weighted by their previous distribution,
    # and any control points
    sample = get_sample( aggregated, [a.pop for a in aggregated], pop = current_pop  )

    # Note that after sampling, we won't use the per-job pop/weights again this turn.
    # So now we set them as filled in the sample for the default dist next turn.
    for j in aggregated:
        j.pop = 0
        j.save()
    jobs = []
    for j in sample:
        jobs += [j]
        j.pop += 1
        j.save()

        
    print "\n\nReturning %i:\n %s" % (current_pop, str(jobs[:current_pop]))
    return jobs[:current_pop]
    
def set_system_jobs(s, changes=None):
    sys_jobs = s.works_from.all()
    


def get_eligible_jobs(job, job_pool):
    result = []
    #for i,j in job_pool:
        # if job.to_node
    #    pass
    return result

def process_turn_request(request, game_id):
    g = Game.objects.get(pk=game_id)
    output = process_cluster(g)

    return HttpResponseRedirect("/pw13mc/client/%s/" % str(game_id))
    
def process_cluster(game):
    cluster_jobs = []
    cluster_prod = {}
    turn_results = {'nodes':{}, 'edges':{} }

    # for each system, sample from jobs according to last_turn_job_dist + gold_commands
    # 
    
    
    for s in game.system_set.all():
        turn_results['nodes'][str(s)] = []
        cluster_jobs += get_system_jobs(game, s) 
    for s in turn_results['nodes'].keys():
        turn_results['edges'][s] = {}
        for t in turn_results['nodes'].keys():
            turn_results['edges'][s][t] = []
    
            
    random.shuffle(cluster_jobs)
    # current_pop = s.get_resources()['P']
    # print "Cluster jobs: %s" % str(cluster_jobs)
    
    for j in cluster_jobs:
        r = j.get_transform()
        #print "Transform: %s" % str(r)
        if r['action'] == "Produce":            
            # example P->B food to Bio resource
            work_sys = j.from_node
            work_sys.remove_resources( r['input'] )
            work_sys.add_resources( r['output'] )

            
            # cluster_prod[work_sys.id] = cluster_prod.get(work_sys.id, {}).update(r['output'])
            print "Updated %s with %s" % (str(work_sys), str(r['output']))
            #do_production(cluster_jobs)
            turn_results['nodes'][str(work_sys)].append(r)
            
        elif r['action']=="Trade":
            pool = get_eligible_jobs(j, cluster_jobs)
            if not pool:
                print "No partner available..."
                continue
            partner = random.choice(pool)

            work_sys.remove_resources( r['input'] )
            work_sys.add_resources( r['output'] )
            remote_sys.input_resources( r['input'] )
            remote_sys.remove_resources( r['output'] )
            turn_results['edges'][str(work_sys)][str(remote_sys)].append(r)

            # if work_sys != remote_sys:
                
                
            print "Trade (%s, %s): %s -> %s" \
                % (str(work_sys), str(remote_sys), str( r['input']), str(r['output']))
            # do_trade(j, r, work_sys, partner)
            del(cluster_jobs[ partner ])
            
        elif r['action']=="Research":
            print "Uh, researching?"
            pass


    # now take fresh population, and distribute across the jobs available for next turn
    # using this turn's pop dist'n as a guide, modified by gold.
    
    #for s in game.system_set.all():
        #new_pop = s.get_pop()
        # new_jobs = 
        # for i in range(new_pop):
            
        
    turn_state, turn_json = game_state_json( game.id, raw_return=True )    
    
    gg = get_game_graph(game.id)
    graph_json = build_graph(gg, turn_results)
    #print "Got graphjson: %s" % graph_json
    new_turn_content = {'state': turn_state, 'events': turn_results}
    #pprint.PrettyPrinter().pprint((new_turn_content))
    new_turn = Turn(state_json=json.dumps(new_turn_content), graph_json=graph_json,
                    index=game.current_turn + 1, game=game)
    new_turn.save()
    game.current_turn += 1
    game.save()

    
def process_game_id(game_id):
    g = Game.objects.get(pk=game_id)
    return process_cluster(g)



def process_game(game):
    results = {'local': {}, 'nonlocal': [] }
    nonlocal_jobs = []
    for s in game.system_set.all():
        print "Processing system: %s" % str(s)
        results[s.id], new_nonlocal_jobs = process_system(game, s)
        nonlocal_jobs.append( new_nonlocal_jobs )
    
    return results

# Admin and 

def create_random_game(user_ids, game_name):
    initial_recipes = [ json.dumps(r) for r in
                        [{"action":"Produce","name": "Breed", "input": {"B":1}, "output": {"P": 1}},
                         {"action":"Produce", "name": "Goldminer", "input": {"P":1, "M":2}, "output": {"G": 1}},
                         {"action":"Trade", "name": "Trade - w for s",
                          "input": {"P":1, "C":2}, "output": {"T": 1}},
                         ] ]

    g = Game(name=game_name)
    g.save()
    gid= g.id
    if  user_ids:
        players = [User.objects.get(pk=user_id) for user_id in user_ids]
    else:
        players =  User.objects.all()
    systems = []
    print "Game! %s Players! %s" % (str(g), str( players ))
    num_players = len( players )

    for p in players:
        s = System(controller=p, name="%s" % str(p), game=g)
        s.set_production(
            {'B': random.randint(0,10),
             'M': random.randint(0,5),
             'C': random.randint(0,5),
             'P': random.randint(5,10)
             })
        s.set_resources(
            {'B': random.randint(0,100),
             'M': random.randint(0,50),
             'C': random.randint(0,10),
             'P': random.randint(10,100)
             })
        s.save()
        systems.append(s)

        for init_recipe in initial_recipes:
            j = Job(controller=p, pop=random.randint(1,10),
                    from_node=s, to_node=random.choice(systems),recipe=init_recipe)
            j.save()
        
    for i in range( num_players * 2):
        from_sys = random.choice(systems)
        to_sys=random.choice(systems)
        e = Edge(from_node=from_sys, to_node=to_sys)
        print "Creating an edge from %s to %s" % (str(from_sys), str(to_sys))
        e.save()

    turn_results = {'nodes':{}, 'edges':{} }
    turn_state, turn_json = game_state_json( g.id, raw_return=True )    
    new_turn_content = {'state': turn_state, 'events': turn_results}
    gg = get_game_graph(g.id)
    graph_json = build_graph(gg, turn_results)
    new_turn = Turn(state_json=json.dumps(new_turn_content), graph_json=graph_json,
                    game=g)
    new_turn.save()

    return gid
        

    

# OLD and DEAD!
# ============
    
# print str(turn_results)
        
def process_system(game, s):

    # get in system jobs

    # get in system resources and local *available* production
    sys_res = s.get_resources()

    gen_res = {}
    system_production = s.get_production()
    print "SysProd: " +  str(system_production)
    print "Already generated SysRes: " +  str(sys_res)
    # populate jobs
    job_objects = list(s.works_to.all())
    local_jobs = []
    edge_jobs = []
    for jo in job_objects:
        if jo.from_node is None or jo.from_node != s:
            edge_jobs.append( jo )
        else:
            local_jobs.append( jo )
    print "Ignoring edge jobs! %s" % str(edge_jobs)
        
    #for j in local_jobs:
    #    for p in range(j.pop):
    #        jobs.append( j.get_transform() )
                      
    # for each randomly selected job recipe without replacement        
    random.shuffle(jobs)
    job_production = {}
    for t in jobs:
        enough = True
        for k,v in t["input"].iteritems():
            if sys_res.get(k, 0) < v:
                enough = False
                break
        print "transformed %s: %s " % (str(enough), str( t ))
        if enough:
            for k,v in t["input"].iteritems():
                sys_res[k] = sys_res.get(k,0) - v
            for k,v in t["output"].iteritems():
                gen_res[k] = gen_res.get(k, 0) + v
    print "Generated resources for next turn: %s" % str( gen_res )
    print "...losing %s" % str( sys_res )
    s.set_resources( gen_res )
    s.save()
    return edge_jobs
