from ogdf_python import ogdf, cppinclude, cppyy
import math
from pulp import *
cppinclude("ogdf/basic/graph_generators/deterministic.h")
cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")
cppinclude("ogdf/basic/graph_generators/deterministic.h")
cppinclude("ogdf/energybased/FMMMLayout.h")
#functions to draw the graph

def add_bends(line, *points):
    for point in points:
        line.pushBack(ogdf.DPoint(*point))

def find_wrap(GA, e):
    s,t = e.source(), e.target()
    wrap_h = GA.x[t] < GA.x[s]
    wrap_v = GA.y[t] < GA.y[s]
    if wrap_h and wrap_v:
        delta_x = abs(GA.x[t] - GA.x[s])
        delta_y = abs(GA.y[t] - GA.y[s])
        if delta_x > delta_y:
            wrap = "hv"
        else:
            wrap = "vh"
    elif wrap_h:
        wrap = "h"
    elif wrap_v:
        wrap = "v"
    else:
        wrap = ""
    return wrap

def apply_wrap(GA, box, e, wrap, margin=50):
    if not wrap:
        return
    
    s,t = e.source(), e.target()
    left = box.p1().m_x
    top = box.p1().m_y
    right = box.p2().m_x
    bottom = box.p2().m_y
    
    GA.bends[e].clear()
    if wrap[0] == "h":
        add_bends(GA.bends[e],
            (right + margin, GA.y[s]),
            (right + margin, top - margin),
            (left - margin, top - margin),
            (left - margin, GA.y[t]),
        )
    elif wrap[0] == "v":
        add_bends(GA.bends[e],
            (GA.x[s], bottom + margin),
            (left - margin, bottom + margin),
            (left - margin, top - margin),
            (GA.x[t], top - margin),
        )


def layout_edges(GA, box):
    wraps = ogdf.EdgeArray[str](GA.constGraph(), "")
    wraps_h = []
    wraps_v = []
    for e in GA.constGraph().edges:
        w = wraps[e] = find_wrap(GA, e)
        if w and w[0] == "h":
            wraps_h.append(e)
        elif w and w[0] == "v":
            wraps_v.append(e)
    wraps_h.sort(key=lambda e: GA.y[e.source()])
    wraps_v.sort(key=lambda e: GA.x[e.source()])
    
    for nr, e in enumerate(wraps_h + wraps_v):
        # GA.arrowType[e] = getattr(ogdf.EdgeArrow, "None")
        apply_wrap(GA, box, e, wraps[e], 50 + nr * 5)
        if wraps[e] in ["hv", "vh"]:
            GA.strokeColor[e] = ogdf.Color(0,255,0)
        elif wraps[e] == "h":
            GA.strokeColor[e] = ogdf.Color(255,0,0)
        elif wraps[e] == "v":
            GA.strokeColor[e] = ogdf.Color(0,0,255)
        
    return GA, wraps

def draw_bounding_box(G, GA, box):
    box_node1 = G.newNode()
    box_node2 = G.newNode()
    GA.x[box_node1] = box.p1().m_x - 25
    GA.y[box_node1] = box.p1().m_y - 25
    GA.x[box_node2] = box.p2().m_x + 25
    GA.y[box_node2] = box.p2().m_y + 25
    GA.width[box_node1] = 0
    GA.height[box_node1] = 0
    GA.width[box_node2] = 0
    GA.height[box_node2] = 0
    box_edge1 = G.newEdge(box_node1, box_node2)
    box_edge2 = G.newEdge(box_node1, box_node2)
    add_bends(GA.bends[box_edge1], (box.p1().m_x - 25, box.p2().m_y + 25))
    add_bends(GA.bends[box_edge2], (box.p2().m_x + 25, box.p1().m_y - 25))


#functions to create embedding
def adjList(G,GA):
    
    adjList = {}
    
    for n in G.nodes:
        
        #adjList[GA.label[n]] = {}
        adjList[n] = {}
        
        for adj in n.adjEntries:
            
            e = adj.theEdge()
            wrap = find_wrap(GA, e)
            print("line117",G,n,e)
            if n == e.source():
                
                if wrap == "h" or wrap == "hv":
                    position = 1
                    
                elif wrap == "v" or wrap == "vh":
                    position = 2
                    
                else:
                    if GA.x[n] == GA.x[adj.twinNode()]:
                        position = 2
                        
                    if GA.y[n] == GA.y[adj.twinNode()]:
                        position = 1
        
                #adjList[GA.label[n]][position] = GA.label[adj.twinNode()]  #uncomment to use node labels
                adjList[n][position] = adj
                        
            else:
                
                if wrap == "h" or wrap == "hv":
                    position = 3
                    
                elif wrap == "v" or wrap == "vh":
                    position = 0
                    
                else:
                    if GA.x[n] == GA.x[adj.twinNode()]:
                        position = 0
                        
                    if GA.y[n] == GA.y[adj.twinNode()]:
                        position = 3
                        
                #adjList[GA.label[n]][position] = GA.label[adj.twinNode()]  #uncomment to use node labels
                adjList[n][position] = adj
            print("line153",n.index(),adjList[n])
            
    return adjList


def sorted_adjList(adjList):
    
    sorted_adjList = {}
    
    for n in adjList:
        
        sortedList = []
        
        for i in sorted (adjList[n]) :
            
            sortedList.append(adjList[n][i])
        
        sorted_adjList[n] = sortedList
    
    return sorted_adjList
    

    
def sortAdjs(node, order):
    l = ogdf.List["ogdf::adjEntry"]()
    for adj in order:
        l.pushBack(adj)
    node.adjEntries.sort(l)

#function to compute the dual
def dualGraph(G):
    dualG = ogdf.Graph()
    # maps G.adjEntry -> dualG.node (face)
    dualFace = ogdf.AdjEntryArray["ogdf::node"](G, cppyy.bind_object(cppyy.nullptr, "ogdf::NodeElement"))
    # maps G.edge -> dualG.edge
    dualEdge = ogdf.EdgeArray["ogdf::edge"](G, cppyy.bind_object(cppyy.nullptr, "ogdf::EdgeElement"))
    # maps dualG.edge -> G.edge (== dualEdge^{-1})
    primalEdge = ogdf.EdgeArray["ogdf::edge"](dualG, cppyy.bind_object(cppyy.nullptr, "ogdf::EdgeElement"))

    for n in G.nodes:
        for adj in n.adjEntries:
            if dualFace[adj]:
                continue
            face = dualG.newNode()
            dualFace[adj] = face
        
            a = adj.faceCycleSucc()
            while a != adj:
                dualFace[a] = face
                a = a.faceCycleSucc()

    for e in G.edges:
        de = dualG.newEdge(dualFace[e.adjSource()], dualFace[e.adjTarget()])
        dualEdge[e] = de
        primalEdge[de] = e

    return dualG, primalEdge

#function to compute the spanning trees
def spanningTrees(G, dualG, GA, primalEdge):
    
    for e in G.edges:
        GA.strokeColor[e] = ogdf.Color(0,0,0)

    # type of G edges: 0 (black) is in X, 1 (red) is edge of spanning cotree, 2 (green) is edge of primal ST
    tree = ogdf.EdgeArray[int](G, 0)

    found = ogdf.NodeArray[bool](dualG, False)
    first_node = next(iter(dualG.nodes))
    found[first_node] = True
    todo = list(first_node.adjEntries)
    count = 1
    while len(todo) > 0:
        cur = todo.pop(-1)
        if found[cur.twinNode()]:
            continue

        tree[primalEdge[cur.theEdge()]] = 1
        GA.strokeColor[primalEdge[cur.theEdge()]] = ogdf.Color(255,0,0)
        found[cur.twinNode()] = True
        count += 1

        for adj in cur.twinNode().adjEntries:
            if not found[adj.twinNode()]:
                todo.append(adj)
    #print("line 238",count, dualG.numberOfNodes())
    
    found = ogdf.NodeArray[bool](G, False)
    first_node = next(iter(G.nodes))
    found[first_node] = True
    todo = list(first_node.adjEntries)
    count = 1
    while len(todo) > 0:
        cur = todo.pop(-1)
        if found[cur.twinNode()] or tree[cur] != 0:
            continue

        tree[cur.theEdge()] = 2
        GA.strokeColor[cur.theEdge()] = ogdf.Color(0,255,0)
        found[cur.twinNode()] = True
        count += 1

        for adj in cur.twinNode().adjEntries:
            if not found[adj.twinNode()] and tree[adj.theEdge()] == 0:
                todo.append(adj)
    return tree


#find a list of bends of an edge
def bendCoord(GA,e):
  
    print("line 271",GA.bends,e)
      
    bends = [(b.m_x,b.m_y) for b in GA.bends[e]]
    return bends

#find angle relative to a node (180 'West', 90 'North', 0 'East', -90 'South')
def findAngle(GA, node,x,y): #angle relative to the current node 
    refx = GA.x[node]
    refy = GA.y[node]
    rad = math.atan2(refy-y,x-refx)
    deg = math.degrees(rad)
    return deg

#find turn relative to refNode left -1/right 1 /straight 0
def findDirection(GA,refNode,e1,e2): 
    
    if len(bendCoord(GA,e1)) != 0:
                    
        if e1.target() == refNode:
                    
            bendpoint = bendCoord(GA,e1)[-1]
            bendpointx = bendpoint[0]
            bendpointy = bendpoint[1]
            
                    
            a1 = findAngle(GA,refNode,bendpointx,bendpointy)
                        
        else:
            
            bendpoint = bendCoord(GA,e1)[0]
            bendpointx = bendpoint[0]
            bendpointy = bendpoint[1]
           
                    
            a1 = findAngle(GA,refNode,bendpointx,bendpointy)
                        
    else:
        if e1.target() == refNode:
            nextNode = e1.source()
            a1 = findAngle(GA,refNode,GA.x[nextNode],GA.y[nextNode])
        else:
            nextNode = e1.target()
            a1 = findAngle(GA,refNode,GA.x[nextNode],GA.y[nextNode])
        
    if len(bendCoord(GA,e2)) != 0:
               
        if e2.target() == refNode:
            bendpoint = bendCoord(GA,e2)[-1]
            bendpointx = bendpoint[0]
            bendpointy = bendpoint[1]
                    
            a2 = findAngle(GA,refNode,bendpointx,bendpointy)
                        
        else:
            bendpoint = bendCoord(GA,e2)[0]
            bendpointx = bendpoint[0]
            bendpointy = bendpoint[1]
                    
            a2 = findAngle(GA,refNode,bendpointx,bendpointy)
                        
    else:
        if e2.target() == refNode:
            nextNode = e2.source()
            a2 = findAngle(GA,refNode,GA.x[nextNode],GA.y[nextNode])
           
        else:
            nextNode = e2.target()
            a2 = findAngle(GA,refNode,GA.x[nextNode],GA.y[nextNode])
            
    
    if a1 == 180: 
        if a2 == 90:
            direction = -1
        elif a2 == 0:
            direction = 0
        elif a2 == -90:
            direction = 1
            
    elif a1 == -90:
        if a2 == 90:
            direction = 0
        elif a2 == 0:
            direction = 1
        elif a2 == 180:
            direction = -1
            
    elif a1 == 90:
        if a2 == -90:
            direction = 0
        elif a2 == 0:
            direction = -1
        elif a2 == 180:
            direction = 1
            
    elif a1 == 0:
        if a2 == -90:
            direction = -1
        elif a2 == 90:
            direction = 1
        elif a2 == 180:
            direction = 0
    #print(a1,a2)
    return direction

#vertical or horizontal (0/1)
def defineOrientation(GA,refEdge,refNode,refOrientation, orientation): 
    
    
    if len(bendCoord(GA,refEdge)) != 0:
        if refEdge.target() == refNode:          
            bendpoint = bendCoord(GA,refEdge)[-1]
            bendpointx = bendpoint[0]
            bendpointy = bendpoint[1]
                    
            refAngle = findAngle(GA,refNode,bendpointx,bendpointy)
                        
        else:
            bendpoint = bendCoord(GA,refEdge)[0]
            bendpointx = bendpoint[0]
            bendpointy = bendpoint[1]
                    
            refAngle = findAngle(GA,refNode,bendpointx,bendpointy)
                        
    else:
        if refEdge.target() == refNode:        
            refAngle = findAngle(GA,refNode,GA.x[refEdge.source()],GA.y[refEdge.source()])
                        
        else:         
            refAngle = findAngle(GA,refNode,GA.x[refEdge.target()],GA.y[refEdge.target()])
        
    
    
    for adj in refNode.adjEntries:
        e= adj.theEdge()
        nextNode = adj.twinNode()
        #print(refNode.index(),nextNode.index())
        if e!= refEdge:
            if orientation[e] == 0 or orientation [e] == 1: #to distinguish vertical 1 and horizontal 0
                #print("this edge is done")
                continue
                
            else:
                if len(bendCoord(GA,e)) != 0:
                    #print("has bend")
                    if e.target() == refNode:
                    
                        bendpoint = bendCoord(GA,e)[-1]
                        bendpointx = bendpoint[0]
                        bendpointy = bendpoint[1]
                    
                        angle = findAngle(GA,refNode,bendpointx,bendpointy)
                        
                    else:
                        bendpoint = bendCoord(GA,e)[0]
                        bendpointx = bendpoint[0]
                        bendpointy = bendpoint[1]
                    
                        angle = findAngle(GA,refNode,bendpointx,bendpointy)
                        
                else:
                    angle = findAngle(GA,refNode,GA.x[nextNode],GA.y[nextNode])
                    
            
            if abs(angle)%180 == abs(refAngle)%180:
                orientation[e] = refOrientation
                    
            else: 
                orientation[e] = 1-refOrientation
                    
            
                    
            defineOrientation(GA,e,nextNode,orientation[e],orientation)
    
    return
   
        
#find the edges in a generator       
def bfs_findGenerator(tree,target, queue, done = [], path = {}):
    print("line 423", target.index(),queue)
    while queue:
        
        try:
            currEdge = queue[0][0].theEdge()
            
            (currAdj, currNode) = queue.pop(0)
            currEdge = currAdj.theEdge()
            path[currNode] = []
            done.append(currEdge)
        except:
            (currEdge, currNode) = queue.pop(0)
            path[currNode] = []
            done.append(currEdge)

        print("line438",currNode.index())
        for adj in currNode.adjEntries:
            e = adj.theEdge()
            print("line441",e, tree[e])
            if e not in done and tree[e] == 2:
                path[currNode].append(adj)
                #print("curr node:", currNode.index())
                #print("adj:", adj.theEdge().source().index(),adj.theEdge().target().index())
                if adj.twinNode() == target:
                    #print("found target", adj.twinNode().index())
                    return path
            
                queue.append((e, adj.twinNode()))
                
    print("no path found")
        
def checkCoeff(loop, variableList):
    if len(loop) > 0:
        sum = 0
        for e in loop:
            sum += variableList[e]
            
        if sum < 0:
            rhs = -1
        else:
            rhs = 1
            
    else:
        rhs = 0
        
    return rhs


#find signs of edges in each loop
def findSigns(GA,alphaLoop, betaLoop, orientation):
    #give an orientation to each edge
    alphaLoopVertical = []
    alphaLoopHorizontal = []
    signs1 = {}
    flags = {}
    prev_turn = 999
    for i, e in enumerate(alphaLoop):
    
        if i < len(alphaLoop)-1:
            #ei = alphaLoop[i]
            ei1 = alphaLoop[i+1]           
        else:
            #ei = alphaLoop[i]
            ei1 = alphaLoop[0]
            
        turn = findDirection(GA,e.commonNode(ei1),e,ei1)
    
        if prev_turn == 999:
            flag = 1 
            sign = 1
            flags[1] = sign
        elif turn !=0 and turn == prev_turn:
            flag = -1*flag
            sign = -1*flags[flag]
            flags[flag] = sign
        elif turn !=0 and turn != prev_turn:
            flag = -1*flag
            if flag in flags:
                sign = flags[flag]
            else:
                flags[flag] = 1
                sign =1
        else:
            sign = flags[flag]
            
        
        if orientation[e] == 1:
            alphaLoopHorizontal.append(e)
        else:
            alphaLoopVertical.append(e)
    
        signs1[ei1] = sign
    
        prev_turn = turn
        #prev_sign = sign
    
        #print(ei1.source().index(),ei1.target().index(), signs1[ei1])

    betaLoopVertical = []
    betaLoopHorizontal = []
    signs2 = {}
    flags = {}
    prev_turn = 999
    for i, e in enumerate(betaLoop):
    
        if i < len(betaLoop)-1:
            #ei = betaLoop[i]
            ei1 = betaLoop[i+1]           
        else:
            ei = betaLoop[i]
            ei1 = betaLoop[0]
            
        turn = findDirection(GA,e.commonNode(ei1),e,ei1)
    
        if prev_turn == 999:
            flag = 1 
            sign = 1
            flags[1] = sign
        elif turn !=0 and turn == prev_turn:
            flag = -1*flag
            sign = -1*flags[flag]
            flags[flag] = sign
        elif turn !=0 and turn != prev_turn:
            flag = -1*flag
            if flag in flags:
                sign = flags[flag]
            else:
                flags[flag] = 1
                sign =1
        else:
            sign = flags[flag]
            
        
        if orientation[e] == 1:
            betaLoopHorizontal.append(e)
        else:
            betaLoopVertical.append(e)
    
        signs2[ei1] = sign
    
        prev_turn = turn
        #prev_sign = sign
    
        #print(ei1.source().index(),ei1.target().index(), signs2[ei1])

    return signs1, signs2, alphaLoopVertical, alphaLoopHorizontal, betaLoopVertical, betaLoopHorizontal





def LP(n):

    #Initial grid graph
    width = n
    height = n

    G = ogdf.Graph()
    ogdf.gridGraph(G, width, height, True, True)
    GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
    GA.destroyAttributes(ogdf.GraphAttributes.nodeId)

    for n in G.nodes:
        GA.label[n] = str(n.index())
        GA.x[n] = (n.index() % width) * 50 
        GA.y[n] = (n.index() // height) * 50
        #print("line614",n.index())
    box = GA.boundingBox()
    GA, wraps = layout_edges(GA, box)
    print("line 591", G,GA)
    #create embedding
    result = adjList(G, GA)
    Sorted_adjList = sorted_adjList(result)

    for n in Sorted_adjList:
        
        node_adjEntries = Sorted_adjList[n]
        sortAdjs(n, node_adjEntries)
        print("line626",n.index(), [(e.theEdge().source().index(),e.theEdge().target().index()) for e in n.adjEntries])

    #dual tree and spanning trees
    dualG, primalEdge = dualGraph(G)
    tree = spanningTrees(G, dualG, GA, primalEdge)
    #print("line 605", type(tree))
    #the black edges that must be included in each generator
    starter_edges = [e for e in G.edges if tree[e] == 0]
    start_edge0 = starter_edges[0]
    target0 = start_edge0.target()
    source0 =  start_edge0.source()
    print("line611",source0.index(), target0.index())
    queue = [(start_edge0, target0)]
    path0 = bfs_findGenerator(tree,source0, queue, done = [], path = {})
    betaLoop = []
    betaLoop.append(start_edge0)
    prev_node = None

    for e in reversed(path0):
        if prev_node == None:
            #print(e.index(), path0[e][-1].theEdge().source().index(),path0[e][-1].theEdge().target().index())
            betaLoop.append(path0[e][-1].theEdge())
            prev_node = e
        else:
            for adj in path0[e]:
                if adj.twinNode() == prev_node:
                    betaLoop.append(adj.theEdge())
                    print(adj.twinNode().index())
                    prev_node = e
                    break
    '''
    print("beta loop")
    for i, e in enumerate(betaLoop):
        print(betaLoop[i].source().index(),betaLoop[i].target().index())
    '''
        

    start_edge1 = starter_edges[1]
    target1 = start_edge1.target()
    source1 =  start_edge1.source()
    #print(source1.index(), target1.index())
    queue = [(start_edge1, target1)]
    path1 = bfs_findGenerator(tree,source1, queue, done = [], path = {})
    alphaLoop = []
    alphaLoop.append(start_edge1)
    prev_node = None

    for e in reversed(path1):
        if prev_node == None:
            alphaLoop.append(path1[e][-1].theEdge())
            prev_node = e
        else:
            for adj in path1[e]:
                if adj.twinNode() == prev_node:
                    alphaLoop.append(adj.theEdge())
                    prev_node = e
                    break
    '''
    print("alpha loop")
    for i, e in enumerate(alphaLoop):
        print(alphaLoop[i].source().index(),alphaLoop[i].target().index())
    '''

    orientation = ogdf.EdgeArray[int](G,99)
    print("line 690",start_edge0,start_edge0.source())
    defineOrientation(GA,start_edge0,start_edge0.source(),0,orientation)
    signs1, signs2, alphaLoopVertical, alphaLoopHorizontal, betaLoopVertical, betaLoopHorizontal = findSigns(GA,alphaLoop, betaLoop, orientation)

    ##Setting variable names

    alphaVerticalDecisionVariables = {}
    betaVerticalDecisionVariables = {}
    alphaHorizontalDecisionVariables = {}
    betaHorizontalDecisionVariables = {}

    for i, e in enumerate(alphaLoopVertical):
        var = LpVariable('eav' + str(i) ,lowBound = 0.1) 
        alphaVerticalDecisionVariables[e] = var
        
        if e in betaLoopVertical:
            betaVerticalDecisionVariables[e] = var
        
    for i, e in enumerate(betaLoopVertical):
        var = LpVariable('ebv' + str(i) ,lowBound = 0.1) 
        if e not in alphaLoopVertical:
            betaVerticalDecisionVariables[e] = var

    for i, e in enumerate(alphaLoopHorizontal):
        var = LpVariable('eah' + str(i) ,lowBound = 0.1) 
        alphaHorizontalDecisionVariables[e] = var
        
        if e in betaLoopHorizontal:
            betaHorizontalDecisionVariables[e] = var
        
    for i, e in enumerate(betaLoopHorizontal):
        var = LpVariable('ebh' + str(i) ,lowBound = 0.1) 
        #print(e.source().index(),e.target().index())
        if e not in alphaLoopHorizontal:
            #print(e.source().index(),e.target().index())
            betaHorizontalDecisionVariables[e] = var
            
    #Set RHS values
    beta_horz_rhs = 0
    if len(betaHorizontalDecisionVariables) != 0:
        for e in betaHorizontalDecisionVariables:
            if find_wrap(GA,e) != "":
                beta_horz_rhs += 1

    alpha_horz_rhs = 0
    if len(alphaHorizontalDecisionVariables) != 0: 
        for e in alphaHorizontalDecisionVariables:
            if find_wrap(GA,e) != "":
                alpha_horz_rhs += 1
            
    beta_ver_rhs = 0
    if len(betaVerticalDecisionVariables) != 0:
        for e in betaVerticalDecisionVariables:
            if find_wrap(GA,e) != "":
                beta_ver_rhs += 1
            
    alpha_ver_rhs = 0
    if len(alphaVerticalDecisionVariables) != 0:
        for e in alphaVerticalDecisionVariables:
            if find_wrap(GA,e) != "":
                alpha_ver_rhs += 1
            


    #set up LP
    setOfVariables = set(list(betaHorizontalDecisionVariables.values()) + list(alphaHorizontalDecisionVariables.values()) +list(betaVerticalDecisionVariables.values())+list(alphaVerticalDecisionVariables.values()))

    model= LpProblem("Network Flow Problem", LpMinimize)

    # The objective function
    model += lpSum([e for e in setOfVariables]), "Sum of flow across all edges"

    # Constraints, if there are more edges going the 'opposite' direction we multiply it by -1 so that a solution exists
    if checkCoeff(betaLoopHorizontal, signs2) == 1:  
        model += lpSum([signs2[e]*betaHorizontalDecisionVariables[e] for e in betaHorizontalDecisionVariables.keys() ]) == beta_horz_rhs, "Sum of flow across all horizontal edges in beta loop"    
    elif checkCoeff(betaLoopHorizontal, signs2) == -1:  
        model += lpSum([signs2[e]*betaHorizontalDecisionVariables[e] for e in betaHorizontalDecisionVariables.keys() ]) == -1*beta_horz_rhs, "Sum of flow across all horizontal edges in beta loop"
        
    if checkCoeff(alphaLoopVertical, signs1) == 1:  
        model += lpSum([signs1[e]*alphaVerticalDecisionVariables[e] for e in alphaVerticalDecisionVariables.keys() ]) == alpha_ver_rhs, "Sum of flow across all vertical edges in alpha loop"
    elif checkCoeff(alphaLoopVertical, signs1) == -1:  
        model += lpSum([signs1[e]*alphaVerticalDecisionVariables[e] for e in alphaVerticalDecisionVariables.keys() ]) == -1*alpha_ver_rhs, "Sum of flow across all vertical edges in alpha loop"

    if checkCoeff(betaLoopVertical, signs2) == 1:    
        model += lpSum([signs2[e]*betaVerticalDecisionVariables[e] for e in betaVerticalDecisionVariables.keys() ]) == beta_ver_rhs, "Sum of flow across all vertical edges in beta loop"
    else:
        model += lpSum([signs2[e]*betaVerticalDecisionVariables[e] for e in betaVerticalDecisionVariables.keys() ]) == -1*beta_ver_rhs, "Sum of flow across all vertical edges in beta loop"

    if checkCoeff(alphaLoopHorizontal, signs1) == 1: 
        model += lpSum([signs1[e]*alphaHorizontalDecisionVariables[e] for e in alphaHorizontalDecisionVariables.keys() ]) == alpha_horz_rhs, "Sum of flow across all horizontal edges in alpha loop"
    else:
        model += lpSum([signs1[e]*alphaHorizontalDecisionVariables[e] for e in alphaHorizontalDecisionVariables.keys() ]) == -1*alpha_horz_rhs, "Sum of flow across all horizontal edges"
        

    restDecisionVariables = {}
    edge_set_list = []
    for i,n in enumerate(G.nodes):
        
        for k,adj in enumerate(n.adjEntries):
            lhs1 = []
            rhs1 = []
            lhs0 = []
            rhs0 = []
            edge_set = set()
            e = adj.theEdge()
            edge_set.add(e)
            list = lhs1
            list.append(e)
            orig_adj = adj
            #print("current edge",e.source().index(),e.target().index())
            
            while True:
                
                next_adj = adj.faceCycleSucc()
                next_e = next_adj.theEdge()
                edge_set.add(next_e)
                #print("next edge", next_e.source().index(),next_e.target().index(),orientation[next_e])
                
                if next_adj == orig_adj:
                    break
                    
                if orientation[next_e] == orientation[e]:
                    list.append(next_e)
                    
                else:
                    if lhs0 == []:
                        lhs0.append(next_e)
                        list = lhs0
                    elif rhs1 == []:
                        rhs1.append(next_e)
                        list = rhs1
                    elif rhs0 == []:
                        rhs0.append(next_e)
                        list = rhs0
                    else:
                        lhs1.append(next_e)
                        list = lhs1


                e = next_e
                adj = next_adj
        
            if edge_set in edge_set_list:
                continue
            else:
                edge_set_list.append(edge_set)       
            
            #print("rhs0")
            #[print(e.source().index(),e.target().index()) for e in rhs0]
            #print("lhs0")
            #[print(e.source().index(),e.target().index()) for e in lhs0]
            #print("rhs1")
            #[print(e.source().index(),e.target().index()) for e in rhs1]
            #print("lhs1")
            #[print(e.source().index(),e.target().index()) for e in lhs1]
            for j, e in enumerate(lhs1):
                if e in restDecisionVariables:
                    pass      
                elif e in alphaHorizontalDecisionVariables:
                    varName = alphaHorizontalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in alphaVerticalDecisionVariables:
                    varName = alphaVerticalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in betaHorizontalDecisionVariables:
                    varName = betaHorizontalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in betaVerticalDecisionVariables:
                    varName = betaVerticalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                else:
                    varName = LpVariable('e11' + str(i) + str(k) + str(j) ,lowBound = 0.1) 
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                
            for j,e in enumerate(rhs1):
                if e in restDecisionVariables:
                    pass      
                elif e in alphaHorizontalDecisionVariables:
                    varName = alphaHorizontalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in alphaVerticalDecisionVariables:
                    varName = alphaVerticalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in betaHorizontalDecisionVariables:
                    varName = betaHorizontalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in betaVerticalDecisionVariables:
                    varName = betaVerticalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                else:
                    varName = LpVariable('e12' + str(i) + str(k) + str(j) ,lowBound = 0.1)
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                
            for j, e in enumerate(lhs0):
                if e in restDecisionVariables:
                    pass      
                elif e in alphaHorizontalDecisionVariables:
                    varName = alphaHorizontalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in alphaVerticalDecisionVariables:
                    varName = alphaVerticalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in betaHorizontalDecisionVariables:
                    varName = betaHorizontalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in betaVerticalDecisionVariables:
                    varName = betaVerticalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                else:
                    varName = LpVariable('e21' + str(i) + str(k) + str(j) ,lowBound = 0.1) 
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                
            for j,e in enumerate(rhs0):
                if e in restDecisionVariables:
                    pass      
                elif e in alphaHorizontalDecisionVariables:
                    varName = alphaHorizontalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in alphaVerticalDecisionVariables:
                    varName = alphaVerticalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in betaHorizontalDecisionVariables:
                    varName = betaHorizontalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                elif e in betaVerticalDecisionVariables:
                    varName = betaVerticalDecisionVariables[e]
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
                else:
                    varName = LpVariable('e22' + str(i) + str(k) + str(j) ,lowBound = 0.1)
                    restDecisionVariables[e] = varName
                    #print(e.source().index(),e.target().index(),varName)
            '''  
            print("rhs0")
            [print(e.source().index(),e.target().index()) for e in rhs0]
            print("lhs0")
            [print(e.source().index(),e.target().index()) for e in lhs0]
            print("rhs1")
            [print(e.source().index(),e.target().index()) for e in rhs1]
            print("lhs1")
            [print(e.source().index(),e.target().index()) for e in lhs1] 
            '''
            if set(lhs1) == set(rhs1):
                #print("pass")
                pass
            else:
                model += lpSum([restDecisionVariables[e] for e in lhs1 ]) == lpSum([restDecisionVariables[e] for e in rhs1 ]), "equal flow on left/right face {} {}".format(i,k)
            if set(lhs0) == set(lhs1):
                #print("pass")
                pass
            else:
                model += lpSum([restDecisionVariables[e] for e in lhs0 ]) == lpSum([restDecisionVariables[e] for e in rhs0 ]), "equal flow on top/bottom face {} {}".format(i,k)


        model.solve()
        time = model.solutionTime
        
        return n, time


if __name__ == "__main__":
    for i in range(4,10):
        
       print("Iteration",i)
       n,time = LP(i)
       print(n, time)




