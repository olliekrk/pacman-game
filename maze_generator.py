from random import randint


class MazeGenerator:
    SIZE = (28, 31)

    def __init__(self):
        self.maze_model = None

    @staticmethod
    def is_border(x, y):
        return x == 0 or y == 0 or x == MazeGenerator.SIZE[0] - 1 or y == MazeGenerator.SIZE[1] - 1

    @staticmethod
    def is_wall(x, y):
        cell = x % 2 == 1 and y % 2 == 1
        return MazeGenerator.is_border(x, y) or not cell

    @staticmethod
    def adjacent_points(v_graph):
        up_edge = v_graph[0], v_graph[1] - 1
        down_edge = v_graph[0], v_graph[1] + 1
        right_edge = v_graph[0] + 1, v_graph[1]
        left_edge = v_graph[0] - 1, v_graph[1]

        return [up_edge, down_edge, right_edge, left_edge]

    def adjacent_edges(self, v_graph):
        edges = self.adjacent_points(v_graph)
        return [e for e in edges if self.maze_model[e[1]][e[0]] == 1 and not self.is_border(e[0], e[1])]

    def adjacent_area(self, v_graph):
        area = {v_graph}
        to_be_checked = {v_graph}
        while to_be_checked:
            new_to_be_checked = set()
            for v in to_be_checked:
                adj = self.adjacent_points(v)
                for p in adj:
                    if p not in area and self.maze_model[p[1]][p[0]] == 0:
                        area.add(p)
                        new_to_be_checked.add(p)
            to_be_checked = new_to_be_checked
        return area

    def prepare_model(self):
        width = MazeGenerator.SIZE[0]
        height = MazeGenerator.SIZE[1]

        self.maze_model = [[(1 if MazeGenerator.is_wall(x, y) else 0) for x in range(width)] for y in range(height)]

        graph = [(i, j) for i in range(width) for j in range(height) if self.maze_model[j][i] == 0]

        # a'la Prim Algorithm
        initial_vertex = graph[randint(0, len(graph) - 1)]
        v_graph = {initial_vertex}
        v_edges = self.adjacent_edges(initial_vertex)

        print(self.adjacent_area(initial_vertex))

        while not len(v_graph) == len(graph):
            edge_i = randint(0, len(v_edges) - 1)
            edge = v_edges[edge_i]

            possible_vertices = [v for v in self.adjacent_points(edge) if v in graph and v not in v_graph]
            if possible_vertices:
                self.maze_model[edge[1]][edge[0]] = 0
                zero_area = self.adjacent_area(initial_vertex)
                v_graph = {v for v in zero_area if v in graph}
                v_edges = list({edge for v in v_graph for edge in self.adjacent_edges(v)})

    def print_model(self):
        for l in self.maze_model:
            print(l)
