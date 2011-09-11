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




