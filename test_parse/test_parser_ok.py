from parser import parse_file

nb_drones, graph = parse_file("ok_map.txt")

print("nb_drones =", nb_drones)
print("start =", graph.start)
print("end =", graph.end)
print("zones =", list(graph.zones.keys()))
print("adj =", graph.adj)
print("links =", graph.links)
print("a max_drones =", graph.zones["a"].max_drones)
print("start-a capacity =", graph.get_link_capacity("start", "a"))
