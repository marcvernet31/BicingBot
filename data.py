import os
import string
import pandas as pd
import networkx as nx

from haversine import haversine
from geopy.geocoders import Nominatim
from staticmap import *


# Returns the dataframe containing the number of bikes on each station
def getBikes():
    url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
    bikes = pd.DataFrame.from_records(pd.read_json(url_status)['data']['stations'], index='station_id')
    bikes = bikes[['num_bikes_available', 'num_docks_available']]
    return bikes


# Returns the dataframe containing the stations' position
def getStations():
    url_info = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    stations = pd.DataFrame.from_records(pd.read_json(url_info)['data']['stations'], index='station_id')
    stations = stations[['address', 'lat', 'lon']]
    return stations


# Given (lon, lat), returns (lat, lon)
def swap(coords):
    return coords[::-1]


# Returns (lon, lat) of a given station
def getCoords(id):
    lon = stations.loc[id, "lon"]
    lat = stations.loc[id, "lat"]
    return (lon, lat)


# Returns the distance between 2 stations (in meters)
def distance(origen, desti):
    coordA = swap(getCoords(origen))
    coordB = swap(getCoords(desti))
    return haversine(coordA, coordB, unit='m')


# Returns the walking time between 2 points (in seconds)
def walkTime(coordsA, coordsB):
    speed = 4*1000/3600
    distance = haversine(coordsA, coordsB, unit='m')
    return distance / speed


# Given two addresses in a string, it returns its' coordinates
def addressesTOcoordinates(addresses):
    try:
        geolocator = Nominatim(user_agent="stations_bot")
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except:
        return None


# Draws a path (given as a list of nodes) in a map
def drawPath(path, coordsST, photoName):
    mida = 1500
    diameter = mida // 180
    thickness = mida // 300
    m = StaticMap(mida, mida)
    n = len(path)

    # Plotting vertices:
    m.add_marker(CircleMarker(swap(coordsST[0]), 'black', diameter*2))
    m.add_marker(CircleMarker(swap(coordsST[0]), 'white', diameter))

    m.add_marker(CircleMarker(swap(coordsST[1]), 'black', diameter*2))
    m.add_marker(CircleMarker(swap(coordsST[1]), 'white', diameter))

    for id in path[1:-1]:
        coords = getCoords(id)
        marker = CircleMarker(coords, 'black', diameter)
        m.add_marker(marker)

    if n == 2:
        m.add_line(Line((swap(coordsST[0]), swap(coordsST[1])), 'red', thickness))
    else:
        m.add_line(Line((swap(coordsST[0]), getCoords(path[1])), 'red', thickness))
        for i in range(2, n-1):
            coordsA = getCoords(path[i-1])
            coordsB = getCoords(path[i])
            m.add_line(Line(((coordsA), (coordsB)), 'blue', thickness))
        m.add_line(Line((swap(coordsST[1]), getCoords(path[-2])), 'red', thickness))
    image = m.render()
    image.save(photoName)


# Calculates the shortest path between 2 given addresses
def shortestPath(G, addresses, photoName):
    coordsST = addressesTOcoordinates(addresses)
    if coordsST is None:
        return None
    G.add_nodes_from(('source', 'target'))

    for id in station_ids:
        idCoords = swap(getCoords(id))
        G.add_edge('source', id, weight=walkTime(coordsST[0], idCoords))
        G.add_edge('target', id, weight=walkTime(coordsST[1], idCoords))

    weightST = walkTime(coordsST[0], coordsST[1])
    G.add_edge('source', 'target', weight=weightST)

    p = nx.dijkstra_path(G, 'source', 'target', 'weight')
    drawPath(p, coordsST, photoName)

    G.remove_nodes_from(('source', 'target'))
    return p


# Returns the bounding box of all points
def boundingBox():
    LatX, Lat_, Lon_, LonX = 0, 999, 999, 0
    for element in station_ids:
        lon, lat = getCoords(element)
        if lon < Lon_:
            Lon_ = lon
        elif lon > LonX:
            LonX = lon
        if lat > LatX:
            LatX = lat
        elif lat < Lat_:
            Lat_ = lat
    return LatX, Lat_, Lon_, LonX


# Creates a matrix containing the stations by quadrant
def stations_matrix(dist):
    d = dist/1000
    punts = dict()  # Map of points with its location in the matrix

    d = d / 111  # Conversion to degrees
    LatX, Lat_, Lon_, LonX = boundingBox()
    w = int((LonX-Lon_)//d)
    h = int((LatX-Lat_)//d)

    Matrix = [[[] for x in range(w)] for y in range(h)]

    for element in station_ids:
        lon, lat = getCoords(element)
        fila = int((lat - Lat_) // d)
        columna = int((lon - Lon_) // d)
        if(fila >= h):
            fila -= 1
        if(columna >= w):
            columna -= 1
        Matrix[h-1-fila][columna].append(element)
        punts[element] = [h-1-fila, columna, 0]

    return Matrix, punts


# Adds eges to the graph G if they are at distance <= max_dist
def puntsConnexes(G, origen, punts, max_dist, directed):
    speed = 10*1000/3600
    for desti in punts:
        dist = distance(origen, desti)
        if(dist <= max_dist):
            if(not directed):
                G.add_edge(origen, desti, weight=dist/speed)
            else:
                G.add_edge(origen, desti, weight=dist)
                G.add_edge(desti, origen, weight=dist)


# Given the matrix that 'classifies' the stations, it builds the graph
def grafFromMatrix(G, Matrix, points, dist, dir):
    for id in station_ids:
        G.add_node(id)
    for key in points:
        f = points[key][0]
        c = points[key][1]
        h = len(Matrix)
        w = len(Matrix[0])

        if points[key][2] != 1:
            puntsConnexes(G, key, Matrix[f][c], dist, dir)
            if f+1 < h:
                puntsConnexes(G, key, Matrix[f+1][c], dist, dir)
            if f-1 >= 0:
                puntsConnexes(G, key, Matrix[f-1][c], dist, dir)
            if c-1 >= 0:
                puntsConnexes(G, key, Matrix[f][c-1], dist, dir)
            if c+1 < w:
                puntsConnexes(G, key, Matrix[f][c+1], dist, dir)
            if f+1 < h and c-1 >= 0:
                puntsConnexes(G, key, Matrix[f+1][c-1], dist, dir)
            if f+1 < h and c+1 < w:
                puntsConnexes(G, key, Matrix[f+1][c+1], dist, dir)
            if f-1 >= 0 and c-1 >= 0:
                puntsConnexes(G, key, Matrix[f-1][c-1], dist, dir)
            if f-1 >= 0 and c+1 < w:
                puntsConnexes(G, key, Matrix[f-1][c+1], dist, dir)
            points[key][2] = 1


# Builds the graph using the quadratic algorithm (only used for short distances)
def grafQuadratic(G, max_dist, directed):
    visitat = dict()
    speed = 10*1000/3600
    for id in station_ids:
        G.add_node(id)
        visitat.update({id: False})
    for origen in station_ids:
        visitat[origen] = True
        for desti in station_ids:
            if (not visitat[desti]):
                dist = distance(origen, desti)
                if (dist <= max_dist):
                    if(not directed):
                        G.add_edge(origen, desti, weight=dist/speed)
                    else:
                        G.add_edge(origen, desti, weight=dist)
                        G.add_edge(desti, origen, weight=dist)


# Builds the graph on linear time
def grafLinial(G, max_dist, directed):
    if max_dist >= 5:
        Matrix, points = stations_matrix(max_dist)
        grafFromMatrix(G, Matrix, points, max_dist, directed)


# Creates the graph using some algorithm, dependind on max_dist
def creaGraf(max_dist, directed):
    if(not directed):
        G = nx.Graph()
    else:
        G = nx.DiGraph()

    if max_dist >= 50:
        grafLinial(G, max_dist, directed)
    else:
        grafQuadratic(G, max_dist, directed)

    return G


# Draws the whole graph in a map
def dibuixaMapa(G, photoName):
    mida = 1500
    diametre = int(mida // 180)
    m = StaticMap(mida, mida)

    # Adding nodes to the map:
    nodes = list(G.nodes)
    for node in nodes:
        coords = getCoords(node)
        m.add_marker(CircleMarker(coords, 'black', diametre*2))
        m.add_marker(CircleMarker(coords, 'white', diametre))

    edges = list(G.edges.data())
    gruix = int(mida // 300)

    # Adding edges to the map:
    for edge in edges:
        origen = edge[0]
        desti = edge[1]

        coorA = getCoords(origen)
        coorB = getCoords(desti)
        m.add_line(Line(((coorA), (coorB)), 'blue', gruix))

    image = m.render()
    image.save(photoName)


# Calculates the bikes that must be transfered to ensure
# requiredBikes and requiredDocks at every station
def flows(radius, requiredBikes, requiredDocks):
    stations = getStations()
    bikes = getBikes()

    nbikes = 'num_bikes_available'
    ndocks = 'num_docks_available'

    G = creaGraf(radius, True)
    G.add_node('TOP')  # The green node
    demand = 0

    # Iterate on every station
    for st in bikes.itertuples():
        idx = st.Index  # Station ID
        if idx not in stations.index: continue
        stridx = str(idx)

        # The blue (s), black and red (t) nodes of the graph
        s_idx, g_idx, t_idx = 's'+stridx, idx, 't'+stridx
        G.add_node(s_idx)
        G.add_node(t_idx)

        b, d = st.num_bikes_available, st.num_docks_available
        req_bikes = max(0, requiredBikes - b)  # Required bikes in a certain station
        req_docks = max(0, requiredDocks - d)  # Required docks in a certain station

        cap_bikes = max(0, b - requiredBikes)  # Bikes that can be recieved
        cap_docks = max(0, d - requiredDocks)  # Bicis that can be given

        G.add_edge('TOP', s_idx)
        G.add_edge(t_idx, 'TOP')
        G.add_edge(s_idx, g_idx, capacity=cap_bikes)
        G.add_edge(g_idx, t_idx, capacity=cap_docks)

        if req_bikes > 0:
            demand += req_bikes
            G.nodes[t_idx]['demand'] = req_bikes
        elif req_docks > 0:
            demand -= req_docks
            G.nodes[s_idx]['demand'] = -req_docks

    G.nodes['TOP']['demand'] = -demand  # The sum of the demands must be zero

    err = False

    try:
        flowCost, flowDict = nx.network_simplex(G)

    except nx.NetworkXUnfeasible:
        err = True
        return "No solution could be found!", "Try again later"

    except:
        err = True
        return "Something bad happened!", "Try again later"

    if not err:

        cost = "The total cost of transferring bikes is " + str(flowCost/1000) + "km."
        max_edge = "Done!"  # If no bikes have to be moved, this will be the 2nd message

        # We update the status of the stations according to the calculated transportation of bicycles
        for src in flowDict:

            if isinstance(src, int) or src == 'TOP': continue
            idx_src = int(src[1:])
            for idx_dst, b in flowDict[src].items():
                if isinstance(idx_dst, int) and b > 0:
                    max_edge = str(idx_src) + " -> " + str(idx_dst) + "  Cost: " + str(b*G.edges[src, idx_dst]['weight'])
                    return cost, max_edge

        return cost, max_edge


def connectedComponents(G):
    return nx.number_connected_components(G)


def nodesGraph(G):
    return G.number_of_nodes()


def edgesGraph(G):
    return G.number_of_edges()


stations = getStations()
station_ids = stations.index.tolist()
