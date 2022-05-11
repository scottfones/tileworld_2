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

The driving force is filtered coin locations. By deciding whether a coin is in an acceptable location, we direct pathfinding toward desirable locations. This has the added benefit of following the ABC principle: Always Be Cointinuing. In this way, we maximize the amount of time spent collecting coins and minimize thinking.

### Test Environment

Player A is used to represent the opposing, competitive agent. I decided that their worst-case strategy would be collecting coins effectively while having no regard for Player B. Therefore, Player A uses a modified version of the strategy implemented in the [first project](https://github.com/scottfones/Tileworld); Player A will pursue the closest coin without constraints on its location or knowledge of Player B.

Player B represents an attempt to counter Player A by implementing the design goal. This player should be used for Case 2
and Case 3 of the [write-up](./Programming%20Assignment%202.pdf). Between the random movements in Case 2 and the strategic movements in Case 3, Player B's effectiveness should be well tested.

### Version 0.1

Coins are filtered by agent distances. If a coin is closer to our competitive agent, Player B, it becomes a potential target.

This design worked during the initial separation phase but failed in the others. The pursuit of coins is too undirected to maintain equilibrium.

### Version 0.2

[Video](https://youtu.be/ngetk3HWgeQ)

Vertical and horizontal partitions are constructed independently based on the opposing agent's location. The initial separation phase results in overlapping agents, but this might be due to their equivalent pathfinding algorithms. When the agent finds itself in a recently invalidated partition, it transitions smoothly by continuing to collect coins.

This approach appears to avoid the other agent but restricts valid coins to a quarter of the map. I believe this is caused by how I constructed the partitions.

### Version 0.3

[Video](https://youtu.be/Y1_S05nIBHw)

Overlapping quadrants are created ahead of time such that the opposing agent is contained within at least one. If a coin is located within one of the opposing agent's quadrants, it is excluded as a potential target. This results in the opponent "owning" at least one quadrant of the map or more if they are located at the boundaries. Our agent is afforded an "L" shaped partition but is effectively reduced to only half. We're guaranteed access to the quadrant of the map opposite the opposing agent, and then whatever contiguous partition is closest.

There remains no working strategy for initial separation. However, the equilibrium state is quickly found and maintained. We are highly susceptible to opposing incursions, especially when the opposing agent is located near the middle of the map. Given the small map size, it is often the case that both agents are near the middle and collisions become unavoidable.
An obvious iterative improvement will be adding another partition to cover the middle of the map. Since the opposing player may be a member of more than one partition, the difficulty will be tuning the partition's size.
