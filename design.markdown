Mutating Node Tycoon


Overview
========

The distribution of workers in jobs across a planet determines its internal and external stochastic dynamics.

Control consists of "change orders" - each of which allows a player to reassign one pop unit and costs one gold.

These changes modify the distribution (and absolute counts) of workers across jobs on a planet.

An epidemic model across the graph describes the spread of things like:
  * disease
  * technologies
  * new jobs
  * grey goo
  * information


Data Structures
=====

Resources
----
  
  * biologicals (food, eco)
  * minerals (energy, metal)
  * cultural (science, politics, etc)
 


Produced in systems, following simple dynamic/periodic models disturbed by noise.

The amplitude of this added noise determines the game's dfficulty.



Nodes and Edges - Systems and Starlanes.
----


Jobs and Workers
-----

JobType - enum
  * produce
  * trade
  * embargo
  * breed
  * research
  * meta - affect noise models, etc?

FromNode, ToNode
FromType, ToType
FromStrength, ToStrength

On more reflections, KISS. There are no "archetype" or technology jobs.
Jobs are very specific, and include system and resource types.
They should spread as a technology.



Game Systems and Mechanics
===


Research - in keeping with the Change Controls model, research work can't specify specific projects. It should specify a "direction", encoded as one or more combinations of resource/job. Improvements will be determined ongoign from this.

Oh shit - food -> pop as just another transform, ie Job. But bumps into bigger question - 
if we have starvation modelled somehow, how do we distribute deaths across jobs (or redistribute pop).
