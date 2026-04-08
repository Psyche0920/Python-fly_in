from graph import Graph, Zone


def parse_metadata(meta) -> dict[str, str]:
    """
    把 metadata 字符串解析成字典
    输入：
    "[zone=restricted max_drones=2]"
    输出：
    {"zone": "restricted", "max_drones": "2"}
    """

    result: dict[str, str] = {}
    meta = meta.strip("[]")
    parts: list[str] = meta.split()  # 按空格把字符串切开，变成列表。
    for p in parts:
        k, v = p.split("=")
        result[k] = v
    return result


def parse_file(filename: str) -> tuple[int, Graph]:
    """
    Input: 整个地图文件

    Return: drone数量, 构建好的 graph
    """

    graph = Graph()
    nb_drones: int = 0

    with open(filename, "r", encoding="utf-8") as f:
        # what is utf-8??? and as f(打开文件，并把文件对象命名为 f)
        for line in f:
            line = line.strip()  # 去掉一行两边的空格、换行符 \n 等。

            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones"):
                nb_drones = int(line.split(":")[1])

            elif line.startswith("start_hub"):
                parts = line.split()
                # start_hub: start 0 0
                name, x, y = parts[1], int(parts[2]), int(parts[3])
                zone = Zone(name, x, y)
                graph.add_zone(zone)
                graph.start = name  # only a name str

            elif line.startswith("end_hub"):
                parts = line.split()
                name, x, y = parts[1], int(parts[2]), int(parts[3])
                zone = Zone(name, x, y, max_drones=999)
                # 999 where is described???
                # 为什么是 999
                # 这是简化写法，想表达：
                # 终点几乎可以无限容纳 drone
                # 因为 end zone 通常不应该像普通 zone 一样只允许 1 架。
                graph.add_zone(zone)
                graph.end = name

            elif line.startswith("hub"):
                parts = line.split()
                name, x, y = parts[1], int(parts[2]), int(parts[3])
                zone_type: str = "normal"
                max_drones: int = 1

                if "[" in line:
                    # 👉 如果这行里有 [，说明它带了 metadata。
                    # 例如：
                    # hub: a 1 0 [zone=restricted max_drones=2]
                    meta = line[line.index("[")]
                    # 从 [ 开始切到最后，把 metadata 那一段取出来。
                    md = parse_metadata(meta)
                    if "zone" in md:
                        zone_type = md["zone"]
                    if "max_drones" in md:
                        max_drones = int(md["max_drones"])

                zone = Zone(name, x, y, zone_type, max_drones)
                graph.add_zone(zone)

            elif line.startswith("connection"):
                # connection: start-a
                parts = line.split()
                z1, z2 = parts[1].split("-")
                graph.add_connection(z1, z2)
    return nb_drones, graph


# parse_file(filename) 做的事情是：

# 创建一个空 Graph

# 逐行读地图文件

# 跳过空行和注释

# 读到 nb_drones 就保存无人机数量

# 读到 start_hub / end_hub / hub 就创建 Zone

# 读到 connection 就添加连接

# 最后返回 (nb_drones, graph)

# [testmain]???
