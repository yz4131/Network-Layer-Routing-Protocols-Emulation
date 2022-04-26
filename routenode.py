import socket
import sys
import time
import threading
import random
import json


def dv():
    # cost-change thread
    def cost_change(new_cost, table, neighbour, my_port, my_socket, mode):
        # start timer
        time.sleep(30)
        # time out, change cost
        largest_port = sorted(neighbour)[-1]
        neighbour[largest_port] = new_cost
        print("[" + str(time.time()) + "] Node " + str(largest_port) + " cost update to " + str(new_cost))
        # notify this port
        content = " cost-change " + str(my_port) + " " + str(new_cost)
        my_socket.sendto((str(time.time()) + content).encode(), ('', largest_port))
        print("[" + str(time.time()) + "]  Link value message sent from Node " + str(my_port) + " to Node " + str(largest_port))
        # recalculate table
        table[my_port] = {my_port: [0, my_port]}
        for node in table:
            if node == my_port:
                continue
            for des in table[node]:
                if des not in table[my_port]:
                    table[my_port][des] = [table[node][des][0] + neighbour[node], node]
                elif table[node][des][0] + neighbour[node] < table[my_port][des][0]:
                    table[my_port][des] = [table[node][des][0] + neighbour[node], node]
        # send recalculated info
        if mode == 'r':
            content = " " + str(my_port)
            for des in table[my_port]:
                content = content + (" " + str(des) + " " + str(table[my_port][des][0]))
            for receiver in neighbour:
                my_socket.sendto((str(time.time()) + content).encode(), ('', receiver))
                print("[" + str(time.time()) + "] Message sent from Node " + str(my_port) +
                      " to Node " + str(receiver))
        elif mode == 'p':
            for receiver in neighbour:
                content = " " + str(my_port)
                infinity_node = ""
                for des in table[my_port]:
                    if table[my_port][des][1] == receiver and table[my_port][des][1] != des:
                        content = content + (" " + str(des) + " " + str(1000000000))
                        infinity_node = infinity_node + str(des) + " "
                        continue
                    else:
                        content = content + (" " + str(des) + " " + str(table[my_port][des][0]))
                my_socket.sendto((str(time.time()) + content).encode(), ('', receiver))
                print("[" + str(time.time()) + "] Message sent from Node " + str(my_port) +
                      " to Node " + str(receiver))
                if infinity_node != "":
                    print("[" + str(time.time()) + "] Message sent from Node " + str(my_port) +
                          " to Node " + str(receiver) + " with distance to Node " + infinity_node + "as inf.")

    # main thread
    input_len = len(sys.argv)
    my_port = int(sys.argv[4])
    update_time = time.time()
    # initialize distance vector table
    table = {}   # dv
    neighbour = {}  # record neighbour cost c(x,v)
    table[my_port] = {my_port: [0, my_port]}
    mode = sys.argv[2]
    i = 5
    while i < input_len and sys.argv[i] != 'last':
        # format {source: {des: [cost, hop]}}
        table[my_port][int(sys.argv[i])] = [int(sys.argv[i+1]), int(sys.argv[i])]
        neighbour[int(sys.argv[i])] = int(sys.argv[i+1])
        i += 2

    # show status
    print("[" + str(time.time()) + "] Node " + str(my_port) + " Routing Table")
    for source in table:
        for des in table[source]:
            if des != source:
                print("(" + str(table[source][des][0]) + ") " + "-> " + "Node " + str(des))

    # start sending or listening
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind(('', my_port))
    if sys.argv[-1] == 'last' or sys.argv[-2] == 'last':
        content = " " + str(my_port)
        for des in table[my_port]:
            # format: timestamp my_port node1 cost1 node2 cost2 ...
            content = content + (" " + str(des) + " " + str(table[my_port][des][0]))
        for receiver in neighbour:
            my_socket.sendto((str(time.time()) + content).encode(), ('', receiver))
            print("[" + str(time.time()) + "] Message sent from Node " + str(my_port) +
                  " to Node " + str(receiver))

        # cost change
        if sys.argv[-2] == 'last':
            threading.Thread(target=cost_change, args=(int(sys.argv[-1]), table, neighbour, my_port, my_socket, mode)).start()

    # listen
    while True:
        message, address = my_socket.recvfrom(2048)
        message = message.decode()
        message = message.split()
        change = False

        # update neighbour
        if message[1] == 'cost-change':
            neighbour[int(message[2])] = int(message[3])
            print("[" + str(time.time()) + "] Node " + str(message[2]) + " cost update to " + str(message[3]))
            print("[" + str(time.time()) + "] Link value message received at Node " + str(my_port) +
                  " from Node " + message[2])
            continue

        print("[" + str(time.time()) + "] Message received at Node " + str(my_port) +
              " from Node " + message[1])

        # update dv table
        if True:  # check package order
            # update_time = float(message[0])
            sender = int(message[1])
            for i in range(2, len(message), 2):
                if sender not in table:
                    table[sender] = {int(message[i]): [int(message[i+1])]}
                    change = True
                else:
                    if int(message[i]) not in table[sender]:
                        table[sender][int(message[i])] = [int(message[i+1])]
                        change = True
                    else:
                        if table[sender][int(message[i])][0] != int(message[i+1]):
                            table[sender][int(message[i])] = [int(message[i+1])]
                            change = True
            if change:
                # recalculate my_port dv
                table[my_port] = {my_port: [0, my_port]}
                for node in table:
                    if node == my_port:
                        continue
                    for des in table[node]:
                        if des not in table[my_port]:
                            table[my_port][des] = [table[node][des][0] + neighbour[node], node]
                        elif table[node][des][0] + neighbour[node] < table[my_port][des][0]:
                            table[my_port][des] = [table[node][des][0] + neighbour[node], node]

                # send recalculated info
                if mode == 'r':
                    content = " " + str(my_port)
                    for des in table[my_port]:
                        content = content + (" " + str(des) + " " + str(table[my_port][des][0]))
                    for receiver in neighbour:
                        my_socket.sendto((str(time.time()) + content).encode(), ('', receiver))
                        print("[" + str(time.time()) + "] Message sent from Node " + str(my_port) +
                              " to Node " + str(receiver))
                elif mode == 'p':
                    for receiver in neighbour:
                        content = " " + str(my_port)
                        infinity_node = ""
                        for des in table[my_port]:
                            if table[my_port][des][1] == receiver and table[my_port][des][1] != des:
                                content = content + (" " + str(des) + " " + str(1000000000))
                                infinity_node = infinity_node + str(des) + " "
                                continue
                            else:
                                content = content + (" " + str(des) + " " + str(table[my_port][des][0]))
                        my_socket.sendto((str(time.time()) + content).encode(), ('', receiver))
                        print("[" + str(time.time()) + "] Message sent from Node " + str(my_port) +
                              " to Node " + str(receiver))
                        if infinity_node != "":
                            print("[" + str(time.time()) + "] Message sent from Node " + str(my_port) +
                                  " to Node " + str(receiver) + " with distance to Node " + infinity_node + "as inf.")

            # show status
            print("[" + str(time.time()) + "] Node " + str(my_port) + " Routing Table")
            for des in sorted(table[my_port]):
                if des == my_port:
                    continue
                if table[my_port][des][1] == des:
                    print("(" + str(table[my_port][des][0]) + ") " + "-> " + "Node " + str(des))
                else:
                    print("(" + str(table[my_port][des][0]) + ") " + "-> " + "Node " + str(des)
                          + "; Next hop -> Node " + str(table[my_port][des][1]))
            # print(table)


def ls():

    class ThreadWithReturnValue(threading.Thread):
        def __init__(self, group=None, target=None, name=None,
                     args=(), kwargs={}, Verbose=None):
            threading.Thread.__init__(self, group, target, name, args, kwargs)
            self._return = None

        def run(self):
            if self._target is not None:
                self._return = self._target(*self._args,
                                            **self._kwargs)

        def join(self, *args):
            threading.Thread.join(self, *args)
            return self._return

    def show(cost, my_port):
        print("[" + str(time.time()) + '] Node ' + str(my_port) + ' Network topology')
        printed = []
        for source in sorted(cost):
            for des in sorted(cost[source]):
                if (int(source), int(des)) not in printed and (int(des), int(source)) not in printed:
                    print("- (" + str(cost[source][des]) + ") from Node " + str(source) + " to Node " + str(des))
                    printed.append((int(source), int(des)))

    def find_next_hop(ls_table, des, my_port):
        if ls_table[des][1] == int(my_port):
            return des
        p = ls_table[des][1]
        return find_next_hop(ls_table, int(p), int(my_port))

    def show_routing(ls_table, my_port):
        print("[" + str(time.time()) + '] Node ' + str(my_port) + ' Routing Table')
        for des in sorted(ls_table):
            if int(des) != int(my_port):
                if int(des) == int(ls_table[int(des)][1]):
                    print("- (" + str(ls_table[int(des)][0]) + ") -> Node " + str(des))
                else:
                    nh = find_next_hop(ls_table, int(des), int(my_port))
                    print("- (" + str(ls_table[int(des)][0]) + ") -> Node " + str(des) + "; Next hop -> Node "
                          + str(nh))

    def cost_change(ROUTING_INTERVAL):
        # start timer
        time.sleep(1.2*ROUTING_INTERVAL)
        # timeout
        return True

    def listen(my_socket, neighbor, pi):
        message, address = my_socket.recvfrom(2048)
        message = message.decode()
        message = json.loads(message)
        try:
            a = message['cost-change']
            return message
        except:
            receive_from = int(message['sender'])
            receive_seq = int(message['seq'])
            forward = int(message['forward'])

            # only forward this message if it has not been forwarded by myself
            if int(receive_from) not in pi or pi[int(receive_from)] < receive_seq:
                print("[" + str(time.time()) + '] LSA of Node ' + str(receive_from) + ' with sequence number '
                      + str(receive_seq) + ' received from Node ' + str(forward))
                message['forward'] = my_port
                for n in neighbor:
                    if n != int(receive_from):
                        my_socket.sendto(json.dumps(message).encode(), ('', n))
            else:
                print("[" + str(time.time()) + '] DUPLICATE LSA packet Received, AND DROPPED:')
                print('- LSA of Node ' + str(receive_from))
                print('- Sequence number ' + str(receive_seq))
                print('- Received from ' + str(forward))

            return message

    # main thread
    debug = False
    first_cost_change = True
    ROUTING_INTERVAL = 30      # default
    input_len = len(sys.argv)
    my_port = sys.argv[4]
    update_interval = int(sys.argv[3])
    seq = 0     # sequence number
    receive_from = ''            # record who just send me its cost table so that I don't send my table back to it

    # initialize ls table and cost table
    ls_table = {}
    cost = {}
    neighbor = []
    pi = {}      # PI Protocol   record the latest sequence number received
    ls_table[int(my_port)] = [0, None]           # format: {destination: [cost, parent]}
    cost[my_port] = {my_port: 0}
    i = 5
    while i < input_len and sys.argv[i] != 'last':
        # format cost: {source: {des: cost}}
        cost[my_port][sys.argv[i]] = int(sys.argv[i+1])
        neighbor.append(int(sys.argv[i]))
        i += 2

    # socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind(('', int(my_port)))

    # last node
    if sys.argv[-1] == 'last' or sys.argv[-2] == 'last':
        # listen
        t = ThreadWithReturnValue(target=listen, args=(my_socket, neighbor, pi))
        t.start()

        # start
        random_add = random.random()
        first_time = True   # first time, start broadcasting immediately

        # show network topology
        show(cost, my_port)

        # a timer to determine when to perform Dijkstra Algorithm
        timer = time.time()
        dijkstra = False
        first_dijkstra = True

        # cost change
        cc = ThreadWithReturnValue(target=cost_change, args=(ROUTING_INTERVAL,))

        if sys.argv[-2] == 'last':
            cc.start()

        while True:
            change = False    # used to determine whether to show network topology or not

            if cc._return and first_cost_change:
                first_cost_change = False
                largest = sorted(neighbor)[-1]
                cost[my_port][str(largest)] = int(sys.argv[-1])
                cost[str(largest)][my_port] = int(sys.argv[-1])
                print("[" + str(time.time()) + "] Node " + str(largest) + " cost update to " + sys.argv[-1])
                change = True
                m = {'s': my_port, 'd': str(largest), 'cost-change': int(sys.argv[-1])}
                my_socket.sendto(json.dumps(m).encode(), ('', int(largest)))
                print("[" + str(time.time()) + "] Link value message sent from Node " + str(my_port)
                      + " to Node " + str(largest))

            if time.time() - timer >= ROUTING_INTERVAL:
                dijkstra = True

            if t._return:
                receive_from = t.join()['sender']
                receive_seq = t.join()['seq']
                if int(receive_from) in pi:
                    if pi[int(receive_from)] < int(receive_seq):
                        pi[int(receive_from)] = int(receive_seq)
                else:
                    pi[int(receive_from)] = int(receive_seq)

                # update cost
                for source in t.join()['content']:
                    if source not in cost or cost[source] != t.join()['content'][source]:
                        if source != my_port:
                            cost[source] = t.join()['content'][source]
                            change = True

                # restart listening
                t = ThreadWithReturnValue(target=listen, args=(my_socket, neighbor, pi))
                t.start()

            if change is True:
                # show network topology
                show(cost, my_port)

            # calculate the shortest path
            if (dijkstra is True and change is True) or (dijkstra is True and first_dijkstra is True):
                N = set()
                N.add(int(my_port))
                M = set()
                for node in cost:
                    M.add(int(node))
                    if int(node) in neighbor:
                        ls_table[int(node)] = [cost[my_port][node], int(my_port)]
                    elif int(node) not in neighbor and int(node) != int(my_port):
                        ls_table[int(node)] = [float('inf'), None]
                while N != M:
                    shortest = float('inf')
                    for node in M - N:
                        if ls_table[int(node)][0] < shortest:
                            shortest = ls_table[int(node)][0]
                            minimum = int(node)
                    N.add(minimum)
                    for n in cost[str(minimum)]:
                        if int(n) in N:
                            continue
                        if ls_table[int(n)][0] < ls_table[int(minimum)][0] + cost[str(minimum)][str(n)]:
                            continue
                        else:
                            ls_table[int(n)] = [ls_table[int(minimum)][0] + cost[str(minimum)][str(n)], int(minimum)]
                first_dijkstra = False
                show_routing(ls_table, my_port)

                if debug is True:
                    quit()

            # broadcast
            if first_time or time.time() - start_time >= update_interval + random_add:
                first_time = False
                msg = {'seq': seq, 'sender': my_port, 'forward': my_port, 'content': cost}
                msg = json.dumps(msg)
                for n in neighbor:
                    my_socket.sendto(msg.encode(), ('', n))
                    print("[" + str(time.time()) + '] LSA of Node ' + str(my_port) + ' with sequence number '
                          + str(seq) + ' sent to Node ' + str(n))

                seq += 1
                start_time = time.time()

    # other nodes
    else:
        # listen
        t = ThreadWithReturnValue(target=listen, args=(my_socket, neighbor, pi))
        t.start()

        # wait for last node start broadcasting
        while True:
            if t._return:
                break

        # start
        start_time = time.time()
        random_add = random.random()

        # show network topology
        show(cost, my_port)

        # a timer to determine when to perform Dijkstra Algorithm
        timer = time.time()
        dijkstra = False
        first_dijkstra = True

        while True:
            if time.time() - timer >= ROUTING_INTERVAL:
                dijkstra = True

            change = False    # used to determine whether to show network topology or not
            if t._return:
                try:
                    new_cost = t.join()['cost-change']
                    s = t.join()['s']
                    d = t.join()['d']
                    cost[s][d] = new_cost
                    cost[d][s] = new_cost
                    change = True
                    print("[" + str(time.time()) + "] Node " + str(s) + " cost update to " + str(new_cost))
                    print("[" + str(time.time()) + "]  Link value message received at Node " + str(my_port) +
                          " from Node " + s)
                except:
                    receive_from = t.join()['sender']
                    receive_seq = t.join()['seq']
                    if int(receive_from) in pi:
                        if pi[int(receive_from)] < int(receive_seq):
                            pi[int(receive_from)] = int(receive_seq)
                    else:
                        pi[int(receive_from)] = int(receive_seq)

                    # update cost
                    for source in t.join()['content']:
                        if source not in cost or cost[source] != t.join()['content'][source]:
                            if source != my_port:
                                cost[source] = t.join()['content'][source]
                                change = True

                # restart listening
                t = ThreadWithReturnValue(target=listen, args=(my_socket, neighbor, pi))
                t.start()

            if change is True:
                # show network topology
                show(cost, my_port)

            # calculate the shortest path
            if (dijkstra is True and change is True) or (dijkstra is True and first_dijkstra is True):
                N = set()
                N.add(int(my_port))
                M = set()
                for node in cost:
                    M.add(int(node))
                    if int(node) in neighbor:
                        ls_table[int(node)] = [cost[my_port][node], int(my_port)]
                    elif int(node) not in neighbor and int(node) != int(my_port):
                        ls_table[int(node)] = [float('inf'), None]
                while N != M:
                    shortest = float('inf')
                    for node in M - N:
                        if ls_table[int(node)][0] < shortest:
                            shortest = ls_table[int(node)][0]
                            minimum = int(node)
                    N.add(minimum)
                    for n in cost[str(minimum)]:
                        if int(n) in N:
                            continue
                        if ls_table[int(n)][0] < ls_table[int(minimum)][0] + cost[str(minimum)][str(n)]:
                            continue
                        else:
                            ls_table[int(n)] = [ls_table[int(minimum)][0] + cost[str(minimum)][str(n)], int(minimum)]
                first_dijkstra = False
                show_routing(ls_table, my_port)

                if debug is True:
                    quit()

            # broadcast
            if time.time() - start_time >= update_interval + random_add:
                msg = {'seq': seq, 'sender': my_port, 'forward': my_port,'content': cost}
                msg = json.dumps(msg)
                for n in neighbor:
                    my_socket.sendto(msg.encode(), ('', n))
                    print("[" + str(time.time()) + '] LSA of Node ' + str(my_port) + ' with sequence number '
                          + str(seq) + ' sent to Node ' + str(n))
                seq += 1
                start_time = time.time()


if __name__ == "__main__":
    if sys.argv[1] == 'dv':
        try:
            dv()
        except:
            print('Error: Invalid Input or Internal Error')
            print('Correct Usage: ')
            print('1. Distance Vector: ')
            print('python3 routenode.py dv <r/p> 0 <local-port> '
                  '<neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>] ')
            print('2. Link State: ')
            print('python3 routenode.py ls r <update-interval> <local-port> '
                  '<neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>] ')

    elif sys.argv[1] == 'ls':
        if 1 <= int(sys.argv[3]) <= 5:
            try:
                ls()
            except:
                print('Error: Invalid Input or Internal Error')
                print('Correct Usage: ')
                print('1. Distance Vector: ')
                print('python3 routenode.py dv <r/p> 0 <local-port> '
                      '<neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>] ')
                print('2. Link State: ')
                print('python3 routenode.py ls r <update-interval> <local-port> '
                      '<neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>] ')
        else:
            print("Error: <update-interval> should be 1-5")

    else:
        print('Error: Invalid Input')
        print('Correct Usage: ')
        print('1. Distance Vector: ')
        print('python3 routenode.py dv <r/p> 0 <local-port> '
              '<neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>] ')
        print('2. Link State: ')
        print('python3 routenode.py ls r <update-interval> <local-port> '
              '<neighbor1-port> <cost-1> <neighbor2-port> <cost-2> .. [last] [<cost-change>] ')

