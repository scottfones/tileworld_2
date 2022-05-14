# CISC 489: PA2 - Simulation of Competitive Agents in Tileworld

![black workflow](https://github.com/scottfones/tileworld_2/actions/workflows/black.yml/badge.svg)

## Design Goal

The goal is to partition the map into halves based on the opposing player's location. To be successful, the agent needs a solution to this problem for three situations:

- Initial Separation
  - With both agents sharing the same space, the agent should be able to gain separation while collecting coins.
- Maintaining Equilibrium
  - Once separated, the agent should move to maintain the partitioning while collecting coins.
- Opposing Incursions
  - With the opposing agent's strategy unknown, the agent should be able to react to drastic changes to the equilibrium state.

The driving force is filtered coin locations. By deciding whether a coin is in an acceptable partition, we direct pathfinding toward desirable locations. This has the added benefit of following the ABC principle: Always Be Cointinuing. This principle dictates that we maximize the amount of time spent collecting coins and minimize thinking.

### Test Environment

`PlayerA` is used to represent the opposing, competitive agent. I decided that the worst-case strategy would be collecting coins effectively while having no regard for Player B. Therefore, Player A uses a modified version of the strategy implemented in the [first project](https://github.com/scottfones/Tileworld); Player A will pursue the closest coin without constraints on its location and has no knowledge of Player B.

`PlayerB` represents an attempt to counter Player A by implementing the design goal. This player should be used for Case 2
and Case 3 of the [write-up](./Programming%20Assignment%202.pdf). Between the random movements in Case 2 and the strategic movements in Case 3, Player B's effectiveness should be well tested.

### Version 0.1

Coins are filtered by agent distances. If a coin is closer to our competitive agent, Player B, it becomes a potential target.

This design worked during the initial separation phase but failed in the others. Pursuing coins in this manner is too undirected to maintain equilibrium.

### Version 0.2

Vertical and horizontal partitions are constructed independently based on the opposing agent's location. The initial separation phase results in overlapping agents, but this might be due to their equivalent pathfinding algorithms. When the agent finds itself in a recently invalidated partition, it transitions smoothly by continuing to collect coins.

This approach appears to avoid the other agent but restricts valid coins to a quarter of the map. I believe this is caused by how I constructed the partitions.

### Version 0.3

Overlapping quadrants are created ahead of time such that the opposing agent is contained within at least one. If a coin is located within one of the opposing agent's quadrants, it is excluded as a potential target. This results in the opponent "owning" at least one quadrant of the map, or more if they are located at the boundaries. Our agent is afforded an "L" shaped partition but this is effectively reduced to half of the map. Essentially, we're guaranteed access to the quadrant of the map opposite the opposing agent, and then whatever contiguous partition is closest.

There remains no working strategy for initial separation. However, the equilibrium state is quickly found and maintained. We are highly susceptible to opposing incursions, especially when the opposing agent is located near the middle of the map. Given the small map size, it is often the case that both agents are near the middle and collisions become unavoidable.
An obvious iterative improvement will be adding another partition to cover the middle of the map. Since the opposing player may be a member of more than one partition, the difficulty will be tuning the partition's size.

### Version 0.4

The two primary problems with v0.3 were center-map play and opportunity loss. Progress has been made on both fronts by decreasing partition sizes. By switching to a 3x3 partitioning, one partition covers the center of the map and we yield less area to the opposing agent. As an added benefit, the increase in total partition perimeter, which is still configured to overlap by a distance of one movement unit, yields a more "predictive" coin filter. Unfortunately, the smaller partition size also results in less reaction time. Through benchmarking, it seems to be a slight improvement.

### Version 0.5

Design optimization. Very little refactoring was done throughout either the [first project](https://github.com/scottfones/Tileworld) or the above iterative improvements. The resulting code is significantly less complicated and more readable. Dictionaries and priority queues were removed or replaced with lists, and distance is now implicitly calculated by the pathfinding algorithm, rather than explicitly for each coin.

The latter improvement is especially significant. We were calculating, and `PlayerA` still calculates, the Manhattan distance for every coin on the map. With the distance calculated, we inserted the coin into a priority queue, allowing us to prioritize distance and use coin value as a tie-breaker. All of this was done twice! Per `update()` call! The new design simply translates the coin locations while filtering, and the pathfinding algorithm expands the search space until it encounters a coin.

This highlighted another design flaw, which is still present in `PlayerA`. Walls were unaccounted for when calculating the Manhattan distance. This led to situations where the pathfinding algorithm was given the "closest" coin as a target, even if several wall segments were in the way.

## Conclusion

Unfortunately, there wasn't time to implement a more sophisticated strategy. I would have liked to attempt some form of reinforcement learning. As the concepts were being introduced, they seemed to address more and more of the issues I've encountered.

Still, I believe `PlayerB` successfully covers the design goals. The agent seeks some semblance of an equilibrium state and remains performant.

## Note

`player_b.py` is provided as a cut-out of the code required to get `PlayerB` working. I've tested removing the `compAgent.py` import and using two instances of `PlayerB` from `player_b.py`, and everything works.
