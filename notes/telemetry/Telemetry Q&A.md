## Problem statement 
> What is the problem that this project is going to address?

Attack/defend decision making models require network/host information as input. However, there’s a lack of contextual telemetry, especially the abstract network status needed by attack graph-based game theory algorithms. (*Or a disconnection between the tools and the models.*)

## Proposal
> What is the basic approach, method, idea or tool that’s being suggested to solve the problem? (E.g. dynamic disk shuffling, stainless-steel moustrap springs, an AI tool for writing monthly progress reports.)

**Substitute the numerical abstractions in game theory models with realistic data collected by telemetry tools.**

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
- Attacker resources expended
- Altered perception
[[Measuring the Effectiveness of Network Deception]]

## What do we need from telemetry?

### Host
Presence of decoy; Deceptive reporting of privileges; Privileges required to access or find data; Attacker’s highest privileges; Valuable data found by the attacker; Local privilege escalation (PrivEsc) discovered by attacker; Attack successful; Presence of attacker on the host; Presence of local PrivEsc vulnerability

### Network
attack graph; deceptive attack graph; attacker's location; for each host representing if the host has been scanned or exploited, and the access the attacker has on the host, none, user, administrator, or unknown; 

### Feedback
attacker's progress; breached host value; the cost for adding honeypots and other defensive actions

## Appendix: Decision-making models

| Paper                                                                                                                         | Attacker Action                                                                                                                                                                                                                                                                | Defender Action                                                                                                                                                                                                                               | Information Requirement                                                                                                                                                                                                                                                                                                                               | Attacker Reward                                                                                                                      | Defender Reward                                                                                                                                                     |
| ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Durkota et al 2015](https://www.aaai.org/ocs/index.php/IJCAI/IJCAI15/paper/view/10721/10737)                                 | Attack                                                                                                                                                                                                                                                                         | Add Honeypots of certain type T                                                                                                                                                                                                               | N/A                                                                                                                                                                                                                                                                                                                                                   | time and resources for the attacker to perform the action.                                                                           | (1) the expected loss for the attacked hosts and (2) the cost for adding the HPs into the network.                                                                  |
| [Kinneer et al 2019](https://dl.acm.org/doi/pdf/10.1145/3359986.3361208)                                                      | in time step 0, the attacker chooses an action γj ∈ Γ = {γ1, ...γZ } that indicates their attack plan or TTP. They will not change it unless they observe that the defender makes an eviction attempt or takes an active measure.                                              | In time step t ∈{1, ...τ }, the defender can choose an action from the set of eviction attempts Ω = {ω1, ω2,...,ωL }. The success of an eviction attempt depends on the suitability of the eviction action to the TTP chosen by the attacker. | attacker's TTP<br>attack graph                                                                                                                                                                                                                                                                                                                        | the amount of time they remain in the system multiplied by the appropriateness αij ∈[0, 1] of their chosen TTP γj to their type θi . | as the negation of the amount of time the attacker remains in the system multiplied by δi ∈[1, 10], a coefficient describing how disruptive the attacker type i is. |
| [Milani et al 2020](https://link.springer.com/content/pdf/10.1007/978-3-030-64793-3_8.pdf?pdf=inline%20link)<br>Du et al 2022 |                                                                                                                                                                                                                                                                                | (i) hiding a real edge with a cost ch(e), (ii) adding a fake edge in a given set Ed with a cost ca(e), and (iii) modifying the perceived reward of a non-entry-point node with a cost cδ(n) per unit of change                                | attack graph<br>deceptive attack graph<br>attacker's location                                                                                                                                                                                                                                                                                         |                                                                                                                                      |                                                                                                                                                                     |
| [Foley et al 2022](https://dl.acm.org/doi/pdf/10.1145/3488932.3527286)                                                        | Discover Remote Systems; Discover Network Services; Exploit Network Services;Escalate;Impact                                                                                                                                                                                   | Monitor; Analyse; Misinform; Remove; Restore                                                                                                                                                                                                  | a vector of 52 bits, 4 bits for each host representing if the host has been scanned or exploited, and the access the attacker has on the host, none, user, administrator, or unknown.                                                                                                                                                                 | host value                                                                                                                           | the negation of attacker reward<br>impact loss                                                                                                                      |
| [Shinde et al 2021](http://thinc.cs.uga.edu/files/ssdAAMAS21-cameraready.pdf)                                                 | Search for sensitive data for theft; Search for local PrivEsc vulnerability; Exploit local PrivEsc vulnerability; Check availability of root privileges; Download data from target; Establish a permanent presence in the system; Manipulate stored data; Terminate the attack | Deploy decoy data                                                                                                                                                                                                                             | Type of data on host; Presence of decoy; Deceptive reporting of privileges; Privileges required to access or find data; Attacker’s highest privileges; Valuable data found by the attacker; Local privilege escalation (PrivEsc) discovered by attacker; Attack successful; Presence of attacker on the host; Presence of local PrivEsc vulnerability | N/A                                                                                                                                  | N/A                                                                                                                                                                 |
