## Problem statement 
> What is the problem that this project is going to address?

> Brian: I think the hypothesis is that 1) we can easily specify different types of strategies and 2) different deception strategies have different efficacy

## Specify different types of strategies

### Definitions
**Strategy**: 
**Policy**: defined by a set of pair "**state -> action**" which should allow from any reachable state.
**Plan**: a strictly defined **sequence of actions** leading from the initial state to the goal. Planning involves the unrolling of a policy through time, and refining the policy based on the resulting trajectory (the series of resulting states). [plan vs policy](http://primo.ai/index.php?title=Policy_vs_Plan)

### In order to specify different types of strategies
1. support **chaining of individual actions** into a sequence of actions leading to the end goal
2. support **action-observation exchange** loop

### References
[[Caldera Terminology Q&A]]
**Ability**: An ability is a specific ATT&CK tactic/technique implementation which can be executed on running agents.
```python
Ability = {
  "UUID":,
  "Name":,
  "Tactic":,
  "Technique":,
  "Singleton":,
  "Repeatable":,
  "command": #{variable},
  "payload":,
  "uploads":,
  "parsers":,
  "requirements":,
  "timeout":
}
```
**When is an ability *available*?**
- platform match
- *fact* requirements satisfied

[[CyGIL]]
> Compliant to the OpenAI Gym standard interface, almost if not all the SOTA RL/DRL algorithm libraries developed by the research community can be used directly with CyGIL.

[OpenAI Gym Interface](https://www.gymlibrary.dev/content/basic_usage/)

[RLLib parametric action/observation space](https://docs.ray.io/en/latest/rllib/rllib-models.html#variable-length-complex-observation-spaces)


## Independent Variable: Deceptive Strategy
> What are the factors of interest?


### Conditions


## Dependent Variable 
>What are the tangible metrics?

> map the cyber operation goals to relevant training games


### Definitions


## Hypothesis
> What's the expected outcome?



