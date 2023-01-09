## Problem statement 
> What is the problem that this project is going to address?

## Proposal
> What is the basic approach, method, idea or tool that’s being suggested to solve the problem? (E.g. dynamic disk shuffling, stainless-steel moustrap springs, an AI tool for writing monthly progress reports.)

**Defender**: defend the network
=> "best" deceptive defense strategies
-  Optimal (given network "state" $a = argmax_{a} Q(s, a)$)
- Adaptive (to the dynmamic network "state" $a = argmax_{a} Q(s^t, a)$)
- Learning (improve defense performance according to feedback on deception efficacy)
- Hierarchical (make defense decisions at various level of abstraction/granularity to defend against host-based attacks and network-wide threats)
- within constraints

=> thus requires information about
- network status (for optimal and adaptive decision-making)
- defense (especially deception) efficacy (as feedback to guide learning)

=> that is 
- real-time
- hierachical

**Attacker**: 
Deception is an art of making someone believe in something not true. It's effectiveness depends on attacker's capabilities of gathering information about the network and detecting the inconsistency. We need a variety of sensors to express the various monitoring/reconnaissance capabilities of attackers.

## Hypotheses
> What exactly are the expected effects of the proposed solution? (E.g. disk I/O time will increase to 2 seconds per request.) Why is this? 


> What are plausible alternatives? How likely are they? What’s good and bad about them by comparison with what’s proposed? What have others done already? What did they learn? (This is the “literature search” segment.)


## What is network telemetry?
Network telemetry is **a technology for gaining network insight and facilitating efficient and automated *network management***. It encompasses various techniques for remote data generation, collection, correlation, and consumption.



## What are the data sources for network telemetry?
[[Towards an Open Format for Scalable System Telemetry]]

[[Network Telemetry - Towards A Top-Down Approach]]

## What indicators can the evaluation of deception efficacy be based on?
[[Examining the Efficacy of Decoy-based and Psychological Cyber Deception]]
- Forward progress
	- 
- Attacker resources expended
- Altered perception

[[Measuring the Effectiveness of Network Deception]]
