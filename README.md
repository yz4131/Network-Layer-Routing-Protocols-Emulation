# Network Layer Routing Protocols Emulation - Distance Vector / Link State

Name: Yuqin Zhao
UNI: yz4131

Running Instructions:
+ 1. Run Distance Vector Regular Mode:
  python3 routenode.py dv <r> 0 <local-port> <neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>]
+ 2. Run Distance Vector Poison Reverse Mode:
  python3 routenode.py dv <p> 0 <local-port> <neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>]
+ 3. Run Link State Mode:
  python3 routenode.py ls <r> <update-interval> <local-port> <neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>]

routenode: Program name.
+ dv: run the distance vector algorithm
+ r/p: Mode of program - Regular or Poisoned Reverse.
+ update-interval: Not used (will be used in the LS section) - can be any value between 1-5
+ local-port: The UDP listening port number (1024-65534) of the node.
+ neighbor#-port: The UDP listening port number (1024-65534) of one of the neighboring nodes.
+ cost-#: This will be used as the link distance to the neighbor#-port. It is an integer that represents the cost/weight of the link.
+ last: Indication of the last node information of the network. This arg as optional. Upon the input of the command with this argument, the routing message exchanges among the nodes kick in.
+ cost-change: Indication of the new cost that will be assigned to the link between the last node and its neighbor with the highest port number. This arg as optional.
+ ctrl+C (exit): Use ctrl+C to exit the program.

Features:
+ 1. Capable of running Distance Vector Routing Algorithms
+ 2. Capable of running Link State Routing Algorithms
+ 3. Capable of emulating the "count to infinity" problem of Distance Vector Routing Algorithms under the "Regular Mode"
+ 4. Capable of handling the "count to infinity" problem of Distance Vector Routing Algorithms under the "Poisoned Reverse Mode"

Algorithms:
+ 1. Multithreading:  Used for listening for incoming message, set timer for cost-change
+ 2. Under Distance Vector Regular Mode, every node keep the routing information of itself and its neighbors. Once the last node's information is entered, every node start sharing its own routing information and forwarding others' information. Each node will only forward the same information once and new messages are sent only when a node's routing table is updated. Hence after a while, the algorithm will converge and everyone has enough information to send any packets to any destination.
+ 3. Under Distance Vector Poisoned Reverse Mode, when a node is sharing its routing table, if this node is using another node, say node x, to get to the destination, this node will not tell node x that it can get to the destination so that node x will not use this node to get to the destination. Therefore, "count to infinity" problem is solved.
+ 4. Under Link State Mode, all nodes first starting to flooding the network, sharing their link state table to all neighbors. The broadcast will last forever and after a while, every node will get to obtain the entire topology of the network. When timeout, all nodes start using the topology of the network to calculate the shortest path to every node, by Dijkstra Algorithm. All nodes are not only capable of calculating the minimal cost to every other nodes, but also capable of obtaining the shortest path to other nodes. calculating the shortest path is realized by recording the "parent" of every destination and backtracking.

Data Structure:
+ 1. Python Dictionary
+ 2. Python List

Known Bugs:
+ To be discovered
