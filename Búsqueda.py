import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq
import random
import string
import time

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def distancia_linea_recta(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

class AStarDualHeuristicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("A* con Manhattan vs Distancia en Línea Recta (con animación)")
        self.root.geometry("1200x800")

        self.graph = nx.Graph()
        self.positions = {}

        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 6))
        self.canvas_tk = None

        self.setup_ui()

    def setup_ui(self):
        # Contenedor principal con scroll
        self.main_canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame dentro del canvas
        self.container_frame = tk.Frame(self.main_canvas)
        self.main_canvas.create_window((0, 0), window=self.container_frame, anchor="nw")

        # Contenido dentro del container_frame
        frame_input = tk.Frame(self.container_frame)
        frame_input.pack(padx=10, pady=10)

        tk.Label(frame_input, text="Nodos y coordenadas (ej: A,0,0)").grid(row=0, column=0, sticky='w')
        self.entry_nodes = tk.Text(frame_input, width=40, height=5)
        self.entry_nodes.grid(row=1, column=0, padx=5, pady=5)

        tk.Label(frame_input, text="Aristas (ej: A,B o A,B,5)").grid(row=0, column=1, sticky='w')
        self.entry_edges = tk.Text(frame_input, width=40, height=5)
        self.entry_edges.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_input, text="Inicio").grid(row=2, column=0)
        self.entry_start = tk.Entry(frame_input)
        self.entry_start.grid(row=3, column=0, pady=5)

        tk.Label(frame_input, text="Objetivo").grid(row=2, column=1)
        self.entry_goal = tk.Entry(frame_input)
        self.entry_goal.grid(row=3, column=1, pady=5)

        btn = tk.Button(frame_input, text="Ejecutar", command=self.run_algorithms)
        btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Leyenda
        legend_frame = tk.Frame(frame_input)
        legend_frame.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Label(legend_frame, text="Leyenda:").pack(side=tk.TOP)
        color_labels = [
            ("Verde", "Nodo visitado con heurística Manhattan"),
            ("Azul", "Nodo visitado con heurística de línea recta"),
            ("Gris claro", "Nodo no visitado aún")
        ]
        color_map = {"verde": "green", "azul": "blue", "gris claro": "lightgray"}
        for color, desc in color_labels:
            item = tk.Frame(legend_frame)
            item.pack(side=tk.LEFT, padx=15)
            c = tk.Canvas(item, width=15, height=15)
            c.create_oval(2, 2, 13, 13, fill=color_map[color.lower()])
            c.pack(side=tk.LEFT)
            tk.Label(item, text=desc).pack(side=tk.LEFT, padx=5)

        self.frame_canvas = tk.Frame(self.container_frame)
        self.frame_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.text_comparacion = tk.Text(self.container_frame, height=6, bg="#f0f0f0")
        self.text_comparacion.pack(fill=tk.X, padx=10, pady=5)
        self.text_comparacion.config(state='disabled')  # Lo dejamos inicialmente deshabilitado

        # Actualizar scrollregion cuando cambie tamaño container_frame
        self.container_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))

    def run_algorithms(self):
        self.graph.clear()
        self.positions.clear()

        try:
            nodes_input = self.entry_nodes.get("1.0", tk.END).strip()
            edges_input = self.entry_edges.get("1.0", tk.END).strip()
            start_input = self.entry_start.get().strip()
            goal_input = self.entry_goal.get().strip()

            if not nodes_input:
                num_nodes = random.randint(5, 10)
                node_names = random.sample(string.ascii_uppercase, num_nodes)
                for name in node_names:
                    x, y = random.randint(0, 20), random.randint(0, 20)
                    self.graph.add_node(name)
                    self.positions[name] = (x, y)
            else:
                for line in nodes_input.splitlines():
                    name, x, y = line.strip().split(',')
                    self.graph.add_node(name)
                    self.positions[name] = (int(x), int(y))

            if not edges_input:
                nodes = list(self.graph.nodes)
                for i in range(len(nodes)):
                    for j in range(i + 1, len(nodes)):
                        if random.random() < 0.4:
                            weight = random.randint(2, 20)
                            self.graph.add_edge(nodes[i], nodes[j], weight=weight)
                for i in range(len(nodes) - 1):
                    if not self.graph.has_edge(nodes[i], nodes[i + 1]):
                        self.graph.add_edge(nodes[i], nodes[i + 1], weight=random.randint(2, 20))
            else:
                for line in edges_input.splitlines():
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        a, b = parts
                        weight = random.randint(2, 20)
                    elif len(parts) == 3:
                        a, b, weight = parts
                        weight = float(weight)
                    else:
                        raise ValueError(f"Formato inválido en la arista: {line}")
                    self.graph.add_edge(a, b, weight=weight)

            if not start_input or not goal_input:
                nodes = list(self.graph.nodes)
                self.start, self.goal = random.sample(nodes, 2)
                self.entry_start.delete(0, tk.END)
                self.entry_start.insert(0, self.start)
                self.entry_goal.delete(0, tk.END)
                self.entry_goal.insert(0, self.goal)
            else:
                self.start = start_input
                self.goal = goal_input

            if self.start not in self.graph.nodes or self.goal not in self.graph.nodes:
                raise ValueError("Nodos inválidos")

            t0 = time.perf_counter()
            self.steps_manhattan = self.a_star_steps(self.start, self.goal, manhattan)
            t1 = time.perf_counter()
            self.time_manhattan = (t1 - t0) * 1000

            t0 = time.perf_counter()
            self.steps_linea_recta = self.a_star_steps(self.start, self.goal, distancia_linea_recta)
            t1 = time.perf_counter()
            self.time_linea_recta = (t1 - t0) * 1000

            self.step_index = 0
            self.animate()
            self.mostrar_comparacion()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def a_star_steps(self, start, goal, heuristic_fn):
        open_set = [(0, start)]
        came_from = {}
        g_score = {n: float('inf') for n in self.graph.nodes}
        g_score[start] = 0
        steps = []
        visited = set()

        while open_set:
            _, current = heapq.heappop(open_set)
            if current in visited:
                continue
            visited.add(current)
            steps.append({'current': current, 'visited': set(visited), 'path': self.reconstruct_path(came_from, current) if current == goal else []})
            if current == goal:
                break
            for neighbor in self.graph.neighbors(current):
                weight = self.graph[current][neighbor].get('weight', 1)
                tentative_g = g_score[current] + weight
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic_fn(self.positions[neighbor], self.positions[goal])
                    heapq.heappush(open_set, (f, neighbor))
        return steps

    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(current)
        return path[::-1]

    def animate(self):
        self.ax1.clear(); self.ax2.clear()
        if self.step_index < len(self.steps_manhattan):
            s = self.steps_manhattan[self.step_index]
            cols = ['green' if n in s['visited'] else 'lightgray' for n in self.graph.nodes]
            nx.draw(self.graph, pos=self.positions, ax=self.ax1, node_color=cols, with_labels=True)
            if s['path']:
                nx.draw_networkx_edges(self.graph, pos=self.positions, edgelist=list(zip(s['path'][:-1], s['path'][1:])), edge_color='green', width=3, ax=self.ax1)
            self.ax1.set_title("Manhattan")
        else:
            s = self.steps_manhattan[-1]
            cols = ['green' if n in s['visited'] else 'lightgray' for n in self.graph.nodes]
            nx.draw(self.graph, pos=self.positions, ax=self.ax1, node_color=cols, with_labels=True)
            if s['path']:
                nx.draw_networkx_edges(self.graph, pos=self.positions, edgelist=list(zip(s['path'][:-1], s['path'][1:])), edge_color='green', width=3, ax=self.ax1)
            self.ax1.set_title("Manhattan (Finalizado)")
        if self.step_index < len(self.steps_linea_recta):
            s = self.steps_linea_recta[self.step_index]
            cols = ['blue' if n in s['visited'] else 'lightgray' for n in self.graph.nodes]
            nx.draw(self.graph, pos=self.positions, ax=self.ax2, node_color=cols, with_labels=True)
            if s['path']:
                nx.draw_networkx_edges(self.graph, pos=self.positions, edgelist=list(zip(s['path'][:-1], s['path'][1:])), edge_color='blue', width=3, ax=self.ax2)
            self.ax2.set_title("Distancia Línea Recta")
        else:
            s = self.steps_linea_recta[-1]
            cols = ['blue' if n in s['visited'] else 'lightgray' for n in self.graph.nodes]
            nx.draw(self.graph, pos=self.positions, ax=self.ax2, node_color=cols, with_labels=True)
            if s['path']:
                nx.draw_networkx_edges(self.graph, pos=self.positions, edgelist=list(zip(s['path'][:-1], s['path'][1:])), edge_color='blue', width=3, ax=self.ax2)
            self.ax2.set_title("Distancia Línea Recta (Finalizado)")

        if not self.canvas_tk:
            self.canvas_tk = FigureCanvasTkAgg(self.fig, master=self.frame_canvas)
            self.canvas_tk.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas_tk.draw()
        self.step_index += 1
        if self.step_index < max(len(self.steps_manhattan), len(self.steps_linea_recta)):
            self.root.after(500, self.animate)

    def mostrar_comparacion(self):
        texto = (f"Tiempo de ejecución con heurística Manhattan: {self.time_manhattan:.2f} ms\n"
                 f"Tiempo de ejecución con heurística Línea Recta: {self.time_linea_recta:.2f} ms\n\n"
                 f"Número de nodos visitados con Manhattan: {len(self.steps_manhattan[-1]['visited'])}\n"
                 f"Número de nodos visitados con Línea Recta: {len(self.steps_linea_recta[-1]['visited'])}")
        self.text_comparacion.config(state='normal')
        self.text_comparacion.delete("1.0", tk.END)
        self.text_comparacion.insert(tk.END, texto)
        self.text_comparacion.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = AStarDualHeuristicApp(root)
    root.mainloop()
