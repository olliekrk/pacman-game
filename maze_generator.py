from random import randint, shuffle


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

    # a'la Prim Algorithm
    def prepare_prim_model(self):
        width = MazeGenerator.SIZE[0]
        height = MazeGenerator.SIZE[1]
        self.maze_model = [[(1 if MazeGenerator.is_wall(x, y) else 0) for x in range(width)] for y in range(height)]

        graph = [(i, j) for i in range(width) for j in range(height) if self.maze_model[j][i] == 0]

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

    CHECK_LIST = [(col, row) for col in range(28 - 2) for row in range(31 - 2)]
    shuffle(CHECK_LIST)

    def nine_nine_finder(self):
        for col, row in MazeGenerator.CHECK_LIST:
            ok = True
            nine_area = [(col + c, row + r) for c in range(3) for r in range(3)]
            for c, r in nine_area:
                if self.maze_model[r][c] == 1:
                    MazeGenerator.CHECK_LIST.remove((col, row))
                    ok = False
                    break

            if ok:
                MazeGenerator.CHECK_LIST.remove((col, row))
                return col + 1, row + 1

        return None

    def check_cell_wall_model(self, cell, origin_cell):
        # cell is out of board
        if not (0 < cell[0] < self.SIZE[0] - 1 and 0 < cell[1] < self.SIZE[1] - 1):
            return False

        # check if placing cell would block some path
        to_check = self.adjacent_points(cell)
        corner_checks = [
            (cell[0] - 1, cell[1] - 1),
            (cell[0] - 1, cell[1] + 1),
            (cell[0] + 1, cell[1] + 1),
            (cell[0] + 1, cell[1] - 1),
        ]
        to_check.extend(corner_checks)

        for point in to_check:
            if 0 <= point[0] < self.SIZE[0] and 0 <= point[1] < self.SIZE[1]:
                if point != origin_cell and self.maze_model[point[1]][point[0]] == 1:
                    return False

        # otherwise OK
        return True

    def prepare_wall_model(self):
        width = MazeGenerator.SIZE[0]
        height = MazeGenerator.SIZE[1]
        self.maze_model = [[(1 if MazeGenerator.is_border(x, y) else 0) for x in range(width)] for y in range(height)]

        build_cells = {(14, 15)}
        already_checked_cells = set()

        while len(build_cells):
            new_build_cells = set()
            for build_cell in build_cells:
                already_checked_cells.add(build_cell)
                self.maze_model[build_cell[1]][build_cell[0]] = 1
                adjacent_list = self.adjacent_points(build_cell)
                available_cells = [cell for cell in adjacent_list if self.check_cell_wall_model(cell, build_cell)]

                shuffle(available_cells)

                for adj_cell in available_cells:
                    if adj_cell not in already_checked_cells:
                        new_build_cells.add(adj_cell)
                        self.maze_model[adj_cell[1]][adj_cell[0]] = 1

                if not available_cells:
                    # find 9x9 empty place
                    n = self.nine_nine_finder()
                    if n:
                        new_build_cells.add(n)

            build_cells = new_build_cells

    def print_model(self):
        for l in self.maze_model:
            print(l)


if __name__ == "__main__":
    m = MazeGenerator()
    m.prepare_wall_model()
    m.print_model()
